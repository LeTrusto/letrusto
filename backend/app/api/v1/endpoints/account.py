from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_user, get_digital_product_service, get_order_service, get_user_service
from app.models.entities import User
from app.schemas.account import CustomerAccountDTO, CustomerOrdersResponse, CustomerProfileUpdateRequest
from app.schemas.orders import ShippingAddress
from app.schemas.user import UserProfileUpdateRequest
from app.services.order_service import OrderService
from app.services.user_service import UserService
from app.services.digital_product_service import DigitalProductService
from app.schemas.digital_products import DigitalEntitlementDTO
from app.services.otp_auth_service import normalize_indian_mobile
from app.core.config import get_settings

router = APIRouter(prefix="/account", tags=["account"])

def _account_dto(user: User) -> CustomerAccountDTO:
    phone = user.phone_number or user.mobile_number
    if phone:
        try:
            phone = normalize_indian_mobile(phone)
        except Exception:
            phone = phone.strip()
    shipping_address = None
    if user.shipping_address:
        try:
            shipping_address = ShippingAddress.model_validate(user.shipping_address)
        except Exception:
            pass
    return CustomerAccountDTO(email=user.email, full_name=user.full_name, phone=phone, shipping_address=shipping_address, email_verified=user.email_verified, created_at=user.created_at.isoformat())


@router.get("", response_model=CustomerAccountDTO)
def get_account(current_user: User = Depends(get_current_user)) -> CustomerAccountDTO:
    return _account_dto(current_user)


@router.get("/orders", response_model=CustomerOrdersResponse)
def get_account_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> CustomerOrdersResponse:
    if not get_settings().PHYSICAL_COMMERCE_ENABLED:
        raise HTTPException(status_code=410, detail="Physical commerce is currently unavailable")
    return service.list_orders(current_user, page, page_size)


@router.get("/digital-purchases", response_model=list[DigitalEntitlementDTO])
def get_digital_purchases(current_user: User = Depends(get_current_user), service: DigitalProductService = Depends(get_digital_product_service)) -> list[DigitalEntitlementDTO]:
    return service.list_entitlements(current_user)


@router.patch("/profile", response_model=CustomerAccountDTO)
def update_account_profile(
    payload: CustomerProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> CustomerAccountDTO:
    updated = service.update_customer_profile(current_user.id, payload.full_name, payload.phone, payload.shipping_address)
    return _account_dto(updated)
