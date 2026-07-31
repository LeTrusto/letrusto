from fastapi import APIRouter, Depends, Query

from app.api.deps import get_ai_service
from app.schemas.ai import (
    AssistantMessageRequest,
    AssistantMessageResponse,
    BuyingGuideResponse,
    ComparisonSummaryRequest,
    ComparisonSummaryResponse,
    RecommendationWorkflowResponse,
    ReviewSummaryResponse,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/assistant", response_model=AssistantMessageResponse)
def ask_assistant(
    payload: AssistantMessageRequest,
    service: AIService = Depends(get_ai_service),
) -> AssistantMessageResponse:
    return service.chat_assistant(payload.message, payload.sessionId, payload.limit)


@router.get("/recommendations", response_model=RecommendationWorkflowResponse)
def get_ai_recommendations(
    q: str,
    limit: int = Query(default=4, ge=1, le=8),
    service: AIService = Depends(get_ai_service),
) -> RecommendationWorkflowResponse:
    return service.recommendation_workflow(q, limit)


@router.post("/compare-summary", response_model=ComparisonSummaryResponse)
def get_compare_summary(
    payload: ComparisonSummaryRequest,
    service: AIService = Depends(get_ai_service),
) -> ComparisonSummaryResponse:
    return service.compare_summary(payload.firstProductId, payload.secondProductId)


@router.get("/products/{product_id}/review-summary", response_model=ReviewSummaryResponse)
def get_review_summary(
    product_id: str,
    service: AIService = Depends(get_ai_service),
) -> ReviewSummaryResponse:
    return service.review_summary(product_id)


@router.get("/products/{product_id}/buying-guide", response_model=BuyingGuideResponse)
def get_buying_guide(
    product_id: str,
    alternativesLimit: int = Query(default=3, ge=1, le=6),
    service: AIService = Depends(get_ai_service),
) -> BuyingGuideResponse:
    return service.buying_guide(product_id, alternativesLimit)
