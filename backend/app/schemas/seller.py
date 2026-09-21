from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import SellerType


class SellerProfileRequest(BaseModel):
    seller_type: SellerType = SellerType.OWNER
    display_name: str = Field(min_length=1, max_length=160)
    phone: str = Field(min_length=7, max_length=32)
    whatsapp_available: bool = False
    email: str | None = Field(default=None, max_length=320)


class SellerProfileUpdate(BaseModel):
    seller_type: SellerType | None = None
    display_name: str | None = Field(default=None, min_length=1, max_length=160)
    phone: str | None = Field(default=None, min_length=7, max_length=32)
    whatsapp_available: bool | None = None
    email: str | None = Field(default=None, max_length=320)


class SellerProfileDTO(SellerProfileRequest):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    verification_status: str
