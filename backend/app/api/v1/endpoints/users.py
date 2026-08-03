import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_user_service
from app.models.entities import User
from app.schemas.common import MessageResponse
from app.schemas.user import (
    DashboardResponse,
    PriceAlertCreateRequest,
    PriceAlertDTO,
    SavedComparisonCreateRequest,
    SavedComparisonDTO,
    UserDTO,
    UserProfileUpdateRequest,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserDTO)
def get_my_profile(current_user: User = Depends(get_current_user)) -> UserDTO:
    from app.services.user_service import _to_user_dto
    return _to_user_dto(current_user)


@router.put("/me", response_model=UserDTO)
def update_my_profile(
    payload: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserDTO:
    return service.update_profile(current_user.id, payload)


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> DashboardResponse:
    return service.get_dashboard(current_user.id)


# ── Saved Comparisons ─────────────────────────────────────────────────────────
@router.get("/comparisons", response_model=list[SavedComparisonDTO])
def list_comparisons(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> list[SavedComparisonDTO]:
    return service.list_saved_comparisons(current_user.id)


@router.post("/comparisons", response_model=SavedComparisonDTO, status_code=201)
def save_comparison(
    payload: SavedComparisonCreateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> SavedComparisonDTO:
    return service.save_comparison(current_user.id, payload)


@router.delete("/comparisons/{comparison_id}", response_model=MessageResponse)
def delete_comparison(
    comparison_id: int,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> MessageResponse:
    service.delete_saved_comparison(current_user.id, comparison_id)
    return MessageResponse(message="Comparison deleted")


# ── Price Alerts ──────────────────────────────────────────────────────────────
@router.get("/price-alerts", response_model=list[PriceAlertDTO])
def list_price_alerts(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> list[PriceAlertDTO]:
    return service.list_price_alerts(current_user.id)


@router.post("/price-alerts", response_model=PriceAlertDTO, status_code=201)
def create_price_alert(
    payload: PriceAlertCreateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> PriceAlertDTO:
    return service.create_price_alert(current_user.id, payload)


@router.delete("/price-alerts/{alert_id}", response_model=MessageResponse)
def delete_price_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> MessageResponse:
    service.delete_price_alert(current_user.id, alert_id)
    return MessageResponse(message="Price alert deleted")
