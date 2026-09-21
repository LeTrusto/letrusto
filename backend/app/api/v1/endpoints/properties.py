from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user, get_db, get_optional_user
from app.models.entities import User
from app.schemas.properties import (
    PropertyListingCreateRequest,
    PropertyListingDTO,
    PropertyListingPage,
    PropertyModerationRequest,
    PropertyPaymentOrderDTO,
    PropertyPaymentVerification,
)
from app.services.property_service import PropertyService

router = APIRouter(prefix="/properties", tags=["properties"])


@router.get("", response_model=PropertyListingPage)
def list_properties(
    property_type: str | None = Query(default=None),
    locality: str | None = Query(default=None),
    min_price: Decimal | None = Query(default=None),
    max_price: Decimal | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> PropertyListingPage:
    return PropertyService(db).list_listings(current_user, property_type, locality, min_price, max_price, page, page_size)


@router.get("/mine", response_model=list[PropertyListingDTO])
def list_my_properties(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[PropertyListingDTO]:
    return PropertyService(db).list_mine(current_user)


@router.get("/{listing_id}", response_model=PropertyListingDTO)
def get_property(listing_id: UUID, current_user: User | None = Depends(get_optional_user), db: Session = Depends(get_db)) -> PropertyListingDTO:
    return PropertyService(db).get_listing(listing_id, current_user)


@router.post("", response_model=PropertyPaymentOrderDTO)
def create_property(payload: PropertyListingCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PropertyPaymentOrderDTO:
    return PropertyService(db).create_listing(current_user, payload)


@router.post("/{listing_id}/listing-payment/verify", response_model=PropertyListingDTO)
def verify_listing_payment(listing_id: UUID, payload: PropertyPaymentVerification, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PropertyListingDTO:
    return PropertyService(db).verify_listing_payment(current_user, listing_id, payload)


@router.post("/{listing_id}/unlock", response_model=PropertyPaymentOrderDTO)
def request_contact_unlock(listing_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PropertyPaymentOrderDTO:
    return PropertyService(db).request_contact_unlock(current_user, listing_id)


@router.post("/{listing_id}/unlock/verify", response_model=PropertyListingDTO)
def verify_contact_unlock(listing_id: UUID, payload: PropertyPaymentVerification, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PropertyListingDTO:
    return PropertyService(db).verify_contact_unlock(current_user, listing_id, payload)


@router.get("/admin/pending", response_model=list[PropertyListingDTO])
def admin_list_pending(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> list[PropertyListingDTO]:
    return PropertyService(db).admin_list_pending()


@router.post("/admin/{listing_id}/moderate", response_model=PropertyListingDTO)
def admin_moderate(listing_id: UUID, payload: PropertyModerationRequest, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> PropertyListingDTO:
    return PropertyService(db).admin_moderate(listing_id, payload)
