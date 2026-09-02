from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class DigitalPaymentOrderDTO(BaseModel):
    attempt_id: UUID
    product_slug: str
    provider: str
    key_id: str
    razorpay_order_id: str
    amount: int
    currency: str


class DigitalPaymentVerification(BaseModel):
    razorpay_order_id: str = Field(min_length=1, max_length=120)
    razorpay_payment_id: str = Field(min_length=1, max_length=160)
    razorpay_signature: str = Field(min_length=1, max_length=256)


class DigitalPurchaseDTO(BaseModel):
    product_slug: str
    status: str
    download_url: str | None = None
    amount: Decimal
    currency: str
