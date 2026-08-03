from pydantic import BaseModel, Field


class AnalyticsEventRequest(BaseModel):
    event_type: str = Field(
        pattern=r"^(product_view|search_query|ai_question|compare_use|wishlist_add|wishlist_remove|buy_click|page_view)$"
    )
    product_id: str | None = None
    session_id: str | None = None
    payload: dict = Field(default_factory=dict)
