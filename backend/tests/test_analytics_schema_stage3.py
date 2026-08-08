from app.schemas.analytics import AnalyticsEventRequest


def test_stage3_analytics_event_types_are_accepted():
    payload = AnalyticsEventRequest(
        event_type="ai_recommendation_completed",
        ai_tool_id="f57f86de-8be1-4caf-acd2-d8480905d12a",
        ai_tool_slug="runway",
        recommendation_id="rec-123",
        session_id="session-1",
        payload={"status": "ok"},
    )

    assert payload.event_type == "ai_recommendation_completed"
    assert payload.ai_tool_slug == "runway"
    assert payload.recommendation_id == "rec-123"
