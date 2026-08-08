from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.entities import AITool, AIToolCategory, AIToolFactProvenance
from app.repositories.ai_tool_repository import AIToolRepository
from app.schemas.ai_tool import (
    AIToolRecommendationBudget,
    AIToolRecommendationIntent,
    AIToolRecommendationPricingPreference,
    AIToolRecommendationRequest,
)
from app.services.ai_tool_intent_router import AIToolIntentRouter
from app.services.ai_tool_recommendation_service import AIToolRecommendationService
from app.services.ai_tool_service import AIToolService


@pytest.fixture()
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    AIToolCategory.__table__.create(bind=engine)
    AITool.__table__.create(bind=engine)
    AIToolFactProvenance.__table__.create(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_tools(session) -> None:
    video = AIToolCategory(name="AI Video & Audio", slug="ai-video-audio", position=1)
    writing = AIToolCategory(name="AI Writing", slug="ai-writing", position=2)
    coding = AIToolCategory(name="AI Coding & Developer Tools", slug="ai-coding-developer-tools", position=3)
    image = AIToolCategory(name="AI Image & Design", slug="ai-image-design", position=4)
    session.add_all([video, writing, coding, image])
    session.flush()

    runway_id = uuid.uuid4()
    eleven_id = uuid.uuid4()

    session.add_all(
        [
            AITool(
                id=runway_id,
                slug="runway",
                name="Runway",
                provider="Runway",
                description="Video workflows",
                website_url="https://runwayml.com",
                category_id=video.id,
                lifecycle_status="published",
                pricing_model="monthly",
                pricing_amount=15,
                pricing_currency="USD",
                pricing_period="month",
                has_free_plan=True,
                use_cases=["youtube videos", "video editing"],
                features=["video editing", "templates", "api"],
                pros=["video-first"],
                cons=["credit usage limits"],
                best_for=["beginner creators", "teams"],
                not_ideal_for=["offline only"],
                tags=["video", "youtube"],
                platforms=["web"],
                integrations=["api"],
                affiliate_available=False,
                last_verified_at=datetime.now(timezone.utc),
            ),
            AITool(
                id=eleven_id,
                slug="elevenlabs",
                name="ElevenLabs",
                provider="ElevenLabs",
                description="Voice workflows",
                website_url="https://elevenlabs.io",
                category_id=video.id,
                lifecycle_status="published",
                pricing_model="monthly",
                pricing_amount=22,
                pricing_currency="USD",
                pricing_period="month",
                has_free_plan=False,
                use_cases=["voiceover", "audio narration"],
                features=["voice synthesis", "api"],
                pros=["voice quality"],
                cons=["higher paid tiers"],
                best_for=["advanced creators"],
                not_ideal_for=["free only"],
                tags=["audio", "voice"],
                platforms=["web"],
                integrations=["api"],
                affiliate_available=False,
                last_verified_at=datetime.now(timezone.utc),
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
                pricing_model="monthly",
                pricing_amount=12,
                pricing_currency="USD",
                pricing_period="month",
                has_free_plan=True,
                use_cases=["blogging", "editing"],
                features=["grammar", "templates"],
                pros=["easy to use"],
                cons=["limited advanced controls"],
                best_for=["beginner writers"],
                not_ideal_for=["developer tooling"],
                tags=["writing"],
                platforms=["web"],
                integrations=["google docs", "microsoft office"],
                affiliate_available=False,
                last_verified_at=datetime.now(timezone.utc),
            ),
            AITool(
                id=uuid.uuid4(),
                slug="jasper",
                name="Jasper",
                provider="Jasper",
                description="Writing copilot",
                website_url="https://www.jasper.ai",
                category_id=writing.id,
                lifecycle_status="published",
                pricing_model="monthly",
                pricing_amount=39,
                pricing_currency="USD",
                pricing_period="month",
                has_free_plan=False,
                use_cases=["blogging", "content creation"],
                features=["templates", "ai chat"],
                pros=["marketing workflows"],
                cons=["no free plan"],
                best_for=["marketing teams"],
                not_ideal_for=["free-only buyers"],
                tags=["writing"],
                platforms=["web"],
                integrations=["api"],
                affiliate_available=False,
                last_verified_at=datetime.now(timezone.utc),
            ),
            AITool(
                id=uuid.uuid4(),
                slug="github-copilot",
                name="GitHub Copilot",
                provider="GitHub",
                description="Coding assistant",
                website_url="https://github.com/features/copilot",
                category_id=coding.id,
                lifecycle_status="published",
                pricing_model="monthly",
                pricing_amount=10,
                pricing_currency="USD",
                pricing_period="month",
                has_free_plan=False,
                use_cases=["coding", "developer productivity"],
                features=["code generation", "chat", "api"],
                pros=["ide integration"],
                cons=["requires review discipline"],
                best_for=["beginner developers", "teams"],
                not_ideal_for=["offline only"],
                tags=["coding", "developer"],
                platforms=["web", "desktop"],
                integrations=["api"],
                affiliate_available=False,
                last_verified_at=datetime.now(timezone.utc),
            ),
            AITool(
                id=uuid.uuid4(),
                slug="midjourney",
                name="Midjourney",
                provider="Midjourney",
                description="Image generation",
                website_url="https://www.midjourney.com",
                category_id=image.id,
                lifecycle_status="published",
                pricing_model="monthly",
                pricing_amount=10,
                pricing_currency="USD",
                pricing_period="month",
                has_free_plan=False,
                use_cases=["image generation", "design"],
                features=["image generation"],
                pros=["creative output"],
                cons=["subscription required"],
                best_for=["design teams"],
                not_ideal_for=["strictly free buyers"],
                tags=["image", "design"],
                platforms=["web"],
                integrations=["api"],
                affiliate_available=False,
                last_verified_at=datetime.now(timezone.utc),
            ),
            AITool(
                id=uuid.uuid4(),
                slug="internal-draft",
                name="Internal Draft",
                provider="Internal",
                description="Draft",
                website_url="https://example.com",
                category_id=video.id,
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

    session.add(
        AIToolFactProvenance(
            ai_tool_id=runway_id,
            fact_type="pricing",
            fact_key="monthly",
            source_url="https://runway.com/pricing",
            source_kind="official_provider",
            verified_at=datetime.now(timezone.utc),
        )
    )
    session.commit()


def test_recommendation_is_deterministic_and_published_only(session):
    seed_tools(session)
    service = AIToolRecommendationService(AIToolRepository(session))

    request = AIToolRecommendationRequest(
        query="I need an AI video tool for YouTube",
        intent=AIToolRecommendationIntent(
            category="ai-video-audio",
            useCases=["youtube videos"],
            requiredFeatures=["video editing"],
            platforms=["web"],
            integrations=["api"],
            budget=AIToolRecommendationBudget(currency="USD", max=20, pricingPeriod="monthly"),
            pricingPreference=AIToolRecommendationPricingPreference(model="monthly", preferFreePlan=True),
            experienceLevel="beginner",
        ),
        limit=3,
    )

    first = service.recommend(request)
    second = service.recommend(request)

    assert first.status == "ok"
    assert [item.aiTool.slug for item in first.results] == [item.aiTool.slug for item in second.results]
    assert [str(item.overallMatchScore) for item in first.results] == [str(item.overallMatchScore) for item in second.results]
    assert "internal-draft" not in {item.aiTool.slug for item in first.results}


def test_recommendation_labels_are_dynamic(session):
    seed_tools(session)
    service = AIToolRecommendationService(AIToolRepository(session))

    response = service.recommend(
        AIToolRecommendationRequest(
            query="Recommend a video tool",
            intent=AIToolRecommendationIntent(
                category="ai-video-audio",
                useCases=["youtube videos"],
                requiredFeatures=["api"],
            ),
            limit=3,
        )
    )

    labels = [row.resultLabel for row in response.results]
    assert labels[0] == "best_match"
    assert "strong_alternative" in labels or "budget_option" in labels


def test_unsupported_feature_returns_no_results(session):
    seed_tools(session)
    service = AIToolRecommendationService(AIToolRepository(session))

    response = service.recommend(
        AIToolRecommendationRequest(
            query="Need holographic rendering",
            intent=AIToolRecommendationIntent(
                category="ai-video-audio",
                requiredFeatures=["holographic rendering"],
            ),
        )
    )

    assert response.status == "unsupported_feature"
    assert response.results == []


def test_partial_or_empty_input_behaves_safely(session):
    seed_tools(session)
    service = AIToolRecommendationService(AIToolRepository(session))

    response = service.recommend(AIToolRecommendationRequest(query="help"))

    assert response.status == "insufficient_data"
    assert response.results == []


def test_query_only_extracts_video_budget_and_experience(session):
    seed_tools(session)
    service = AIToolService(AIToolRepository(session), intent_router=AIToolIntentRouter())

    response = service.recommend(
        AIToolRecommendationRequest(query="I need an AI tool to create YouTube videos under ₹2,000/month. I am a beginner.")
    )

    assert response.status == "ok"
    assert response.intent.category == "ai-video-audio"
    assert response.intent.experienceLevel == "beginner"
    assert response.intent.budget is not None
    assert response.intent.budget.currency == "INR"
    assert response.intent.budget.max == Decimal("2000")
    assert "youtube videos" in response.intent.useCases
    assert "video generation" in response.intent.useCases


def test_query_only_completely_free_maps_to_free_only_and_excludes_paid_only(session):
    seed_tools(session)
    service = AIToolService(AIToolRepository(session), intent_router=AIToolIntentRouter())

    response = service.recommend(AIToolRecommendationRequest(query="I need a completely free AI writing tool."))

    assert response.status == "ok"
    assert response.intent.pricingPreference is not None
    assert response.intent.pricingPreference.model == "free_only"
    assert response.results
    assert all(result.aiTool.pricing.hasFreePlan is True for result in response.results)
    assert "jasper" not in {result.aiTool.slug for result in response.results}


def test_query_only_prefer_free_keeps_paid_allowed(session):
    seed_tools(session)
    service = AIToolService(AIToolRepository(session), intent_router=AIToolIntentRouter())

    response = service.recommend(AIToolRecommendationRequest(query="I prefer a free AI writing tool but paid is okay."))

    assert response.status == "ok"
    assert response.intent.pricingPreference is not None
    assert response.intent.pricingPreference.model == "prefer_free"
    slugs = [result.aiTool.slug for result in response.results]
    assert "grammarly" in slugs
    assert "jasper" in slugs


def test_query_only_extracts_coding_beginner(session):
    seed_tools(session)
    service = AIToolService(AIToolRepository(session), intent_router=AIToolIntentRouter())

    response = service.recommend(AIToolRecommendationRequest(query="I need an AI coding tool for a beginner."))

    assert response.status == "ok"
    assert response.intent.category == "ai-coding-developer-tools"
    assert response.intent.experienceLevel == "beginner"


def test_query_only_extracts_image_generation(session):
    seed_tools(session)
    service = AIToolService(AIToolRepository(session), intent_router=AIToolIntentRouter())

    response = service.recommend(AIToolRecommendationRequest(query="I need an AI image generator."))

    assert response.status == "ok"
    assert response.intent.category == "ai-image-design"
    assert "image generation" in response.intent.useCases


def test_query_only_ambiguous_input_returns_insufficient_data_with_followup(session):
    seed_tools(session)
    service = AIToolService(AIToolRepository(session), intent_router=AIToolIntentRouter())

    response = service.recommend(AIToolRecommendationRequest(query="I need something."))

    assert response.status == "insufficient_data"
    assert response.results == []
    assert response.followUpQuestions


def test_query_only_deterministic_intent_yields_deterministic_ranking(session):
    seed_tools(session)
    service = AIToolService(AIToolRepository(session), intent_router=AIToolIntentRouter())

    req = AIToolRecommendationRequest(query="I need an AI tool to create YouTube videos under ₹2,000/month.")
    first = service.recommend(req)
    second = service.recommend(req)

    assert first.status == "ok"
    assert second.status == "ok"
    assert [item.aiTool.slug for item in first.results] == [item.aiTool.slug for item in second.results]
    assert [str(item.overallMatchScore) for item in first.results] == [str(item.overallMatchScore) for item in second.results]


def test_confidence_distinguishes_persisted_provenance_from_fallback(session):
    seed_tools(session)
    service = AIToolRecommendationService(AIToolRepository(session))

    response = service.recommend(
        AIToolRecommendationRequest(
            query="Need AI video tools",
            intent=AIToolRecommendationIntent(
                category="ai-video-audio",
                requiredFeatures=["video editing"],
                platforms=["web"],
            ),
            limit=5,
        )
    )

    runway = next(item for item in response.results if item.aiTool.slug == "runway")
    elevenlabs = next(item for item in response.results if item.aiTool.slug == "elevenlabs")

    assert runway.provenance
    assert elevenlabs.provenance
    assert runway.confidence.provenanceStrength > elevenlabs.confidence.provenanceStrength


def test_generic_persisted_homepage_does_not_count_as_strict_provenance(session):
    seed_tools(session)

    elevenlabs = session.query(AITool).filter(AITool.slug == "elevenlabs").one()
    session.add(
        AIToolFactProvenance(
            ai_tool_id=elevenlabs.id,
            fact_type="integration",
            fact_key="api",
            source_url=elevenlabs.website_url,
            source_kind="official_provider",
            verified_at=datetime.now(timezone.utc),
        )
    )
    session.commit()

    service = AIToolRecommendationService(AIToolRepository(session))
    response = service.recommend(
        AIToolRecommendationRequest(
            query="Need voice workflow tools",
            intent=AIToolRecommendationIntent(category="ai-video-audio", requiredFeatures=["api"]),
            limit=5,
        )
    )

    eleven = next(item for item in response.results if item.aiTool.slug == "elevenlabs")
    assert eleven.confidence.provenanceStrength == Decimal("58")


def test_non_official_source_kind_is_omitted_from_persisted_provenance(session):
    seed_tools(session)

    runway = session.query(AITool).filter(AITool.slug == "runway").one()
    session.add(
        AIToolFactProvenance(
            ai_tool_id=runway.id,
            fact_type="feature",
            fact_key="video editing",
            source_url="https://community.example/runway-guide",
            source_kind="community",
            verified_at=datetime.now(timezone.utc),
        )
    )
    session.commit()

    service = AIToolRecommendationService(AIToolRepository(session))
    response = service.recommend(
        AIToolRecommendationRequest(
            query="Need AI video tools",
            intent=AIToolRecommendationIntent(category="ai-video-audio", requiredFeatures=["video editing"]),
            limit=3,
        )
    )

    result = next(item for item in response.results if item.aiTool.slug == "runway")
    assert all(item.sourceKind == "official_provider" for item in result.provenance)
