from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.entities import Notification
from app.schemas.notification import NotificationDTO, NotificationListResponse


class NotificationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_notifications(self, user_id: uuid.UUID, limit: int = 50) -> NotificationListResponse:
        rows = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )
        unread_count = sum(1 for r in rows if not r.is_read)
        notifications = [
            NotificationDTO(
                id=r.id,
                type=r.type,
                title=r.title,
                body=r.body,
                is_read=r.is_read,
                created_at=r.created_at.isoformat(),
                related_entity_type=r.related_entity_type,
                related_entity_id=r.related_entity_id,
            )
            for r in rows
        ]
        return NotificationListResponse(notifications=notifications, unread_count=unread_count)

    def create_once(
        self,
        *,
        user_id: uuid.UUID,
        event_key: str,
        notification_type: str,
        title: str,
        body: str,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
    ) -> Notification:
        existing = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.event_key == event_key,
        ).first()
        if existing:
            return existing
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            body=body,
            event_key=event_key,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )
        self.db.add(notification)
        return notification

    def mark_read(self, user_id: uuid.UUID, notification_id: int) -> None:
        row = self.db.query(Notification).filter(
            Notification.id == notification_id, Notification.user_id == user_id
        ).first()
        if row:
            row.is_read = True
            self.db.commit()

    def mark_all_read(self, user_id: uuid.UUID) -> None:
        self.db.query(Notification).filter(
            Notification.user_id == user_id, Notification.is_read.is_(False)
        ).update({"is_read": True})
        self.db.commit()
