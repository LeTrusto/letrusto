from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import Pagination


AIToolLifecycleStatus = Literal["draft", "published", "archived"]
AIToolPricingModel = Literal["free", "free_trial", "monthly", "yearly", "custom"]


class AIToolCategoryDTO(BaseModel):
    id: int
    name: str
    slug: str
    position: int


class AIToolPricingDTO(BaseModel):
    model: AIToolPricingModel | None = None
    amount: Decimal | None = None
    currency: str | None = None
    period: str | None = None
    hasFreePlan: bool | None = None
    hasFreeTrial: bool | None = None
    trialDays: int | None = None
    notes: str | None = None
    pricingUrl: str | None = None


class AIToolDTO(BaseModel):
    id: str
    slug: str
    name: str
    provider: str
    description: str
    websiteUrl: str
    logoUrl: str | None = None
    category: AIToolCategoryDTO
    lifecycleStatus: AIToolLifecycleStatus
    pricing: AIToolPricingDTO
    letrustoScore: Decimal | None = None
    useCases: list[str]
    features: list[str]
    pros: list[str]
    cons: list[str]
    bestFor: list[str]
    notIdealFor: list[str]
    whyLetrustoRecommends: str | None = None
    tags: list[str]
    platforms: list[str]
    integrations: list[str]
    affiliateAvailable: bool = False
    affiliateUrl: str | None = None
    lastVerifiedAt: str | None = None


class AIToolSearchQuery(BaseModel):
    q: str = ""
    category: str | None = None
    pricingModel: AIToolPricingModel | None = None
    platform: str | None = None
    integration: str | None = None
    tag: str | None = None
    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=12, ge=1, le=100)


class PaginatedAIToolsResponse(BaseModel):
    items: list[AIToolDTO]
    pagination: Pagination


class AIToolsCatalogResponse(BaseModel):
    items: list[AIToolDTO]


class AIToolCompareResponse(BaseModel):
    firstTool: AIToolDTO
    secondTool: AIToolDTO


class AIToolRecommendationCandidateRequest(BaseModel):
    category: str | None = None
    limit: int = Field(default=4, ge=1, le=20)


class AIToolRecommendationCandidateResponse(BaseModel):
    items: list[AIToolDTO]
    note: str
