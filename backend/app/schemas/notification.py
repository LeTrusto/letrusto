from pydantic import BaseModel


class NotificationDTO(BaseModel):
    id: int
    type: str
    title: str
    body: str
    is_read: bool
    created_at: str
    related_entity_type: str | None = None
    related_entity_id: str | None = None


class NotificationListResponse(BaseModel):
    notifications: list[NotificationDTO]
    unread_count: int
