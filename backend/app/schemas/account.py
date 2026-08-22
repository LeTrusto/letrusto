from pydantic import BaseModel, Field

from app.schemas.orders import OrderListDTO, ShippingAddress


class CustomerAccountDTO(BaseModel):
    email: str | None
    full_name: str
    phone: str | None = None
    shipping_address: ShippingAddress | None = None
    email_verified: bool
    created_at: str


class CustomerProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    phone: str | None = Field(default=None, min_length=7, max_length=30)
    shipping_address: ShippingAddress | None = None


class CustomerOrdersResponse(OrderListDTO):
    pass