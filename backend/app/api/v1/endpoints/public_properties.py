from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.exceptions import NotFoundError
from app.models.entities import Property, PropertyType
from app.repositories.property_repository import PropertyRepository
from app.schemas.enquiry import EnquiryCreate, PublicEnquiryResponse
from app.schemas.property import LocationDTO, PublicPropertyDTO, PublicPropertyPageDTO, public_verification
from app.services.enquiry_service import EnquiryService

router = APIRouter(tags=["properties"])


def public_dto(prop: Property) -> PublicPropertyDTO:
    verification = public_verification(
        prop.verification.verification_status if prop.verification else "NOT_REVIEWED",
        prop.verification.verified_at if prop.verification else None,
    )
    return PublicPropertyDTO.model_validate({
        **prop.__dict__,
        "location": prop.location,
        "media": [m for m in prop.media if m.status == "READY" and m.public_url],
        "verification_label": verification.status.value,
        "verification": verification,
    })


@router.get("/properties", response_model=PublicPropertyPageDTO)
def list_properties(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=48),
    property_type: PropertyType | None = Query(default=None, alias="type"),
    bhk: int | None = Query(default=None, ge=1, le=4),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    locality: str | None = Query(default=None, min_length=1, max_length=140),
    search: str | None = Query(default=None, min_length=1, max_length=120),
    sort: str = Query(default="newest", pattern="^(newest|price_asc|price_desc)$"),
    db: Session = Depends(get_db),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        from app.core.exceptions import BadRequestError
        raise BadRequestError("Minimum price cannot exceed maximum price")
    properties, total = PropertyRepository(db).public_page(
        page=page,
        page_size=page_size,
        property_type=property_type,
        bhk=bhk,
        min_price=min_price,
        max_price=max_price,
        locality=locality,
        search=search,
        sort=sort,
    )
    return PublicPropertyPageDTO(items=[public_dto(prop) for prop in properties], page=page, page_size=page_size, total=total, has_more=page * page_size < total)


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
