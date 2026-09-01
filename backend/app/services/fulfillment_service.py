import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.entities import Order, OrderItem, User
from app.schemas.payments import AdminFulfillmentOrderDTO
from app.services.cancellation_service import is_fulfillable
from app.services.inventory_reservation_service import InventoryReservationService
from app.services.cj_supplier_payment_service import CJSupplierPaymentService, SupplierPaymentRecord, apply_payment_record_to_order
from app.services.email_service import EmailService
from app.suppliers.base import SupplierAdapter, SupplierTrackingResult
from app.suppliers.factory import build_supplier_adapter


logger = logging.getLogger(__name__)


class FulfillmentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _get_order(self, order_id: UUID, *, for_update: bool = False) -> Order:
        statement = select(Order).where(Order.id == order_id).options(selectinload(Order.items).selectinload(OrderItem.product), selectinload(Order.items).selectinload(OrderItem.variant))
        if for_update:
            statement = statement.with_for_update()
        order = self.db.scalar(statement)
        if order is None:
            raise NotFoundError("Order not found")
        return order

    @staticmethod
    def _supplier(order: Order) -> str:
        suppliers = {str(item.product.supplier or "").strip().lower() for item in order.items if item.product}
        if not suppliers or "" in suppliers:
            raise BadRequestError("Order item traceability is incomplete")
        if len(suppliers) > 1:
            raise BadRequestError("Orders with multiple suppliers are not supported")
        return suppliers.pop()

    @staticmethod
    def _address(order: Order, supplier: str) -> dict:
        address = order.shipping_address or {}
        required = {"address", "city", "state", "postal_code", "country"}
        missing = sorted(field for field in required if not str(address.get(field, "")).strip())
        if not order.customer_name.strip():
            missing.append("recipient name")
        if not order.customer_phone.strip():
            missing.append("phone")
        if missing:
            raise BadRequestError(f"Shipping address is missing: {', '.join(missing)}")
        if supplier == "cj" and str(address["country"]).upper() != "IN":
            raise BadRequestError("CJ fulfillment currently supports India addresses only")
        return address

    def list_orders(self) -> list[AdminFulfillmentOrderDTO]:
        orders = list(self.db.scalars(select(Order).where(Order.payment_status == "PAID").order_by(Order.created_at.desc())).all())
        return [AdminFulfillmentOrderDTO(order_id=order.id, order_number=order.order_number, payment_status=order.payment_status, total=order.total, fulfillment_status=order.fulfillment_status, supplier_order_id=order.supplier_order_id, failure_reason=order.fulfillment_failure_reason, customer_email=order.customer_email, tracking_number=order.tracking_number, tracking_carrier=order.tracking_carrier, supplier_status=order.supplier_status, last_supplier_sync_at=order.last_supplier_sync_at.isoformat() if order.last_supplier_sync_at else None) for order in orders]

    @staticmethod
    def map_supplier_status(status: str | None, current: str) -> str:
        normalized = (status or "").strip().lower()
        mapping = {
            "submitted": "SUBMITTED", "created": "SUBMITTED", "accepted": "PROCESSING",
            "processing": "PROCESSING", "shipped": "SHIPPED", "in transit": "SHIPPED",
            "delivered": "DELIVERED", "completed": "DELIVERED", "cancelled": "CANCELLED",
            "failed": "FAILED",
        }
        return mapping.get(normalized, current)

    async def sync_tracking(self, order_id: UUID) -> Order:
        order = self._get_order(order_id, for_update=True)
        if not order.supplier_order_id:
            raise BadRequestError("Order has no CJ order ID; tracking was not requested")
        if order.fulfillment_status in {"DELIVERED", "CANCELLED"}:
            return order
        supplier = self._supplier(order)
        settings = get_settings()
        order.last_supplier_sync_at = datetime.now(timezone.utc)
        if supplier == "cj" and not getattr(settings, "CJ_API_KEY", ""):
            order.fulfillment_failure_reason = "CJ_API_KEY is not configured; tracking was not synchronized"
            self.db.commit()
            return order
        try:
            adapter: SupplierAdapter = build_supplier_adapter(supplier)
            result: SupplierTrackingResult = await adapter.get_tracking(order.supplier_order_id)
        except Exception as exc:
            order.fulfillment_failure_reason = str(exc)[:500]
            self.db.commit()
            return order
        if not result.supported:
            order.fulfillment_failure_reason = result.error or "CJ tracking is unavailable"
            self.db.commit()
            return order
        previous_status = order.fulfillment_status
        order.supplier_status = result.supplier_status or order.supplier_status
        order.fulfillment_status = self.map_supplier_status(result.supplier_status, order.fulfillment_status)
        if result.tracking_number:
            order.tracking_number = result.tracking_number
        if result.carrier:
            order.tracking_carrier = result.carrier
        if result.tracking_url:
            order.tracking_url = result.tracking_url if result.tracking_url.startswith(("https://", "http://")) else None
        if result.shipped_at:
            order.shipped_at = datetime.fromisoformat(result.shipped_at.replace("Z", "+00:00"))
        if result.delivered_at:
            order.delivered_at = datetime.fromisoformat(result.delivered_at.replace("Z", "+00:00"))
        order.fulfillment_failure_reason = None
        self.db.commit()
        if order.fulfillment_status in {"SHIPPED", "DELIVERED"} and order.fulfillment_status != previous_status:
            self._send_shipment_notification(order, order.fulfillment_status, settings)
        return order

    def _send_shipment_notification(self, order: Order, status: str, settings: object) -> None:
        public_app_url = getattr(settings, "PUBLIC_APP_URL", "")
        if not public_app_url:
            return
        sent_field = "shipped_email_sent_at" if status == "SHIPPED" else "delivered_email_sent_at"
        template = "order_shipped" if status == "SHIPPED" else "order_delivered"
        locked_order = self._get_order(order.id, for_update=True)
        if getattr(locked_order, sent_field):
            self.db.rollback()
            return
        setattr(locked_order, sent_field, datetime.now(timezone.utc))
        locked_order.notification_failure_reason = None
        locked_order.notification_failed_at = None
        self.db.commit()
        items_summary = ", ".join(f"{item.product_name} x{item.quantity}" for item in locked_order.items)
        context = {
            "customer_name": locked_order.customer_name,
            "order_number": locked_order.order_number,
            "items_summary": items_summary or "Your LeTrusto order",
            "tracking_number": locked_order.tracking_number,
            "carrier": locked_order.tracking_carrier,
            "tracking_url": locked_order.tracking_url,
            "order_url": f"{public_app_url}/orders/{locked_order.id}",
        }
        try:
            EmailService.from_settings(settings).send_template(template, to=locked_order.customer_email, context=context)
        except Exception:
            logger.warning("Shipment notification delivery failed", extra={"order_id": str(locked_order.id), "notification": template})
            failed_order = self._get_order(locked_order.id, for_update=True)
            setattr(failed_order, sent_field, None)
            failed_order.notification_failure_reason = "Email delivery failed"
            failed_order.notification_failed_at = datetime.now(timezone.utc)
            self.db.commit()

    async def sync_pending_fulfillments(self) -> list[Order]:
        orders = list(self.db.scalars(select(Order).where(Order.payment_status == "PAID", Order.supplier_order_id.is_not(None), Order.fulfillment_status.not_in({"DELIVERED", "CANCELLED"}))).all())
        results = []
        for order in orders:
            results.append(await self.sync_tracking(order.id))
        return results

    async def submit(self, order_id: UUID, _: User | None = None) -> Order:
        order = self._get_order(order_id, for_update=True)
        if order.supplier_order_id:
            return order
        if not is_fulfillable(order):
            raise BadRequestError("Order is not eligible for fulfillment")
        if not InventoryReservationService(self.db).fulfillment_safe(order.id):
            raise BadRequestError("Order inventory reservation is not consumed")
        if order.payment_status != "PAID":
            raise BadRequestError("Only server-verified PAID orders can be fulfilled")
        if order.status in {"CANCELLED", "REFUNDED"}:
            raise BadRequestError("Cancelled or refunded orders cannot be fulfilled")
        if order.fulfillment_status == "SUBMITTING":
            raise BadRequestError("Fulfillment submission is already in progress")
        if not order.items:
            raise BadRequestError("Order has no items")
        supplier = self._supplier(order)
        address = self._address(order, supplier)
        payload_items = []
        for item in order.items:
            product = item.product
            variant = item.variant
            if product is None or variant is None:
                raise BadRequestError("Order item traceability is incomplete")
            if not product.supplier_product_id:
                raise BadRequestError(f"Product {product.name} has no supplier product ID")
            if not variant.supplier_variant_id:
                raise BadRequestError(f"Variant for {product.name} has no supplier variant ID")
            payload_items.append({"pid": product.supplier_product_id, "vid": variant.supplier_variant_id, "quantity": item.quantity})

        settings = get_settings()
        if supplier == "cj" and not getattr(settings, "CJ_API_KEY", ""):
            order.fulfillment_status = "FAILED"
            order.fulfillment_failure_reason = "CJ_API_KEY is not configured; no supplier order was created"
            self.db.commit()
            return order

        order.fulfillment_status = "SUBMITTING"
        order.fulfillment_failure_reason = None
        self.db.commit()
        try:
            adapter: SupplierAdapter = build_supplier_adapter(supplier)
            result = await adapter.create_order({
                "orderNumber": order.order_number,
                "shippingCustomerName": order.customer_name,
                "shippingPhone": order.customer_phone,
                "shippingAddress": address["address"],
                "shippingCity": address["city"],
                "shippingProvince": address["state"],
                "shippingZip": address["postal_code"],
                "shippingCountryCode": address["country"],
                "products": payload_items,
            })
        except Exception as exc:
            order.fulfillment_status = "FAILED"
            order.fulfillment_failure_reason = str(exc)[:500]
            self.db.commit()
            return order
        if not result.accepted or not result.supplier_order_id:
            order.fulfillment_status = "FAILED"
            order.fulfillment_failure_reason = result.error or "CJ rejected supplier order"
        else:
            order.supplier_order_id = result.supplier_order_id
            order.supplier_status = result.supplier_status or result.status
            order.supplier_pay_id = result.pay_id
            order.supplier_payment_url = result.payment_url
            order.supplier_shipment_order_id = result.shipment_order_id
            order.supplier_payment_state = result.payment_state or ("AWAITING_PAYMENT" if order.supplier_status == "UNPAID" else None)
            order.fulfillment_status = self.map_supplier_status(result.status, "SUBMITTED")
            order.fulfillment_submitted_at = datetime.now(timezone.utc)
        self.db.commit()
        return order

    async def pay_supplier(self, order_id: UUID, required_amount_usd: float) -> Order:
        order = self._get_order(order_id, for_update=True)
        if order.payment_status != "PAID":
            raise BadRequestError("Customer payment must be PAID before supplier payment")
        if not order.supplier_order_id:
            raise BadRequestError("Supplier payment requires an existing CJ order")
        if not order.supplier_shipment_order_id:
            raise BadRequestError("Supplier payment requires a CJ shipment order")
        if required_amount_usd <= 0:
            raise BadRequestError("Supplier payment amount must be positive")

        record = SupplierPaymentRecord(
            supplier_order_id=order.supplier_order_id,
            shipment_order_id=order.supplier_shipment_order_id,
            payment_state=order.supplier_payment_state or "REQUIRED",
            supplier_status=order.supplier_status,
            pay_id=order.supplier_pay_id,
            payment_error=order.supplier_payment_error,
            payment_attempted_at=order.supplier_payment_attempted_at,
            payment_confirmed_at=order.supplier_payment_confirmed_at,
        )
        try:
            result = await CJSupplierPaymentService(build_supplier_adapter("cj")).pay(record, required_amount_usd=required_amount_usd)
        except Exception as exc:
            record.payment_state = "FAILED"
            record.payment_error = str(exc)[:500]
            apply_payment_record_to_order(order, record)
            self.db.commit()
            return order
        if result.payment_url:
            order.supplier_payment_url = result.payment_url
        if result.shipment_order_id:
            order.supplier_shipment_order_id = result.shipment_order_id
        if result.supplier_status:
            order.supplier_status = result.supplier_status
        apply_payment_record_to_order(order, record)
        self.db.commit()
        return order