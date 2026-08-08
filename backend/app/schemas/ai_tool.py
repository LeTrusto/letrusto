from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import Pagination


AIToolLifecycleStatus = Literal["draft", "published", "archived"]
AIToolPricingModel = Literal["free", "free_trial", "monthly", "yearly", "custom"]
RecommendationResultLabel = Literal["best_match", "strong_alternative", "budget_option"]
RecommendationStatus = Literal[
    "ok",
    "no_match",
    "insufficient_data",
    "conflicting_requirements",
    "overconstrained_budget",
    "unsupported_feature",
]


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


class AIToolRecommendationBudget(BaseModel):
    currency: str | None = None
    min: Decimal | None = None
    max: Decimal | None = None
    pricingPeriod: Literal["monthly", "yearly", "one_time", "unknown"] | None = None


class AIToolRecommendationPricingPreference(BaseModel):
    model: AIToolPricingModel | Literal["free_only", "prefer_free", "paid_allowed", "any", "unknown"] | None = None
    preferFreePlan: bool | None = None
    preferFreeTrial: bool | None = None


class AIToolRecommendationIntent(BaseModel):
    category: str | None = None
    useCases: list[str] = Field(default_factory=list)
    requiredFeatures: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
    integrations: list[str] = Field(default_factory=list)
    budget: AIToolRecommendationBudget | None = None
    pricingPreference: AIToolRecommendationPricingPreference | None = None
    experienceLevel: Literal["beginner", "intermediate", "advanced", "team", "unknown"] | None = None
    constraints: list[str] = Field(default_factory=list)


class AIToolRecommendationRequest(BaseModel):
    query: str | None = Field(default=None, min_length=2, max_length=500)
    intent: AIToolRecommendationIntent | None = None
    limit: int = Field(default=5, ge=1, le=20)


class AIToolRecommendationFactor(BaseModel):
    score: Decimal = Decimal("0")
    weight: Decimal = Decimal("0")
    matchedInputs: list[str] = Field(default_factory=list)
    matchedToolValues: list[str] = Field(default_factory=list)
    missingRequiredInputs: list[str] = Field(default_factory=list)
    missingToolData: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class AIToolRecommendationPenalty(BaseModel):
    code: Literal[
        "missing_required_feature",
        "budget_exceeded",
        "unsupported_platform",
        "unsupported_integration",
        "insufficient_verified_data",
    ]
    delta: Decimal
    reason: str


class AIToolRecommendationFactors(BaseModel):
    categoryMatch: AIToolRecommendationFactor
    useCaseMatch: AIToolRecommendationFactor
    featureMatch: AIToolRecommendationFactor
    platformMatch: AIToolRecommendationFactor
    integrationMatch: AIToolRecommendationFactor
    budgetMatch: AIToolRecommendationFactor
    experienceMatch: AIToolRecommendationFactor
    penalties: list[AIToolRecommendationPenalty] = Field(default_factory=list)
    overallMatchScore: Decimal


class AIToolRecommendationExplanation(BaseModel):
    whyRecommended: list[str] = Field(default_factory=list)
    tradeOffs: list[str] = Field(default_factory=list)
    coveredRequirements: list[str] = Field(default_factory=list)
    missingRequirements: list[str] = Field(default_factory=list)
    disclaimer: str | None = None


class AIToolRecommendationConfidence(BaseModel):
    score: Decimal
    level: Literal["low", "medium", "high"]
    metadataCompleteness: Decimal
    provenanceStrength: Decimal
    freshness: Decimal
    requirementCoverage: Decimal
    missingDataFlags: list[str] = Field(default_factory=list)


class AIToolRecommendationProvenance(BaseModel):
    aiToolId: str
    factType: Literal["pricing", "feature", "integration", "platform", "use_case"]
    factKey: str
    sourceUrl: str | None = None
    sourceKind: Literal["official_provider", "vendor_docs", "internal_editorial"]
    verifiedAt: str | None = None


class AIToolRecommendationResult(BaseModel):
    rank: int
    resultLabel: RecommendationResultLabel
    aiTool: AIToolDTO
    overallMatchScore: Decimal
    factors: AIToolRecommendationFactors
    explanation: AIToolRecommendationExplanation
    confidence: AIToolRecommendationConfidence
    provenance: list[AIToolRecommendationProvenance] = Field(default_factory=list)


class AIToolRecommendationDiagnostic(BaseModel):
    code: str
    message: str


class AIToolRecommendationResponse(BaseModel):
    recommendationId: str
    status: RecommendationStatus
    query: str | None = None
    intent: AIToolRecommendationIntent
    results: list[AIToolRecommendationResult] = Field(default_factory=list)
    diagnostics: list[AIToolRecommendationDiagnostic] = Field(default_factory=list)
    followUpQuestions: list[str] = Field(default_factory=list)
    message: str
    generatedAt: str
