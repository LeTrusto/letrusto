from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.product import ProductDTO


class ShoppingIntentDTO(BaseModel):
    budgetMin: int | None = None
    budgetMax: int | None = None
    usage: str | None = None
    category: str | None = None
    priorities: list[str] = Field(default_factory=list)


class RankedRecommendationDTO(BaseModel):
    product: ProductDTO
    score: float
    reasons: list[str]


class RecommendationWorkflowResponse(BaseModel):
    intent: ShoppingIntentDTO
    explanation: str
    rankedRecommendations: list[RankedRecommendationDTO]
    followUpQuestions: list[str]


class AssistantMessageRequest(BaseModel):
    message: str = Field(min_length=2, max_length=400)
    sessionId: str | None = None
    limit: int = Field(default=4, ge=1, le=8)


class AssistantMessageResponse(BaseModel):
    sessionId: str
    reply: str
    workflow: RecommendationWorkflowResponse


class ComparisonSummaryRequest(BaseModel):
    firstProductId: str
    secondProductId: str


class ComparisonSummaryResponse(BaseModel):
    winnerProductId: str
    summary: str
    keyAdvantages: list[str]
    tradeOffs: list[str]


class ReviewSummaryResponse(BaseModel):
    positives: list[str]
    negatives: list[str]
    buyingAdvice: str
    finalVerdict: str


class BuyingGuideResponse(BaseModel):
    worthBuying: bool
    verdict: str
    bestFor: list[str]
    alternatives: list[ProductDTO]
    priceValueAnalysis: str
