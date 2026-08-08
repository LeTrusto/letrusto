from __future__ import annotations

import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.v1.endpoints.ai_tools import recommend_ai_tools
from app.models.entities import AITool, AIToolCategory, AIToolFactProvenance
from app.repositories.ai_tool_repository import AIToolRepository
from app.schemas.ai_tool import AIToolRecommendationIntent, AIToolRecommendationRequest
from app.services.ai_tool_service import AIToolService


@pytest.fixture()
def service():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    AIToolCategory.__table__.create(bind=engine)
    AITool.__table__.create(bind=engine)
    AIToolFactProvenance.__table__.create(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()

    category = AIToolCategory(name="AI Writing", slug="ai-writing", position=1)
    session.add(category)
    session.flush()
    session.add(
        AITool(
            id=uuid.uuid4(),
            slug="grammarly",
            name="Grammarly",
            provider="Grammarly",
            description="Writing assistant",
            website_url="https://grammarly.com",
            category_id=category.id,
            lifecycle_status="published",
            pricing_model="monthly",
            pricing_amount=12,
            has_free_plan=True,
            use_cases=["blogging"],
            features=["grammar"],
            pros=["easy"],
            cons=["limits"],
            best_for=["beginner writers"],
            not_ideal_for=["offline-only"],
            tags=["writing"],
            platforms=["web"],
            integrations=["google docs"],
            affiliate_available=False,
        )
    )
    session.commit()

    try:
        yield AIToolService(repository=AIToolRepository(session))
    finally:
        session.close()


def test_post_recommendations_contract(service: AIToolService):
    payload = AIToolRecommendationRequest(
        query="Best AI writing tool for blogging",
        intent=AIToolRecommendationIntent(
            category="ai-writing",
            useCases=["blogging"],
            requiredFeatures=["grammar"],
            platforms=["web"],
        ),
        limit=3,
    )

    response = recommend_ai_tools(payload, service=service)

    assert response.status == "ok"
    assert response.results
    assert response.results[0].aiTool.slug == "grammarly"


def test_post_recommendations_no_match_contract(service: AIToolService):
    payload = AIToolRecommendationRequest(
        query="Need unsupported requirement",
        intent=AIToolRecommendationIntent(
            category="ai-writing",
            requiredFeatures=["quantum parser"],
        ),
    )

    response = recommend_ai_tools(payload, service=service)

    assert response.status in {"unsupported_feature", "no_match"}
    assert response.results == []


def test_post_recommendations_query_only_normalization(service: AIToolService):
    payload = AIToolRecommendationRequest(
        query="I need a completely free AI writing tool.",
        limit=3,
    )

    response = recommend_ai_tools(payload, service=service)

    assert response.status == "ok"
    assert response.intent.category == "ai-writing"
    assert response.intent.pricingPreference is not None
    assert response.intent.pricingPreference.model == "free_only"
    assert response.results
