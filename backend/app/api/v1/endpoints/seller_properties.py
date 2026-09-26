from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_storage
from app.models.entities import User
from app.schemas.property import MediaUploadTargetRequest, MediaUploadTargetResponse, PropertyCreate, PropertySubmitResponse, PropertyUpdate, SellerPropertyDTO, public_verification
from app.schemas.seller import SellerProfileDTO, SellerProfileRequest, SellerProfileUpdate
from app.services.media_service import MediaService
from app.storage import MockObjectStorage, ObjectStorage
from app.services.property_service import PropertyService
from app.services.seller_profile_service import SellerProfileService

router = APIRouter(prefix="/seller", tags=["seller"])


def seller_dto(prop):
    verification = public_verification(
        prop.verification.verification_status if prop.verification else "NOT_REVIEWED",
        prop.verification.verified_at if prop.verification else None,
    )
    return SellerPropertyDTO.model_validate({
        **prop.__dict__,
        "location": prop.location,
        "media": prop.media,
        "verification_label": verification.status.value,
        "verification": verification,
    })


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


@router.post("/properties/{property_id}/request-changes", response_model=PropertySubmitResponse)
def request_property_changes(property_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    prop = PropertyService(db).request_changes(current_user, property_id)
    return PropertySubmitResponse(id=prop.id, status=prop.status)


@router.post("/properties/{property_id}/media/upload-target", response_model=MediaUploadTargetResponse, status_code=201)
def create_media_upload_target(property_id: UUID, payload: MediaUploadTargetRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), storage: ObjectStorage = Depends(get_storage)):
    prop = PropertyService(db).get_owned(current_user, property_id)
    if prop.status not in {"DRAFT", "CHANGES_REQUESTED"}:
        from app.core.exceptions import BadRequestError
        raise BadRequestError("Media can only be added to editable properties")
    media, target = MediaService(db, storage).create_upload_target(property_id=property_id, media_type=payload.media_type, mime_type=payload.mime_type, file_size_bytes=payload.file_size_bytes, is_cover=payload.is_cover, caption=payload.caption)
    return MediaUploadTargetResponse(media_id=media.id, upload_url=target.url, headers=target.headers, expires_at=target.expires_at, status=media.status)


@router.put("/media/mock-upload/{storage_key:path}")
async def mock_upload(storage_key: str, request: Request, _: User = Depends(get_current_user), storage: ObjectStorage = Depends(get_storage)):
    if not isinstance(storage, MockObjectStorage) or not storage_key.startswith("properties/") or ".." in storage_key:
        from app.core.exceptions import BadRequestError
        raise BadRequestError("Development mock upload is unavailable")
    MockObjectStorage.put(storage_key, await request.body(), request.headers.get("content-type", "application/octet-stream"))
    return {"status": "uploaded"}


@router.put("/properties/{property_id}/media/{media_id}/upload", response_model=dict)
async def upload_media(property_id: UUID, media_id: UUID, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), storage: ObjectStorage = Depends(get_storage)):
    PropertyService(db).get_owned(current_user, property_id)
    media = MediaService(db, storage).upload(
        property_id=property_id,
        media_id=media_id,
        content=await request.body(),
        content_type=request.headers.get("content-type", ""),
    )
    return {"id": media.id, "status": media.status, "public_url": media.public_url}


@router.get("/media/mock-public/{storage_key:path}")
def mock_public(storage_key: str, storage: ObjectStorage = Depends(get_storage)):
    from fastapi.responses import Response as FastAPIResponse
    from app.core.exceptions import NotFoundError
    if not isinstance(storage, MockObjectStorage) or ".." in storage_key:
        raise NotFoundError("Media not found")
    stored = MockObjectStorage.get(storage_key)
    if not stored:
        raise NotFoundError("Media not found")
    content, content_type = stored
    return FastAPIResponse(content=content, media_type=content_type)


@router.post("/properties/{property_id}/media/{media_id}/complete", response_model=dict)
def complete_media_upload(property_id: UUID, media_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), storage: ObjectStorage = Depends(get_storage)):
    PropertyService(db).get_owned(current_user, property_id)
    media = MediaService(db, storage).complete(property_id=property_id, media_id=media_id)
    return {"id": media.id, "status": media.status, "public_url": media.public_url}


@router.delete("/properties/{property_id}/media/{media_id}", status_code=204)
def delete_media(property_id: UUID, media_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), storage: ObjectStorage = Depends(get_storage)):
    PropertyService(db).get_owned(current_user, property_id)
    MediaService(db, storage).delete(property_id=property_id, media_id=media_id, actor=current_user)
