from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.entities import User
from app.schemas.property import MediaCreateRequest, PropertyCreate, PropertySubmitResponse, PropertyUpdate, SellerPropertyDTO
from app.schemas.seller import SellerProfileDTO, SellerProfileRequest, SellerProfileUpdate
from app.services.media_service import MediaService
from app.services.property_service import PropertyService
from app.services.seller_profile_service import SellerProfileService

router = APIRouter(prefix="/seller", tags=["seller"])


def seller_dto(prop):
    return SellerPropertyDTO.model_validate({**prop.__dict__, "location": prop.location, "media": prop.media, "verification_label": prop.verification.verification_status if prop.verification else "NOT_REVIEWED"})


@router.get("/profile", response_model=SellerProfileDTO)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SellerProfileService(db).get_or_create(current_user)


@router.post("/profile", response_model=SellerProfileDTO, status_code=201)
def create_profile(payload: SellerProfileRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SellerProfileService(db).get_or_create(current_user, payload)


@router.patch("/profile", response_model=SellerProfileDTO)
def update_profile(payload: SellerProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SellerProfileService(db).update(current_user, payload)


@router.post("/properties", response_model=SellerPropertyDTO, status_code=201)
def create_property(payload: PropertyCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return seller_dto(PropertyService(db).create_draft(current_user, payload))


@router.get("/properties", response_model=list[SellerPropertyDTO])
def list_properties(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = PropertyService(db)
    profile = service._profile(current_user)
    return [seller_dto(prop) for prop in profile.properties]


@router.get("/properties/{property_id}", response_model=SellerPropertyDTO)
def get_property(property_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return seller_dto(PropertyService(db).get_owned(current_user, property_id))


@router.patch("/properties/{property_id}", response_model=SellerPropertyDTO)
def update_property(property_id: UUID, payload: PropertyUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return seller_dto(PropertyService(db).update_draft(current_user, property_id, payload))


@router.post("/properties/{property_id}/submit", response_model=PropertySubmitResponse)
def submit_property(property_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    prop = PropertyService(db).submit(current_user, property_id)
    return PropertySubmitResponse(id=prop.id, status=prop.status)


@router.post("/properties/{property_id}/media", response_model=dict, status_code=201)
def add_media(property_id: UUID, payload: MediaCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    PropertyService(db).get_owned(current_user, property_id)
    media = MediaService(db).validate_metadata(
        property_id=property_id,
        media_type=payload.media_type,
        storage_key=payload.storage_key,
        mime_type=payload.mime_type,
        file_size_bytes=payload.file_size_bytes,
        is_cover=payload.is_cover,
        caption=payload.caption,
    )
    return {"id": media.id, "status": media.status}
