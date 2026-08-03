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
                product_id=str(r.product_id) if r.product_id else None,
                is_read=r.is_read,
                created_at=r.created_at.isoformat(),
            )
            for r in rows
        ]
        return NotificationListResponse(notifications=notifications, unread_count=unread_count)

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
