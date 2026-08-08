from __future__ import annotations

import json
import uuid

from sqlalchemy.orm import Session

from app.models.entities import AnalyticsEvent
from app.schemas.analytics import AnalyticsEventRequest


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record_event(self, req: AnalyticsEventRequest, user_id: uuid.UUID | None = None) -> None:
        product_id: uuid.UUID | None = None
        ai_tool_id: uuid.UUID | None = None
        if req.product_id:
            try:
                product_id = uuid.UUID(req.product_id)
            except ValueError:
                pass
        if req.ai_tool_id:
            try:
                ai_tool_id = uuid.UUID(req.ai_tool_id)
            except ValueError:
                pass
        event = AnalyticsEvent(
            event_type=req.event_type,
            user_id=user_id,
            product_id=product_id,
            ai_tool_id=ai_tool_id,
            ai_tool_slug=req.ai_tool_slug,
            recommendation_id=req.recommendation_id,
            session_id=req.session_id,
            payload=json.dumps(req.payload),
        )
        self.db.add(event)
        self.db.commit()

    def get_stats(self) -> dict:
        from sqlalchemy import func, text
        total = self.db.query(AnalyticsEvent).count()
        by_type = (
            self.db.query(AnalyticsEvent.event_type, func.count(AnalyticsEvent.id))
            .group_by(AnalyticsEvent.event_type)
            .all()
        )
        return {
            "total_events": total,
            "by_type": {row[0]: row[1] for row in by_type},
        }
