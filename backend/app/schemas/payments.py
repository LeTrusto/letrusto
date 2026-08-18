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


class PaymentStatusDTO(BaseModel):
    order_id: UUID
    payment_status: str
    order_status: str
    fulfillment_status: str
    provider_reference: str | None
