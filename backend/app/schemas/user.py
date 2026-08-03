from pydantic import BaseModel, EmailStr, Field


class UserDTO(BaseModel):
    id: str
    email: str
    full_name: str
    avatar_url: str | None
    role: str
    is_active: bool
    email_verified: bool
    created_at: str


class UserProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    avatar_url: str | None = None


class SavedComparisonDTO(BaseModel):
    id: int
    product_ids: list[str]
    label: str
    created_at: str


class SavedComparisonCreateRequest(BaseModel):
    product_ids: list[str] = Field(min_length=2, max_length=4)
    label: str = Field(default="", max_length=200)


class PriceAlertDTO(BaseModel):
    id: int
    product_id: str
    product_name: str
    current_price: float
    target_price: float | None
    is_active: bool
    created_at: str


class PriceAlertCreateRequest(BaseModel):
    product_id: str
    target_price: float | None = None


class DashboardResponse(BaseModel):
    user: UserDTO
    favorites_count: int
    saved_comparisons: list[SavedComparisonDTO]
    price_alerts: list[PriceAlertDTO]
    unread_notifications: int
    recent_conversations_count: int
