from app.ai.providers.heuristic import HeuristicLLMProvider
from app.schemas.ai_tool import (
    AIToolCategoryDTO,
    AIToolDTO,
    AIToolPricingDTO,
    AIToolRecommendationConfidence,
    AIToolRecommendationExplanation,
    AIToolRecommendationFactor,
    AIToolRecommendationFactors,
    AIToolRecommendationIntent,
    AIToolRecommendationResponse,
    AIToolRecommendationResult,
)
from app.schemas.ai import RecommendationWorkflowResponse, ShoppingIntentDTO
from app.services.ai_service import AIService, InMemorySessionStore


class DummyProductRepository:
    pass


class DummyIntentRouter:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def is_ai_tool_request(self, message: str) -> bool:
        return self.enabled

    def build_request(self, query: str, limit: int = 5):
        return type("Req", (), {"query": query, "intent": AIToolRecommendationIntent(), "limit": limit})()


class DummyRecommendationService:
    def __init__(self, raise_error: bool = False) -> None:
        self.raise_error = raise_error

    def recommend(self, request):
        if self.raise_error:
            raise RuntimeError("boom")

        factor = AIToolRecommendationFactor(score=100, weight=1)
        return AIToolRecommendationResponse(
            recommendationId="rid-1",
            status="ok",
            query=request.query,
            intent=AIToolRecommendationIntent(),
            results=[
                AIToolRecommendationResult(
                    rank=1,
                    resultLabel="best_match",
                    aiTool=AIToolDTO(
                        id="chatgpt",
                        slug="chatgpt",
                        name="ChatGPT",
                        provider="OpenAI",
                        description="Assistant",
                        websiteUrl="https://chatgpt.com",
                        category=AIToolCategoryDTO(id=1, name="AI Assistants", slug="ai-assistants", position=1),
                        lifecycleStatus="published",
                        pricing=AIToolPricingDTO(model="monthly"),
                        useCases=[],
                        features=[],
                        pros=[],
                        cons=[],
                        bestFor=[],
                        notIdealFor=[],
                        tags=[],
                        platforms=[],
                        integrations=[],
                    ),
                    overallMatchScore=91,
                    factors=AIToolRecommendationFactors(
                        categoryMatch=factor,
                        useCaseMatch=factor,
                        featureMatch=factor,
                        platformMatch=factor,
                        integrationMatch=factor,
                        budgetMatch=factor,
                        experienceMatch=factor,
                        overallMatchScore=91,
                    ),
                    explanation=AIToolRecommendationExplanation(
                        whyRecommended=["Matches category"],
                        tradeOffs=["Paid tiers vary"],
                    ),
                    confidence=AIToolRecommendationConfidence(
                        score=80,
                        level="high",
                        metadataCompleteness=80,
                        provenanceStrength=80,
                        freshness=80,
                        requirementCoverage=80,
                    ),
                )
            ],
            message="Deterministic response",
            generatedAt="2026-08-08T00:00:00+00:00",
        )


def test_chat_assistant_returns_reply_and_reuses_session():
    service = AIService(
        repository=DummyProductRepository(),
        provider=HeuristicLLMProvider(),
        session_store=InMemorySessionStore(ttl_minutes=30),
    )

    workflow = RecommendationWorkflowResponse(
        intent=ShoppingIntentDTO(),
        explanation="Stage 2 assistant response",
        rankedRecommendations=[],
        followUpQuestions=["What is your budget?"],
    )

    service._build_recommendation_workflow = lambda intent, limit: workflow  # type: ignore[attr-defined]
    service._build_assistant_reply = lambda message, wf: "Assistant draft reply"  # type: ignore[attr-defined]

    first = service.chat_assistant("I need help choosing", None, 4)
    second = service.chat_assistant("Can you refine this?", first.sessionId, 4)

    assert first.reply == "Assistant draft reply"
    assert first.workflow.followUpQuestions == ["What is your budget?"]
    assert second.sessionId == first.sessionId


def test_chat_assistant_uses_ai_tool_recommendations_when_routed():
    service = AIService(
        repository=DummyProductRepository(),
        provider=HeuristicLLMProvider(),
        session_store=InMemorySessionStore(ttl_minutes=30),
        ai_tool_intent_router=DummyIntentRouter(enabled=True),
        ai_tool_recommendation_service=DummyRecommendationService(),
    )

    workflow = RecommendationWorkflowResponse(
        intent=ShoppingIntentDTO(),
        explanation="Stage 2 assistant response",
        rankedRecommendations=[],
        followUpQuestions=["What is your budget?"],
    )

    service._build_recommendation_workflow = lambda intent, limit: workflow  # type: ignore[attr-defined]

    response = service.chat_assistant("Best AI writing tool?", None, 4)
    assert "AI tool recommendation engine" in response.reply


def test_chat_assistant_falls_back_when_ai_tool_flow_fails():
    service = AIService(
        repository=DummyProductRepository(),
        provider=HeuristicLLMProvider(),
        session_store=InMemorySessionStore(ttl_minutes=30),
        ai_tool_intent_router=DummyIntentRouter(enabled=True),
        ai_tool_recommendation_service=DummyRecommendationService(raise_error=True),
    )

    workflow = RecommendationWorkflowResponse(
        intent=ShoppingIntentDTO(),
        explanation="Stage 2 assistant response",
        rankedRecommendations=[],
        followUpQuestions=["What is your budget?"],
    )

    service._build_recommendation_workflow = lambda intent, limit: workflow  # type: ignore[attr-defined]
    service._build_assistant_reply = lambda message, wf: "Fallback assistant reply"  # type: ignore[attr-defined]

    response = service.chat_assistant("Best AI writing tool?", None, 4)
    assert response.reply == "Fallback assistant reply"


def test_chat_assistant_general_question_is_not_product_style():
    service = AIService(
        repository=DummyProductRepository(),
        provider=HeuristicLLMProvider(),
        session_store=InMemorySessionStore(ttl_minutes=30),
    )

    workflow = RecommendationWorkflowResponse(
        intent=ShoppingIntentDTO(),
        explanation="Stage 2 assistant response",
        rankedRecommendations=[],
        followUpQuestions=["What is your budget?"],
    )

    service._build_recommendation_workflow = lambda intent, limit: workflow  # type: ignore[attr-defined]
    service._build_assistant_reply = lambda message, wf: "For 'What is generative AI?', my top pick is Product X."  # type: ignore[attr-defined]

    response = service.chat_assistant("What is generative AI?", None, 4)
    assert "my top pick" not in response.reply.lower()
    assert "generative ai" in response.reply.lower()
