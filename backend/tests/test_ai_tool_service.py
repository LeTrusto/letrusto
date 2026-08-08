from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.exceptions import NotFoundError
from app.models.entities import AITool, AIToolCategory
from app.repositories.ai_tool_repository import AIToolRepository
from app.schemas.ai_tool import AIToolRecommendationCandidateRequest, AIToolSearchQuery
from app.services.ai_tool_service import AIToolService


@pytest.fixture()
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    AIToolCategory.__table__.create(bind=engine)
    AITool.__table__.create(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_tools(session) -> None:
    category = AIToolCategory(name="AI Assistants", slug="ai-assistants", position=1)
    session.add(category)
    session.flush()

    session.add_all(
        [
            AITool(
                id=uuid.uuid4(),
                slug="chatgpt",
                name="ChatGPT",
                provider="OpenAI",
                description="Assistant",
                website_url="https://chatgpt.com",
                category_id=category.id,
                lifecycle_status="published",
                use_cases=["research"],
                features=["chat"],
                pros=["adoption"],
                cons=["paid tier variance"],
                best_for=["teams"],
                not_ideal_for=["offline-only"],
                tags=["assistant"],
                platforms=["web"],
                integrations=["api"],
                affiliate_available=False,
                last_verified_at=datetime.now(timezone.utc),
            ),
            AITool(
                id=uuid.uuid4(),
                slug="internal-draft",
                name="Internal Draft Tool",
                provider="Example",
                description="Draft",
                website_url="https://example.com",
                category_id=category.id,
                lifecycle_status="draft",
                use_cases=[],
                features=[],
                pros=[],
                cons=[],
                best_for=[],
                not_ideal_for=[],
                tags=[],
                platforms=[],
                integrations=[],
                affiliate_available=False,
            ),
        ]
    )
    session.commit()


def test_list_tools_returns_only_published(session):
    seed_tools(session)
    service = AIToolService(AIToolRepository(session))

    response = service.list_tools()

    assert len(response.items) == 1
    assert response.items[0].slug == "chatgpt"


def test_get_tool_excludes_unpublished(session):
    seed_tools(session)
    service = AIToolService(AIToolRepository(session))

    with pytest.raises(NotFoundError):
        service.get_tool("internal-draft")


def test_compare_returns_two_way_tools(session):
    seed_tools(session)

    category = session.query(AIToolCategory).filter(AIToolCategory.slug == "ai-assistants").one()
    session.add(
        AITool(
            id=uuid.uuid4(),
            slug="claude",
            name="Claude",
            provider="Anthropic",
            description="Assistant",
            website_url="https://claude.ai",
            category_id=category.id,
            lifecycle_status="published",
            use_cases=["analysis"],
            features=["chat"],
            pros=["reasoning"],
            cons=["tier limits"],
            best_for=["docs"],
            not_ideal_for=["offline-only"],
            tags=["assistant"],
            platforms=["web"],
            integrations=["api"],
            affiliate_available=False,
        )
    )
    session.commit()

    service = AIToolService(AIToolRepository(session))
    response = service.compare("chatgpt", "claude")

    assert response.firstTool.slug == "chatgpt"
    assert response.secondTool.slug == "claude"


def test_compare_ignores_unpublished_tool_slug(session):
    seed_tools(session)
    service = AIToolService(AIToolRepository(session))

    response = service.compare("internal-draft", "chatgpt")

    assert response.firstTool.slug == "chatgpt"
    assert response.secondTool.slug == "chatgpt"


def test_search_returns_only_matching_published_tools(session):
    seed_tools(session)

    category = session.query(AIToolCategory).filter(AIToolCategory.slug == "ai-assistants").one()
    session.add(
        AITool(
            id=uuid.uuid4(),
            slug="claude",
            name="Claude",
            provider="Anthropic",
            description="Assistant for analysis",
            website_url="https://claude.ai",
            category_id=category.id,
            lifecycle_status="published",
            use_cases=["analysis"],
            features=["chat"],
            pros=["reasoning"],
            cons=["tier limits"],
            best_for=["docs"],
            not_ideal_for=["offline-only"],
            tags=["assistant"],
            platforms=["web"],
            integrations=["api"],
            affiliate_available=False,
        )
    )
    session.commit()

    service = AIToolService(AIToolRepository(session))
    response = service.search(AIToolSearchQuery(q="claude", page=1, pageSize=10))

    assert len(response.items) == 1
    assert response.items[0].slug == "claude"


def test_recommendation_candidates_note_mentions_stage_2(session):
    seed_tools(session)
    service = AIToolService(AIToolRepository(session))

    response = service.recommendation_candidates(AIToolRecommendationCandidateRequest(limit=3))

    assert response.items
    assert "Stage 2" in response.note
