from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class CancelOrderRequest(BaseModel):
    reason: str = "Customer requested cancellation"


class CancellationStatusDTO(BaseModel):
    order_id: UUID
    order_status: str
    payment_status: str
    fulfillment_status: str
    cancellation_reason: str | None = None
    cancelled_at: str | None = None
    refund_status: str | None = None
    refund_amount: Decimal | None = None
    refund_message: str | None = None


class RefundDTO(BaseModel):
    id: UUID
    order_id: UUID
    provider: str
    provider_refund_id: str | None = None
    amount: Decimal
    currency: str
    status: str
    reason: str | None = None
    requested_by: str
    requested_at: str
    completed_at: str | None = None
    failed_at: str | None = None
    failure_reason: str | None = None


class AdminCancelRequest(BaseModel):
    reason: str = "Admin cancellation"
