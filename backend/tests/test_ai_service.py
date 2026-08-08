from app.ai.providers.heuristic import HeuristicLLMProvider
from app.schemas.ai import RecommendationWorkflowResponse, ShoppingIntentDTO
from app.services.ai_service import AIService, InMemorySessionStore


class DummyProductRepository:
    pass


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
