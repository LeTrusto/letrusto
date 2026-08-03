from fastapi import APIRouter, Depends

from app.api.deps import get_optional_user, get_support_service
from app.models.entities import User
from app.schemas.support import FaqListResponse, SupportTicketRequest, SupportTicketResponse
from app.services.support_service import SupportService

router = APIRouter(prefix="/support", tags=["support"])


@router.get("/faq", response_model=FaqListResponse)
def get_faq(service: SupportService = Depends(get_support_service)) -> FaqListResponse:
    return service.get_faq()


@router.post("/tickets", response_model=SupportTicketResponse, status_code=201)
def create_ticket(
    payload: SupportTicketRequest,
    service: SupportService = Depends(get_support_service),
    current_user: User | None = Depends(get_optional_user),
) -> SupportTicketResponse:
    user_id = current_user.id if current_user else None
    return service.create_ticket(payload, user_id=user_id)
