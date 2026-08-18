from pydantic import BaseModel, Field

from app.schemas.orders import OrderListDTO


class CustomerAccountDTO(BaseModel):
    email: str
    full_name: str
    email_verified: bool
    created_at: str


class CustomerProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)


class CustomerOrdersResponse(OrderListDTO):
    pass