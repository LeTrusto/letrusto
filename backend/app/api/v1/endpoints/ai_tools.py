from fastapi import APIRouter, Depends, Query

from app.api.deps import get_ai_tool_service
from app.schemas.ai_tool import (
    AIToolCompareResponse,
    AIToolDTO,
    AIToolRecommendationCandidateRequest,
    AIToolRecommendationCandidateResponse,
    AIToolsCatalogResponse,
    AIToolSearchQuery,
    PaginatedAIToolsResponse,
)
from app.services.ai_tool_service import AIToolService

router = APIRouter(prefix="/ai-tools", tags=["ai-tools"])


@router.get("", response_model=AIToolsCatalogResponse)
def list_ai_tools(service: AIToolService = Depends(get_ai_tool_service)) -> AIToolsCatalogResponse:
    return service.list_tools()


@router.get("/search", response_model=PaginatedAIToolsResponse)
def search_ai_tools(
    q: str = "",
    category: str | None = None,
    pricingModel: str | None = None,
    platform: str | None = None,
    integration: str | None = None,
    tag: str | None = None,
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=12, ge=1, le=100),
    service: AIToolService = Depends(get_ai_tool_service),
) -> PaginatedAIToolsResponse:
    query = AIToolSearchQuery(
        q=q,
        category=category,
        pricingModel=pricingModel,
        platform=platform,
        integration=integration,
        tag=tag,
        page=page,
        pageSize=pageSize,
    )
    return service.search(query)


@router.get("/compare", response_model=AIToolCompareResponse)
def compare_ai_tools(
    first: str | None = None,
    second: str | None = None,
    service: AIToolService = Depends(get_ai_tool_service),
) -> AIToolCompareResponse:
    return service.compare(first, second)


@router.get("/recommendations", response_model=AIToolRecommendationCandidateResponse)
def get_recommendation_candidates(
    category: str | None = None,
    limit: int = Query(default=4, ge=1, le=20),
    service: AIToolService = Depends(get_ai_tool_service),
) -> AIToolRecommendationCandidateResponse:
    return service.recommendation_candidates(AIToolRecommendationCandidateRequest(category=category, limit=limit))


@router.get("/{slug}", response_model=AIToolDTO)
def get_ai_tool(slug: str, service: AIToolService = Depends(get_ai_tool_service)) -> AIToolDTO:
    return service.get_tool(slug)
