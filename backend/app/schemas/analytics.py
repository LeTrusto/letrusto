from pydantic import BaseModel, Field


class AnalyticsEventRequest(BaseModel):
    event_type: str = Field(
        pattern=(
            r"^(product_view|search_query|ai_question|compare_use|wishlist_add|wishlist_remove|buy_click|page_view|"
            r"ai_recommendation_started|ai_recommendation_completed|ai_recommendation_no_match|"
            r"ai_recommendation_result_viewed|ai_tool_recommended|ai_tool_view_from_recommendation|"
            r"ai_tool_compare_from_recommendation|ai_tool_official_link_clicked)$"
        )
    )
    product_id: str | None = None
    ai_tool_id: str | None = None
    ai_tool_slug: str | None = None
    recommendation_id: str | None = None
    session_id: str | None = None
    payload: dict = Field(default_factory=dict)
