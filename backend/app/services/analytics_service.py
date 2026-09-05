from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func

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

    def get_activation_stats(self, days: int = 30) -> dict:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        event_types = (
            "signup_started",
            "account_created",
            "widget_created",
            "first_event_added",
            "embed_code_viewed",
        )
        rows = (
            self.db.query(AnalyticsEvent.event_type, func.count(AnalyticsEvent.id))
            .filter(AnalyticsEvent.created_at >= cutoff, AnalyticsEvent.event_type.in_(event_types))
            .group_by(AnalyticsEvent.event_type)
            .all()
        )
        counts = {event_type: 0 for event_type in event_types}
        counts.update({event_type: count for event_type, count in rows})
        started = counts["signup_started"]
        return {
            "days": days,
            "counts": counts,
            "conversion_rates": {
                "account_created_from_signup": _rate(counts["account_created"], started),
                "widget_created_from_account": _rate(counts["widget_created"], counts["account_created"]),
                "first_event_from_widget": _rate(counts["first_event_added"], counts["widget_created"]),
                "embed_viewed_from_event": _rate(counts["embed_code_viewed"], counts["first_event_added"]),
            },
        }


def _rate(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator * 100, 1) if denominator else None
