from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class PaymentSessionDTO(BaseModel):
    order_id: UUID
    provider: str
    provider_order_id: str
    payment_session_id: str
    amount: Decimal
    currency: str


class RazorpayOrderDTO(BaseModel):
    order_id: UUID
    provider: str
    key_id: str
    razorpay_order_id: str
    amount: int
    currency: str


class RazorpayPaymentVerification(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentStatusDTO(BaseModel):
    order_id: UUID
    payment_status: str
    order_status: str
    fulfillment_status: str
    provider_reference: str | None


class FulfillmentDTO(BaseModel):
    order_id: UUID
    fulfillment_status: str
    supplier_order_id: str | None
    failure_reason: str | None = None


class AdminFulfillmentOrderDTO(FulfillmentDTO):
    order_number: str
    payment_status: str
    total: Decimal
    customer_email: str
    tracking_number: str | None = None
    tracking_carrier: str | None = None
    supplier_status: str | None = None
    last_supplier_sync_at: str | None = None
