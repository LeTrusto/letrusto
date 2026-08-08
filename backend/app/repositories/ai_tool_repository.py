import uuid

from sqlalchemy import Select, Text, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.entities import AITool, AIToolCategory, AIToolFactProvenance
from app.schemas.ai_tool import AIToolSearchQuery


class AIToolRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _load_options() -> tuple:
        return (selectinload(AITool.category),)

    def list_published(self) -> list[AITool]:
        stmt = (
            select(AITool)
            .options(*self._load_options())
            .where(AITool.lifecycle_status == "published")
            .order_by(AITool.last_verified_at.desc(), AITool.name.asc())
        )
        return list(self.db.scalars(stmt).unique().all())

    def get_published_by_slug(self, slug: str) -> AITool | None:
        stmt = (
            select(AITool)
            .options(*self._load_options())
            .where(AITool.slug == slug, AITool.lifecycle_status == "published")
        )
        return self.db.scalars(stmt).unique().first()

    def search_published(self, query: AIToolSearchQuery) -> list[AITool]:
        stmt: Select = (
            select(AITool)
            .join(AITool.category)
            .options(*self._load_options())
            .where(AITool.lifecycle_status == "published")
        )

        if query.category:
            stmt = stmt.where(AIToolCategory.slug == query.category)

        if query.pricingModel:
            stmt = stmt.where(AITool.pricing_model == query.pricingModel)

        if query.q.strip():
            q = query.q.strip().lower()
            stmt = stmt.where(
                func.lower(AITool.name).contains(q)
                | func.lower(AITool.provider).contains(q)
                | func.lower(AITool.description).contains(q)
            )

        # Filter JSON arrays using textual fallback to keep query simple and migration-safe.
        if query.platform:
            platform = query.platform.strip().lower()
            stmt = stmt.where(func.lower(AITool.platforms.cast(Text)).contains(platform))

        if query.integration:
            integration = query.integration.strip().lower()
            stmt = stmt.where(func.lower(AITool.integrations.cast(Text)).contains(integration))

        if query.tag:
            tag = query.tag.strip().lower()
            stmt = stmt.where(func.lower(AITool.tags.cast(Text)).contains(tag))

        stmt = stmt.order_by(AITool.last_verified_at.desc(), AITool.name.asc())
        return list(self.db.scalars(stmt).unique().all())

    def get_fact_provenance(self, tool_ids: list[uuid.UUID]) -> dict[str, list[AIToolFactProvenance]]:
        if not tool_ids:
            return {}

        stmt = select(AIToolFactProvenance).where(AIToolFactProvenance.ai_tool_id.in_(tool_ids))
        rows = list(self.db.scalars(stmt).all())

        grouped: dict[str, list[AIToolFactProvenance]] = {}
        for row in rows:
            key = str(row.ai_tool_id)
            grouped.setdefault(key, []).append(row)
        return grouped
