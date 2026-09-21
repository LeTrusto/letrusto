from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class PropertyListingCreateRequest(BaseModel):
    property_type: str = Field(pattern="^(flat|plot|house)$")
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(default="", max_length=4000)
    locality: str = Field(min_length=2, max_length=160)
    price: Decimal = Field(gt=0)
    area_sqft: Decimal | None = Field(default=None, gt=0)
    bedrooms: int | None = Field(default=None, ge=0, le=20)
    image_urls: list[str] = Field(default_factory=list, max_length=12)
    contact_name: str = Field(min_length=2, max_length=200)
    contact_phone: str = Field(min_length=8, max_length=20)
    contact_email: str | None = None


class PropertyListingDTO(BaseModel):
    id: UUID
    property_type: str
    title: str
    description: str
    locality: str
    city: str
    price: Decimal
    area_sqft: Decimal | None
    bedrooms: int | None
    image_urls: list[str]
    status: str
    is_featured: bool
    is_own_listing: bool
    contact_unlocked: bool
    contact_name: str | None
    contact_phone: str | None
    contact_email: str | None
    created_at: str


class PropertyListingPage(BaseModel):
    items: list[PropertyListingDTO]
    total: int
    page: int
    page_size: int


class PropertyPaymentOrderDTO(BaseModel):
    attempt_id: UUID
    listing_id: UUID
    purpose: str
    provider: str
    key_id: str
    razorpay_order_id: str
    amount: int
    currency: str


class PropertyPaymentVerification(BaseModel):
    razorpay_order_id: str = Field(min_length=1, max_length=120)
    razorpay_payment_id: str = Field(min_length=1, max_length=160)
    razorpay_signature: str = Field(min_length=1, max_length=256)


class PropertyModerationRequest(BaseModel):
    approve: bool
    reason: str | None = Field(default=None, max_length=500)
