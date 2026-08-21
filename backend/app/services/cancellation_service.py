"""Order cancellation and refund lifecycle service."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.entities import Order, PaymentAttempt, RefundRequest, User
from app.services.inventory_reservation_service import InventoryReservationService

# States that block CJ fulfillment
UNFULFILLABLE_STATUSES = frozenset({"CANCELLED", "REFUND_PENDING", "REFUNDED"})

# Payment statuses that require refund when cancelling
PAID_STATUSES = frozenset({"PAID"})


class CancellationService:
    def __init__(self, db: Session, settings: Settings | None = None, cashfree_service=None, razorpay_service=None) -> None:
        self.db = db
        self.settings = settings or get_settings()
        if cashfree_service is None:
            from app.services.cashfree_service import CashfreeService

            cashfree_service = CashfreeService(db, self.settings)
        self.cashfree_service = cashfree_service
        if razorpay_service is None:
            from app.services.razorpay_service import RazorpayService

            razorpay_service = RazorpayService(db, self.settings)
        self.razorpay_service = razorpay_service

    def _get_order_for_user(self, user: User, order_id: UUID) -> Order:
        order = self.db.scalar(select(Order).where(Order.id == order_id, Order.user_id == user.id).with_for_update())
        if order is None:
            raise NotFoundError("Order not found")
        return order

    def _get_order(self, order_id: UUID) -> Order:
        order = self.db.scalar(select(Order).where(Order.id == order_id).with_for_update())
        if order is None:
            raise NotFoundError("Order not found")
        return order

    def _check_cancellable(self, order: Order) -> str | None:
        """Return rejection reason, or None if cancellable."""
        if order.status == "REFUNDED":
            return "Order is already refunded"
        if order.status == "CANCELLED" and order.payment_status == "REFUND_PENDING":
            return None  # Allow re-entry for idempotency
        if order.status == "CANCELLED":
            return None  # Idempotent
        if order.payment_status == "REFUND_PENDING":
            return None  # Idempotent
        if order.supplier_order_id:
            return "Order has been submitted to supplier and cannot be cancelled"
        if order.fulfillment_status in {"SUBMITTED", "SUBMITTING", "PROCESSING", "SHIPPED", "DELIVERED"}:
            return "Order fulfillment has progressed and cannot be cancelled"
        return None

    def _existing_refund(self, order: Order) -> RefundRequest | None:
        return self.db.scalar(
            select(RefundRequest).where(RefundRequest.order_id == order.id, RefundRequest.status.not_in({"FAILED"}))
        )

    def cancel_by_customer(self, user: User, order_id: UUID, reason: str = "Customer requested cancellation") -> Order:
        order = self._get_order_for_user(user, order_id)
        rejection = self._check_cancellable(order)
        if rejection:
            raise BadRequestError(rejection)

        # Idempotent: already cancelled
        if order.status == "CANCELLED":
            return order

        if order.payment_status in PAID_STATUSES:
            self._initiate_refund(order, reason=reason, requested_by="customer")
        else:
            order.status = "CANCELLED"
            order.payment_status = "CANCELLED"
        InventoryReservationService(self.db).release_for_order(order.id)

        order.cancelled_at = datetime.now(timezone.utc)
        order.cancellation_reason = reason
        order.cancelled_by = "customer"
        self.db.commit()
        return order

    def cancel_by_admin(self, admin: User, order_id: UUID, reason: str = "Admin cancellation") -> Order:
        order = self._get_order(order_id)
        rejection = self._check_cancellable(order)
        if rejection:
            raise BadRequestError(rejection)

        if order.payment_status in PAID_STATUSES:
            self._initiate_refund(order, reason=reason, requested_by="admin", admin_id=admin.id)
        else:
            order.status = "CANCELLED"
            order.payment_status = "CANCELLED"
        InventoryReservationService(self.db).release_for_order(order.id)

        order.cancelled_at = datetime.now(timezone.utc)
        order.cancellation_reason = reason
        order.cancelled_by = f"admin:{admin.id}"
        self.db.commit()
        return order

    def _initiate_refund(self, order: Order, *, reason: str, requested_by: str, admin_id: UUID | None = None) -> RefundRequest:
        if order.payment_provider not in {"CASHFREE", "RAZORPAY"}:
            raise BadRequestError("Order payment provider is missing or unsupported for refunds")
        existing = self._existing_refund(order)
        if existing:
            return existing

        idempotency_key = f"refund-{order.id}"
        # Check unique constraint won't be violated
        dup = self.db.scalar(select(RefundRequest).where(RefundRequest.idempotency_key == idempotency_key))
        if dup:
            return dup

        provider_order_id = order.provider_order_id or order.order_number
        refund = RefundRequest(
            order=order,
            provider=order.payment_provider,
            provider_order_id=provider_order_id,
            amount=order.total,
            currency=order.currency,
            status="PENDING",
            reason=reason,
            idempotency_key=idempotency_key,
            requested_by=requested_by,
            admin_id=admin_id,
        )

        # Link payment attempt if available
        attempt = self.db.scalar(select(PaymentAttempt).where(
            PaymentAttempt.order_id == order.id,
            PaymentAttempt.provider == order.payment_provider,
            PaymentAttempt.status.in_({"SUCCESS", "CAPTURED"}),
        ))
        if attempt:
            refund.payment_attempt_id = attempt.id

        order.status = "CANCELLED"
        order.payment_status = "REFUND_PENDING"
        self.db.add(refund)
        self.db.flush()

        # Attempt provider refund call
        self._request_provider_refund(refund)
        return refund

    def _request_provider_refund(self, refund: RefundRequest) -> None:
        if refund.provider == "CASHFREE":
            response = self.cashfree_service.request_refund(
                provider_order_id=refund.provider_order_id,
                refund_amount=refund.amount,
                idempotency_key=refund.idempotency_key,
                reason=refund.reason or "Customer cancellation",
            )
        elif refund.provider == "RAZORPAY":
            payment_id = refund.payment_attempt.provider_payment_id if refund.payment_attempt else None
            response = self.razorpay_service.request_refund(
                payment_id=payment_id or "",
                refund_amount=refund.amount,
                reason=refund.reason or "Customer cancellation",
            )
        else:
            response = {"provider_status": "FAILED", "failure_reason": "Unsupported refund provider"}
        refund.provider_refund_id = response.get("provider_refund_id")
        refund.status = self._map_refund_status(response.get("provider_status"))
        if response.get("failure_reason"):
            refund.failure_reason = response["failure_reason"]
        if refund.status == "FAILED":
            refund.failed_at = datetime.now(timezone.utc)
            refund.order.payment_status = "REFUND_FAILED"
        elif refund.status == "SUCCESS":
            self._mark_refunded(refund)

    @staticmethod
    def _map_refund_status(provider_status: str | None) -> str:
        mapping = {
            "SUCCESS": "SUCCESS",
            "PENDING": "PROCESSING",
            "CANCELLED": "FAILED",
            "FAILED": "FAILED",
            "ONHOLD": "PROCESSING",
        }
        return mapping.get((provider_status or "").upper(), "PROCESSING")

    def _mark_refunded(self, refund: RefundRequest) -> None:
        refund.completed_at = datetime.now(timezone.utc)
        order = refund.order
        order.payment_status = "REFUNDED"
        order.status = "REFUNDED"

    def process_refund_webhook(self, provider_refund_id: str, status: str, order_id_str: str) -> None:
        """Process a Cashfree refund webhook event idempotently."""
        refund = self.db.scalar(
            select(RefundRequest).where(RefundRequest.provider_refund_id == provider_refund_id)
        )
        if refund is None:
            refund = self.db.scalar(
                select(RefundRequest).where(RefundRequest.idempotency_key == f"refund-{order_id_str}")
            ) if order_id_str else None
        if refund is None:
            return  # Unknown refund — ignore

        if refund.status == "SUCCESS":
            return  # Already completed — idempotent

        mapped = self._map_refund_status(status)
        refund.status = mapped
        if mapped == "SUCCESS":
            self._mark_refunded(refund)
        elif mapped == "FAILED":
            refund.failed_at = datetime.now(timezone.utc)
            refund.failure_reason = f"Provider status: {status}"
            refund.order.payment_status = "REFUND_FAILED"
        if provider_refund_id:
            refund.provider_refund_id = provider_refund_id
        self.db.commit()

    def retry_failed_refund(self, admin: User, order_id: UUID) -> RefundRequest:
        """Admin retries a failed refund."""
        order = self._get_order(order_id)
        refund = self.db.scalar(
            select(RefundRequest).where(RefundRequest.order_id == order.id, RefundRequest.status == "FAILED")
        )
        if refund is None:
            raise BadRequestError("No failed refund to retry")

        refund.status = "PENDING"
        refund.failed_at = None
        refund.failure_reason = None
        order.payment_status = "REFUND_PENDING"
        self._request_provider_refund(refund)
        self.db.commit()
        return refund

    def get_refund_status(self, order_id: UUID) -> RefundRequest | None:
        return self.db.scalar(select(RefundRequest).where(RefundRequest.order_id == order_id))


def is_fulfillable(order: Order) -> bool:
    """Gate check: can this order be submitted to CJ?"""
    if order.payment_status != "PAID":
        return False
    if order.status in UNFULFILLABLE_STATUSES:
        return False
    if order.cancelled_at is not None:
        return False
    return True
