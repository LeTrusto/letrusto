from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_notification_service
from app.models.entities import User
from app.schemas.common import MessageResponse
from app.schemas.notification import NotificationListResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationListResponse:
    return service.list_notifications(current_user.id)


@router.put("/{notification_id}/read", response_model=MessageResponse)
def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> MessageResponse:
    service.mark_read(current_user.id, notification_id)
    return MessageResponse(message="Notification marked as read")


@router.put("/read-all", response_model=MessageResponse)
def mark_all_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> MessageResponse:
    service.mark_all_read(current_user.id)
    return MessageResponse(message="All notifications marked as read")
