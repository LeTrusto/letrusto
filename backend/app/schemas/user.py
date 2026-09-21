from pydantic import BaseModel, Field


class UserDTO(BaseModel):
    id: str
    email: str | None
    full_name: str
    avatar_url: str | None
    role: str
    is_active: bool
    email_verified: bool
    created_at: str


class UserProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    avatar_url: str | None = None
