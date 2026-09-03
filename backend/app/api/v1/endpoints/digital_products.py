from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.models.entities import User
from app.schemas.digital_products import DigitalPaymentOrderDTO, DigitalPaymentVerification, DigitalPurchaseDTO
from app.services.digital_product_service import DigitalProductService

router = APIRouter(prefix="/digital-products", tags=["digital-products"])


@router.post("/{product_slug}/payment-order", response_model=DigitalPaymentOrderDTO)
def create_payment_order(
    product_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DigitalPaymentOrderDTO:
    return DigitalProductService(db).create_payment_order(current_user, product_slug)


@router.post("/internal/fulfillment-test/payment-order", response_model=DigitalPaymentOrderDTO)
def create_internal_test_payment_order(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> DigitalPaymentOrderDTO:
    return DigitalProductService(db).create_payment_order(current_admin, "letrusto-fulfillment-test-toolkit")


@router.post("/{product_slug}/verify", response_model=DigitalPurchaseDTO)
def verify_payment(
    product_slug: str,
    payload: DigitalPaymentVerification,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DigitalPurchaseDTO:
    return DigitalProductService(db).verify_payment(current_user, product_slug, payload)


@router.get("/{product_slug}/download", response_class=FileResponse)
def download_product(
    product_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    path, _ = DigitalProductService(db).download_path(current_user, product_slug)
    return FileResponse(path, media_type="text/csv", filename=path.name)
