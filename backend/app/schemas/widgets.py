from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WidgetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    domain_name: str = Field(min_length=1, max_length=255)
    theme_color: str = Field(default="#2563eb", min_length=4, max_length=20)
    position: str = Field(default="bottom-left", pattern="^(bottom-left|bottom-right|top-left|top-right)$")
    display_delay: int = Field(default=3, ge=1, le=3600)
    is_active: bool = True


class WidgetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    domain_name: str | None = Field(default=None, min_length=1, max_length=255)
    theme_color: str | None = Field(default=None, min_length=4, max_length=20)
    position: str | None = Field(default=None, pattern="^(bottom-left|bottom-right|top-left|top-right)$")
    display_delay: int | None = Field(default=None, ge=1, le=3600)
    is_active: bool | None = None


class WidgetEventCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=200)
    customer_location: str | None = Field(default=None, max_length=160)
    action_text: str | None = Field(default=None, max_length=300)
    avatar_url: str | None = Field(default=None, max_length=2000)
    rating: int | None = Field(default=None, ge=1, le=5)
    review_text: str | None = Field(default=None, max_length=5000)
    is_approved: bool = True


class WidgetEventDTO(WidgetEventCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    widget_id: UUID
    created_at: datetime


class WidgetDTO(WidgetCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime


class PublicWidgetEventDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_name: str
    customer_location: str | None
    action_text: str | None
    avatar_url: str | None
    rating: int | None
    review_text: str | None
    created_at: datetime


class PublicWidgetDTO(BaseModel):
    id: UUID
    position: str
    theme_color: str
    display_delay: int
    events: list[PublicWidgetEventDTO]
