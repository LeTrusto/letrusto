from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models.entities import InventoryReservation, Order
from app.schemas.reconciliation import ReconciliationIssueDTO, ReconciliationResultDTO
from app.services.cashfree_service import CashfreeService
from app.services.fulfillment_service import FulfillmentService
from app.services.inventory_reservation_service import InventoryReservationService


class OrderLifecycleReconciliationService:
    """Scheduler-ready, independently callable order lifecycle jobs."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def expire_reservations(self) -> int:
        expired = InventoryReservationService(self.db).release_expired()
        self.db.commit()
        return expired

    async def reconcile_pending_payments(self, failures: list[str], provider_unavailable: list[str]) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=self.settings.PENDING_PAYMENT_RECONCILIATION_AGE_MINUTES)
        orders = list(self.db.scalars(
            select(Order).where(
                Order.status == "PENDING_PAYMENT",
                Order.payment_status == "PENDING",
                Order.provider_order_id.is_not(None),
                Order.created_at <= cutoff,
            ).options(selectinload(Order.user)).order_by(Order.created_at.asc()).limit(self.settings.RECONCILIATION_BATCH_SIZE)
        ).all())
        reconciled = 0
        service = CashfreeService(self.db)
        for order in orders:
            try:
                result = await service.reconcile_order_payment(order.id)
                state = result.get("state")
                if state == "PROVIDER_UNAVAILABLE":
                    provider_unavailable.append(f"payment:{order.order_number}")
                elif state in {"SUCCESS", "FAILED", "USER_DROPPED", "CANCELLED", "VOID"}:
                    reconciled += 1
                elif state not in {"PENDING", "SKIPPED"}:
                    failures.append(f"payment:{order.order_number}:{result.get('failure') or state}")
            except Exception as exc:
                self.db.rollback()
                failures.append(f"payment:{order.order_number}:{str(exc)[:300]}")
        return reconciled

    async def reconcile_fulfillment(self, failures: list[str], provider_unavailable: list[str]) -> int:
        if not self.settings.CJ_API_KEY:
            provider_unavailable.append("fulfillment:CJ_API_KEY_not_configured")
            return 0
        orders = list(self.db.scalars(
            select(Order).where(
                Order.payment_status == "PAID",
                Order.supplier_order_id.is_(None),
                Order.fulfillment_status.in_({"PENDING", "FAILED"}),
            ).order_by(Order.created_at.asc()).limit(self.settings.RECONCILIATION_BATCH_SIZE)
        ).all())
        submitted = 0
        service = FulfillmentService(self.db)
        for order in orders:
            try:
                if not InventoryReservationService(self.db).fulfillment_safe(order.id):
                    failures.append(f"fulfillment:{order.order_number}:reservation_not_consumed")
                    continue
                result = await service.submit(order.id)
                if result.supplier_order_id:
                    submitted += 1
            except Exception as exc:
                self.db.rollback()
                failures.append(f"fulfillment:{order.order_number}:{str(exc)[:300]}")
        return submitted

    async def sync_tracking(self, failures: list[str], provider_unavailable: list[str]) -> int:
        if not self.settings.CJ_API_KEY:
            provider_unavailable.append("tracking:CJ_API_KEY_not_configured")
            return 0
        try:
            orders = await FulfillmentService(self.db).sync_pending_fulfillments()
            return len(orders)
        except Exception as exc:
            self.db.rollback()
            failures.append(f"tracking:{str(exc)[:300]}")
            return 0

    def detect_inconsistencies(self) -> list[ReconciliationIssueDTO]:
        orders = list(self.db.scalars(select(Order).order_by(Order.created_at.asc()).limit(self.settings.RECONCILIATION_BATCH_SIZE)).all())
        issues: list[ReconciliationIssueDTO] = []
        for order in orders:
            def add(code: str, detail: str) -> None:
                issues.append(ReconciliationIssueDTO(order_id=order.id, order_number=order.order_number, code=code, detail=detail))

            if order.status == "PAID" and order.payment_status != "PAID":
                add("ORDER_PAID_PAYMENT_MISMATCH", "Order status is PAID but payment status is not PAID")
            if order.payment_status == "PAID" and order.status not in {"PAID", "CANCELLED", "REFUNDED"}:
                add("PAYMENT_PAID_ORDER_MISMATCH", "Payment is PAID but order status is not payment-compatible")
            if order.status == "REFUNDED" and order.payment_status != "REFUNDED":
                add("REFUNDED_PAYMENT_MISMATCH", "Order is REFUNDED without a matching payment state")
            if order.fulfillment_status in {"SUBMITTING", "SUBMITTED", "PROCESSING", "SHIPPED", "DELIVERED"} and order.payment_status != "PAID":
                add("UNPAID_FULFILLMENT", "Fulfillment progressed without a PAID payment")
            reservations = list(self.db.scalars(select(InventoryReservation).where(InventoryReservation.order_id == order.id)).all())
            if any(row.status == "ACTIVE" and order.status in {"CANCELLED", "REFUNDED"} for row in reservations):
                add("ACTIVE_TERMINAL_RESERVATION", "Terminal order still has an ACTIVE reservation")
            if reservations and order.payment_status == "PAID" and order.fulfillment_status in {"SUBMITTING", "SUBMITTED", "PROCESSING", "SHIPPED", "DELIVERED"} and not all(row.status == "CONSUMED" for row in reservations):
                add("FULFILLMENT_RESERVATION_MISMATCH", "Fulfillment progressed while reservation was not fully consumed")
        duplicates = self.db.execute(
            select(InventoryReservation.order_item_id).where(InventoryReservation.status == "ACTIVE").group_by(InventoryReservation.order_item_id).having(func.count(InventoryReservation.id) > 1)
        ).all()
        for (order_item_id,) in duplicates:
            order = self.db.scalar(select(Order).join(InventoryReservation, InventoryReservation.order_id == Order.id).where(InventoryReservation.order_item_id == order_item_id))
            if order:
                add_issue = ReconciliationIssueDTO(order_id=order.id, order_number=order.order_number, code="MULTIPLE_ACTIVE_RESERVATIONS", detail=f"Order item {order_item_id} has multiple ACTIVE reservations")
                issues.append(add_issue)
        return issues

    async def run_order_lifecycle_reconciliation(self) -> ReconciliationResultDTO:
        started = datetime.now(timezone.utc)
        failures: list[str] = []
        provider_unavailable: list[str] = []
        reservations_expired = payments_reconciled = fulfillment_submitted = tracking_synced = 0
        try:
            reservations_expired = self.expire_reservations()
        except Exception as exc:
            self.db.rollback()
            failures.append(f"reservations:{str(exc)[:300]}")
        try:
            payments_reconciled = await self.reconcile_pending_payments(failures, provider_unavailable)
        except Exception as exc:
            self.db.rollback()
            failures.append(f"payments:{str(exc)[:300]}")
        try:
            fulfillment_submitted = await self.reconcile_fulfillment(failures, provider_unavailable)
        except Exception as exc:
            self.db.rollback()
            failures.append(f"fulfillment:{str(exc)[:300]}")
        try:
            tracking_synced = await self.sync_tracking(failures, provider_unavailable)
        except Exception as exc:
            self.db.rollback()
            failures.append(f"tracking:{str(exc)[:300]}")
        try:
            inconsistencies = self.detect_inconsistencies()
        except Exception as exc:
            self.db.rollback()
            failures.append(f"consistency:{str(exc)[:300]}")
            inconsistencies = []
        return ReconciliationResultDTO(
            started_at=started,
            completed_at=datetime.now(timezone.utc),
            reservations_expired=reservations_expired,
            payments_reconciled=payments_reconciled,
            fulfillment_submitted=fulfillment_submitted,
            tracking_synced=tracking_synced,
            inconsistencies_found=len(inconsistencies),
            failures=failures,
            provider_unavailable=provider_unavailable,
            inconsistencies=inconsistencies,
        )
