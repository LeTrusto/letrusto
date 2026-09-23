from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


CHANNELS = ("INSTAGRAM", "FACEBOOK", "WHATSAPP")
STATUSES = ("DRAFT", "ACTIVE", "PAUSED", "COMPLETED")


class SocialPostInput(BaseModel):
    platform: str
    post_type: str = "POST"
    headline: str | None = None
    body: str = Field(min_length=1)
    cta: str | None = None
    content: str | None = None


class CampaignCreate(BaseModel):
    campaign_title: str = Field(min_length=2, max_length=180)
    campaign_key: str = Field(min_length=2, max_length=120, pattern=r"^[a-z0-9-]+$")
    source: str
    medium: str = Field(min_length=1, max_length=64)
    content: str | None = Field(default=None, max_length=120)
    status: str = "DRAFT"
    campaign_description: str | None = None
    social_posts: list[SocialPostInput] = Field(default_factory=list)


class CampaignUpdate(BaseModel):
    campaign_title: str | None = Field(default=None, min_length=2, max_length=180)
    campaign_description: str | None = None
    source: str | None = None
    medium: str | None = Field(default=None, max_length=64)
    content: str | None = Field(default=None, max_length=120)
    status: str | None = None
    social_posts: list[SocialPostInput] | None = None


class SocialPostDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    platform: str
    post_type: str
    headline: str | None
    body: str
    cta: str | None
    content: str | None
    status: str


class CampaignDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    property_id: UUID
    property_title: str
    property_slug: str
    campaign_title: str
    campaign_key: str
    campaign_description: str | None
    source: str
    medium: str
    content: str | None
    status: str
    public_path: str
    social_posts: list[SocialPostDTO]
    created_at: datetime
    updated_at: datetime