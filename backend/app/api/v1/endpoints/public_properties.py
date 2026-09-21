from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.exceptions import NotFoundError
from app.models.entities import Property
from app.repositories.property_repository import PropertyRepository
from app.schemas.enquiry import EnquiryCreate, PublicEnquiryResponse
from app.schemas.property import LocationDTO, PublicPropertyDTO
from app.services.enquiry_service import EnquiryService

router = APIRouter(tags=["properties"])


def public_dto(prop: Property) -> PublicPropertyDTO:
    verification = prop.verification.verification_status if prop.verification else "NOT_REVIEWED"
    return PublicPropertyDTO.model_validate({**prop.__dict__, "location": prop.location, "media": [m for m in prop.media if m.status == "READY"], "verification_label": verification})


@router.get("/properties", response_model=list[PublicPropertyDTO])
def list_properties(offset: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    return [public_dto(prop) for prop in PropertyRepository(db).public(offset, limit)]


@router.get("/properties/{slug}", response_model=PublicPropertyDTO)
def get_property(slug: str, db: Session = Depends(get_db)):
    prop = PropertyRepository(db).by_slug_live(slug)
    if not prop:
        raise NotFoundError("Property not found")
    return public_dto(prop)


@router.get("/locations", response_model=list[LocationDTO])
def list_locations(db: Session = Depends(get_db)):
    return PropertyRepository(db).locations()


@router.post("/properties/{property_id}/enquiries", response_model=PublicEnquiryResponse, status_code=201)
def create_enquiry(property_id: UUID, payload: EnquiryCreate, db: Session = Depends(get_db)):
    enquiry = EnquiryService(db).create(property_id, payload)
    return enquiry
