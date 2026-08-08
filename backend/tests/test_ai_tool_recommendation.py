from __future__ import annotations

import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.entities import AITool, AIToolCategory
from app.repositories.ai_tool_repository import AIToolRepository
from app.schemas.ai_tool import AIToolRecommendationCandidateRequest
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


def seed_tools(session):
    assistants = AIToolCategory(name="AI Assistants", slug="ai-assistants", position=1)
    writing = AIToolCategory(name="AI Writing", slug="ai-writing", position=2)
    session.add_all([assistants, writing])
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
                category_id=assistants.id,
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
            ),
            AITool(
                id=uuid.uuid4(),
                slug="claude",
                name="Claude",
                provider="Anthropic",
                description="Assistant",
                website_url="https://claude.ai",
                category_id=assistants.id,
                lifecycle_status="published",
                use_cases=["analysis"],
                features=["chat"],
                pros=["reasoning"],
                cons=["tier limits"],
                best_for=["documents"],
                not_ideal_for=["offline-only"],
                tags=["assistant"],
                platforms=["web"],
                integrations=["api"],
                affiliate_available=False,
            ),
            AITool(
                id=uuid.uuid4(),
                slug="grammarly",
                name="Grammarly",
                provider="Grammarly",
                description="Writing assistant",
                website_url="https://grammarly.com",
                category_id=writing.id,
                lifecycle_status="published",
                use_cases=["editing"],
                features=["grammar"],
                pros=["ease"],
                cons=["premium limits"],
                best_for=["writers"],
                not_ideal_for=["offline-only"],
                tags=["writing"],
                platforms=["web"],
                integrations=["docs"],
                affiliate_available=False,
            ),
            AITool(
                id=uuid.uuid4(),
                slug="internal-draft",
                name="Internal Draft Tool",
                provider="Internal",
                description="Draft",
                website_url="https://internal.example.com",
                category_id=assistants.id,
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


def test_recommendation_candidates_returns_published_only(session):
    seed_tools(session)
    service = AIToolService(AIToolRepository(session))

    response = service.recommendation_candidates(AIToolRecommendationCandidateRequest(limit=10))

    slugs = {tool.slug for tool in response.items}
    assert "internal-draft" not in slugs
    assert slugs == {"chatgpt", "claude", "grammarly"}


def test_recommendation_candidates_respects_limit(session):
    seed_tools(session)
    service = AIToolService(AIToolRepository(session))

    response = service.recommendation_candidates(AIToolRecommendationCandidateRequest(limit=2))

    assert len(response.items) == 2


def test_recommendation_candidates_respects_category(session):
    seed_tools(session)
    service = AIToolService(AIToolRepository(session))

    response = service.recommendation_candidates(
        AIToolRecommendationCandidateRequest(category="ai-writing", limit=10)
    )

    assert len(response.items) == 1
    assert response.items[0].slug == "grammarly"
