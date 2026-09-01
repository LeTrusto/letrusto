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


class StripeCheckoutSessionDTO(BaseModel):
    order_id: UUID
    provider: str
    provider_order_id: str
    checkout_url: str
    amount: Decimal
    currency: str


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


class AdminFulfillmentTimelineEventDTO(BaseModel):
    name: str
    occurred_at: str


class AdminFulfillmentHistoryItemDTO(BaseModel):
    order_id: UUID
    order_number: str
    created_at: str
    updated_at: str
    customer_email: str
    payment_status: str
    payment_provider: str | None = None
    provider_order_id: str | None = None
    provider_reference: str | None = None
    amount: Decimal
    currency: str
    order_status: str
    fulfillment_status: str
    printful_order_id: str | None = None
    printful_status: str | None = None
    tracking_status: str
    tracking_carrier: str | None = None
    tracking_number: str | None = None
    tracking_url: str | None = None
    cancellation_status: str | None = None
    cancellation_reason: str | None = None
    refund_status: str | None = None
    refund_amount: Decimal | None = None
    fulfillment_failure_category: str | None = None
    fulfillment_failure: bool
    last_fulfillment_attempt_at: str | None = None
    has_printful_order: bool
    timeline: list[AdminFulfillmentTimelineEventDTO]


class AdminFulfillmentHistoryResponse(BaseModel):
    items: list[AdminFulfillmentHistoryItemDTO]
    total: int
    page: int
    page_size: int


class SupplierPaymentRequest(BaseModel):
    required_amount_usd: Decimal


class AdminSupplierPaymentDTO(BaseModel):
    order_id: UUID
    supplier_order_id: str
    supplier_shipment_order_id: str
    required_amount_usd: Decimal
    payment_state: str
    supplier_status: str | None = None
    payment_error: str | None = None
    confirmation_required: bool
