from pydantic import BaseModel, Field


class ShippingAddress(BaseModel):
    line1: str = Field(min_length=1, max_length=200)
    line2: str | None = Field(default=None, max_length=200)
    city: str = Field(min_length=1, max_length=120)
    state: str = Field(min_length=1, max_length=120)
    postal_code: str = Field(min_length=1, max_length=20)
    country: str = Field(default="IN", max_length=2)


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
