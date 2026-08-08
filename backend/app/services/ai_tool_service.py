from app.core.exceptions import NotFoundError
from app.repositories.ai_tool_repository import AIToolRepository
from app.schemas.common import Pagination
from app.schemas.ai_tool import (
    AIToolCompareResponse,
    AIToolDTO,
    AIToolRecommendationCandidateRequest,
    AIToolRecommendationCandidateResponse,
    AIToolsCatalogResponse,
    AIToolSearchQuery,
    PaginatedAIToolsResponse,
)
from app.services.ai_tool_mapper import to_ai_tool_dto


class AIToolService:
    def __init__(self, repository: AIToolRepository) -> None:
        self.repository = repository

    def list_tools(self) -> AIToolsCatalogResponse:
        items = [to_ai_tool_dto(tool) for tool in self.repository.list_published()]
        return AIToolsCatalogResponse(items=items)

    def get_tool(self, slug: str) -> AIToolDTO:
        tool = self.repository.get_published_by_slug(slug)
        if not tool:
            raise NotFoundError(f"AI tool '{slug}' not found")
        return to_ai_tool_dto(tool)

    def search(self, query: AIToolSearchQuery) -> PaginatedAIToolsResponse:
        matched = self.repository.search_published(query)

        total_items = len(matched)
        total_pages = max(1, (total_items + query.pageSize - 1) // query.pageSize)
        page = min(query.page, total_pages)
        start = (page - 1) * query.pageSize
        end = start + query.pageSize

        return PaginatedAIToolsResponse(
            items=[to_ai_tool_dto(tool) for tool in matched[start:end]],
            pagination=Pagination(
                page=page,
                pageSize=query.pageSize,
                totalItems=total_items,
                totalPages=total_pages,
                hasNextPage=page < total_pages,
                hasPreviousPage=page > 1,
            ),
        )

    def compare(self, first_slug: str | None, second_slug: str | None) -> AIToolCompareResponse:
        tools = self.repository.list_published()
        if not tools:
            raise NotFoundError("No published AI tools found")

        first = self.repository.get_published_by_slug(first_slug) if first_slug else tools[0]
        if not first:
            first = tools[0]

        second = self.repository.get_published_by_slug(second_slug) if second_slug else None
        if second and second.slug == first.slug:
            second = None

        if not second:
            second = next((item for item in tools if item.slug != first.slug), first)

        return AIToolCompareResponse(firstTool=to_ai_tool_dto(first), secondTool=to_ai_tool_dto(second))

    def recommendation_candidates(
        self,
        request: AIToolRecommendationCandidateRequest,
    ) -> AIToolRecommendationCandidateResponse:
        query = AIToolSearchQuery(category=request.category, page=1, pageSize=max(1, request.limit))
        ranked = self.repository.search_published(query)
        return AIToolRecommendationCandidateResponse(
            items=[to_ai_tool_dto(tool) for tool in ranked[: request.limit]],
            note=(
                "Stage 2 returns recommendation-ready published tools only. "
                "Recommendation intelligence will be introduced in Stage 3."
            ),
        )
