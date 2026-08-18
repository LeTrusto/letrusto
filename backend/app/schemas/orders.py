from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class CartItemRequest(BaseModel):
    product_id: str = Field(min_length=1, max_length=150)
    variant_id: str = Field(min_length=1, max_length=120)
    quantity: int = Field(ge=1, le=100)


class CartItemDTO(BaseModel):
    id: UUID
    product_id: str
    variant_id: str
    product_name: str
    variant_name: str
    quantity: int
    unit_price: Decimal
    inventory: int


class CartDTO(BaseModel):
    id: UUID
    items: list[CartItemDTO]
    subtotal: Decimal


class CustomerDetails(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)


class ShippingAddress(BaseModel):
    address: str = Field(min_length=3, max_length=500)
    city: str = Field(min_length=2, max_length=120)
    state: str = Field(min_length=2, max_length=120)
    postal_code: str = Field(min_length=4, max_length=12)
    country: str = Field(min_length=2, max_length=80)

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        return value.strip().upper()


class CreateOrderRequest(BaseModel):
    items: list[CartItemRequest] = Field(min_length=1, max_length=100)
    customer: CustomerDetails
    shipping_address: ShippingAddress
    idempotency_key: str = Field(min_length=8, max_length=100)


class OrderItemDTO(BaseModel):
    id: UUID
    product_name: str
    variant_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderDTO(BaseModel):
    id: UUID
    order_number: str
    status: str
    payment_status: str
    fulfillment_status: str
    subtotal: Decimal
    shipping_amount: Decimal
    total: Decimal
    currency: str
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    shipping_address: ShippingAddress
    items: list[OrderItemDTO]
    created_at: str
    payment_provider: str | None = None
    paid_at: str | None = None
    tracking_number: str | None = None
    tracking_carrier: str | None = None
    shipped_at: str | None = None
    delivered_at: str | None = None
