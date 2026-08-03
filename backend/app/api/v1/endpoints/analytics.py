from fastapi import APIRouter, Depends

from app.api.deps import get_analytics_service, get_optional_user
from app.models.entities import User
from app.schemas.analytics import AnalyticsEventRequest
from app.schemas.common import MessageResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/events", response_model=MessageResponse, status_code=202)
def record_event(
    payload: AnalyticsEventRequest,
    service: AnalyticsService = Depends(get_analytics_service),
    current_user: User | None = Depends(get_optional_user),
) -> MessageResponse:
    user_id = current_user.id if current_user else None
    service.record_event(payload, user_id=user_id)
    return MessageResponse(message="Event recorded")
