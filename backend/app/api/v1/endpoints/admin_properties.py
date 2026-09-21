from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_admin, get_db
from app.core.exceptions import NotFoundError
from app.models.entities import Property, User
from app.schemas.property import AdminReviewRequest, PropertySubmitResponse, SellerPropertyDTO, VerificationUpdateRequest
from app.services.property_service import PropertyService
from app.services.property_verification_service import PropertyVerificationService
from app.api.v1.endpoints.seller_properties import seller_dto

router = APIRouter(prefix="/admin", tags=["admin-properties"])


@router.get("/properties", response_model=list[SellerPropertyDTO])
def review_queue(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    properties = db.scalars(select(Property).options(joinedload(Property.location), joinedload(Property.media), joinedload(Property.verification)).where(Property.status.in_(["SUBMITTED", "UNDER_REVIEW"]))).unique()
    return [seller_dto(prop) for prop in properties]


@router.get("/properties/{property_id}", response_model=SellerPropertyDTO)
def review_property(property_id: UUID, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    prop = db.scalar(select(Property).options(joinedload(Property.location), joinedload(Property.media), joinedload(Property.verification)).where(Property.id == property_id))
    if not prop:
        raise NotFoundError("Property not found")
    return seller_dto(prop)


@router.post("/properties/{property_id}/review", response_model=PropertySubmitResponse)
def review(property_id: UUID, payload: AdminReviewRequest, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    prop = db.get(Property, property_id)
    if not prop:
        raise NotFoundError("Property not found")
    PropertyService(db).admin_review(admin, prop, payload.decision, payload.notes)
    return PropertySubmitResponse(id=prop.id, status=prop.status)


@router.patch("/properties/{property_id}/verification")
def update_verification(property_id: UUID, payload: VerificationUpdateRequest, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return PropertyVerificationService(db).update(admin, property_id, payload)
