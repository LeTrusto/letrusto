from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_order_service, get_user_service
from app.models.entities import User
from app.schemas.account import CustomerAccountDTO, CustomerOrdersResponse, CustomerProfileUpdateRequest
from app.schemas.user import UserProfileUpdateRequest
from app.services.order_service import OrderService
from app.services.user_service import UserService

router = APIRouter(prefix="/account", tags=["account"])


@router.get("", response_model=CustomerAccountDTO)
def get_account(current_user: User = Depends(get_current_user)) -> CustomerAccountDTO:
    return CustomerAccountDTO(
        email=current_user.email,
        full_name=current_user.full_name,
        email_verified=current_user.email_verified,
        created_at=current_user.created_at.isoformat(),
    )


@router.get("/orders", response_model=CustomerOrdersResponse)
def get_account_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> CustomerOrdersResponse:
    return service.list_orders(current_user, page, page_size)


@router.patch("/profile", response_model=CustomerAccountDTO)
def update_account_profile(
    payload: CustomerProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> CustomerAccountDTO:
    updated = service.update_profile(current_user.id, UserProfileUpdateRequest(full_name=payload.full_name))
    return CustomerAccountDTO(
        email=updated.email,
        full_name=updated.full_name,
        email_verified=updated.email_verified,
        created_at=updated.created_at,
    )
