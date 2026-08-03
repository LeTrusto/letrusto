from pydantic import BaseModel


class NotificationDTO(BaseModel):
    id: int
    type: str
    title: str
    body: str
    product_id: str | None
    is_read: bool
    created_at: str


class NotificationListResponse(BaseModel):
    notifications: list[NotificationDTO]
    unread_count: int
