from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.entities import Order, OrderItem, User
from app.schemas.payments import AdminFulfillmentOrderDTO
from app.suppliers.base import SupplierTrackingResult
from app.suppliers.factory import build_supplier_adapter


class FulfillmentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _get_order(self, order_id: UUID) -> Order:
        order = self.db.scalar(
            select(Order).where(Order.id == order_id).options(selectinload(Order.items).selectinload(OrderItem.product), selectinload(Order.items).selectinload(OrderItem.variant))
        )
        if order is None:
            raise NotFoundError("Order not found")
        return order

    @staticmethod
    def _address(order: Order) -> dict:
        address = order.shipping_address or {}
        required = {"address", "city", "state", "postal_code", "country"}
        missing = sorted(field for field in required if not str(address.get(field, "")).strip())
        if not order.customer_name.strip():
            missing.append("recipient name")
        if not order.customer_phone.strip():
            missing.append("phone")
        if missing:
            raise BadRequestError(f"Shipping address is missing: {', '.join(missing)}")
        if str(address["country"]).upper() != "IN":
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
        order = self._get_order(order_id)
        if not order.supplier_order_id:
            raise BadRequestError("Order has no CJ order ID; tracking was not requested")
        if order.fulfillment_status in {"DELIVERED", "CANCELLED"}:
            return order
        settings = get_settings()
        order.last_supplier_sync_at = datetime.now(timezone.utc)
        if not settings.CJ_API_KEY:
            order.fulfillment_failure_reason = "CJ_API_KEY is not configured; tracking was not synchronized"
            self.db.commit()
            return order
        try:
            adapter = build_supplier_adapter("cj")
            result: SupplierTrackingResult = await adapter.get_tracking(order.supplier_order_id)
        except Exception as exc:
            order.fulfillment_failure_reason = str(exc)[:500]
            self.db.commit()
            return order
        if not result.supported:
            order.fulfillment_failure_reason = result.error or "CJ tracking is unavailable"
            self.db.commit()
            return order
        order.supplier_status = result.supplier_status or order.supplier_status
        order.fulfillment_status = self.map_supplier_status(result.supplier_status, order.fulfillment_status)
        if result.tracking_number:
            order.tracking_number = result.tracking_number
        if result.carrier:
            order.tracking_carrier = result.carrier
        if result.shipped_at:
            order.shipped_at = datetime.fromisoformat(result.shipped_at.replace("Z", "+00:00"))
        if result.delivered_at:
            order.delivered_at = datetime.fromisoformat(result.delivered_at.replace("Z", "+00:00"))
        order.fulfillment_failure_reason = None
        self.db.commit()
        return order

    async def sync_pending_fulfillments(self) -> list[Order]:
        orders = list(self.db.scalars(select(Order).where(Order.payment_status == "PAID", Order.supplier_order_id.is_not(None), Order.fulfillment_status.not_in({"DELIVERED", "CANCELLED"}))).all())
        results = []
        for order in orders:
            results.append(await self.sync_tracking(order.id))
        return results

    async def submit(self, order_id: UUID, _: User | None = None) -> Order:
        order = self._get_order(order_id)
        if order.supplier_order_id:
            return order
        if order.payment_status != "PAID":
            raise BadRequestError("Only server-verified PAID orders can be fulfilled")
        if order.status in {"CANCELLED", "REFUNDED"}:
            raise BadRequestError("Cancelled or refunded orders cannot be fulfilled")
        if order.fulfillment_status == "SUBMITTING":
            raise BadRequestError("Fulfillment submission is already in progress")
        if not order.items:
            raise BadRequestError("Order has no items")
        address = self._address(order)
        payload_items = []
        for item in order.items:
            product = item.product
            variant = item.variant
            if product is None or variant is None:
                raise BadRequestError("Order item traceability is incomplete")
            if not product.supplier_product_id:
                raise BadRequestError(f"Product {product.name} has no supplier product ID")
            if not variant.supplier_variant_id:
                raise BadRequestError(f"Variant for {product.name} has no CJ variant ID")
            payload_items.append({"pid": product.supplier_product_id, "vid": variant.supplier_variant_id, "quantity": item.quantity})

        settings = get_settings()
        if not settings.CJ_API_KEY:
            order.fulfillment_status = "FAILED"
            order.fulfillment_failure_reason = "CJ_API_KEY is not configured; no supplier order was created"
            self.db.commit()
            return order

        order.fulfillment_status = "SUBMITTING"
        order.fulfillment_failure_reason = None
        self.db.commit()
        try:
            adapter = build_supplier_adapter("cj")
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
            order.fulfillment_status = result.status or "SUBMITTED"
            order.fulfillment_submitted_at = datetime.now(timezone.utc)
        self.db.commit()
        return order