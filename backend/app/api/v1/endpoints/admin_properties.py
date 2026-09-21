from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_admin, get_db
from app.core.exceptions import NotFoundError
from app.models.entities import AdminReview, AuditLog, Property, PropertyEnquiry, PropertyStatus, SellerProfile, User
from app.schemas.admin import AdminAuditDTO, AdminDashboardDTO, AdminEnquiryDTO, AdminMediaDTO, AdminPropertyDTO, AdminReviewDTO, AdminSellerDTO, AdminVerificationDTO
from app.schemas.property import AdminReviewRequest, PropertySubmitResponse, VerificationUpdateRequest
from app.services.property_service import PropertyService
from app.services.property_verification_service import PropertyVerificationService

router = APIRouter(prefix="/admin", tags=["admin-properties"])


def _seller_dto(profile: SellerProfile) -> AdminSellerDTO:
    return AdminSellerDTO(
        id=profile.id,
        display_name=profile.display_name,
        seller_type=profile.seller_type,
        phone=profile.phone,
        email=profile.email or profile.user.email,
        whatsapp_available=profile.whatsapp_available,
        verification_status=profile.verification_status,
        property_count=len(profile.properties),
        created_at=profile.created_at,
    )


def _property_dto(prop: Property, reviews: list[AdminReview] | None = None, audits: list[AuditLog] | None = None) -> AdminPropertyDTO:
    return AdminPropertyDTO(
        id=prop.id,
        slug=prop.slug,
        title=prop.title,
        description=prop.description,
        property_type=prop.property_type,
        price_amount=prop.price_amount,
        currency=prop.currency,
        built_up_area_sqft=prop.built_up_area_sqft,
        carpet_area_sqft=prop.carpet_area_sqft,
        plot_area_sqft=prop.plot_area_sqft,
        bhk=prop.bhk,
        floor_number=prop.floor_number,
        total_floors=prop.total_floors,
        property_age_years=prop.property_age_years,
        facing=prop.facing,
        parking_details=prop.parking_details,
        maintenance_amount=prop.maintenance_amount,
        possession_status=prop.possession_status,
        road_width_ft=prop.road_width_ft,
        plot_dimensions=prop.plot_dimensions,
        corner_site=prop.corner_site,
        approval_information=prop.approval_information,
        amenities=prop.amenities,
        address_line=prop.address_line,
        address_visibility=prop.address_visibility,
        latitude=prop.latitude,
        longitude=prop.longitude,
        status=prop.status,
        submitted_at=prop.submitted_at,
        published_at=prop.published_at,
        created_at=prop.created_at,
        updated_at=prop.updated_at,
        location=prop.location,
        media=[AdminMediaDTO.model_validate(media) for media in prop.media],
        seller=_seller_dto(prop.seller_profile),
        verification=AdminVerificationDTO.model_validate(prop.verification) if prop.verification else None,
        reviews=[AdminReviewDTO(id=review.id, decision=review.decision, notes=review.notes, reviewer_id=review.reviewer_id, reviewer_name=None, created_at=review.created_at) for review in (reviews if reviews is not None else prop.reviews)],
        audit=[AdminAuditDTO(id=entry.id, action=entry.action, metadata=entry.metadata_json, actor_user_id=entry.actor_user_id, created_at=entry.created_at) for entry in audits or []],
    )


def _enquiry_dto(enquiry: PropertyEnquiry) -> AdminEnquiryDTO:
    return AdminEnquiryDTO(
        id=enquiry.id,
        property_id=enquiry.property_id,
        property_title=enquiry.property.title,
        seller_name=enquiry.property.seller_profile.display_name,
        buyer_name=enquiry.buyer_name,
        buyer_phone=enquiry.buyer_phone,
        buyer_email=enquiry.buyer_email,
        whatsapp_available=enquiry.whatsapp_available,
        budget_amount=enquiry.budget_amount,
        buying_timeline=enquiry.buying_timeline,
        message=enquiry.message,
        preferred_contact_method=enquiry.preferred_contact_method,
        source=enquiry.source,
        status=enquiry.status,
        consent_to_share=enquiry.consent_to_share,
        created_at=enquiry.created_at,
    )


@router.get("/dashboard", response_model=AdminDashboardDTO)
def dashboard(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    def count(status: str) -> int:
        return int(db.scalar(select(func.count()).select_from(Property).where(Property.status == status)) or 0)

    enquiries = db.scalars(select(PropertyEnquiry).options(joinedload(PropertyEnquiry.property).joinedload(Property.seller_profile)).order_by(PropertyEnquiry.created_at.desc()).limit(8)).all()
    return AdminDashboardDTO(
        awaiting_review=count(PropertyStatus.SUBMITTED.value) + count(PropertyStatus.UNDER_REVIEW.value),
        changes_requested=count(PropertyStatus.CHANGES_REQUESTED.value),
        live_properties=count(PropertyStatus.LIVE.value),
        suspended_properties=count(PropertyStatus.SUSPENDED.value),
        recent_enquiries=[_enquiry_dto(enquiry) for enquiry in enquiries],
    )


@router.get("/properties", response_model=list[AdminPropertyDTO])
def review_queue(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    properties = db.scalars(select(Property).options(joinedload(Property.location), joinedload(Property.media), joinedload(Property.verification), joinedload(Property.seller_profile).joinedload(SellerProfile.user), joinedload(Property.seller_profile).joinedload(SellerProfile.properties), joinedload(Property.reviews)).where(Property.status.in_(["SUBMITTED", "UNDER_REVIEW"])).order_by(Property.submitted_at.asc())).unique()
    return [_property_dto(prop) for prop in properties]


@router.get("/properties/{property_id}", response_model=AdminPropertyDTO)
def review_property(property_id: UUID, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    prop = db.scalar(select(Property).options(joinedload(Property.location), joinedload(Property.media), joinedload(Property.verification), joinedload(Property.seller_profile).joinedload(SellerProfile.user), joinedload(Property.seller_profile).joinedload(SellerProfile.properties), joinedload(Property.reviews)).where(Property.id == property_id))
    if not prop:
        raise NotFoundError("Property not found")
    audits = db.scalars(select(AuditLog).where(AuditLog.entity_type == "PROPERTY", AuditLog.entity_id == property_id).order_by(AuditLog.created_at.asc())).all()
    return _property_dto(prop, audits=audits)


@router.get("/enquiries", response_model=list[AdminEnquiryDTO])
def enquiries(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    rows = db.scalars(select(PropertyEnquiry).options(joinedload(PropertyEnquiry.property).joinedload(Property.seller_profile)).order_by(PropertyEnquiry.created_at.desc())).all()
    return [_enquiry_dto(row) for row in rows]


@router.get("/sellers", response_model=list[AdminSellerDTO])
def sellers(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    profiles = db.scalars(select(SellerProfile).options(joinedload(SellerProfile.user), joinedload(SellerProfile.properties)).order_by(SellerProfile.created_at.desc())).unique()
    return [_seller_dto(profile) for profile in profiles]


@router.post("/properties/{property_id}/review", response_model=PropertySubmitResponse)
def review(property_id: UUID, payload: AdminReviewRequest, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    prop = db.get(Property, property_id)
    if not prop:
        raise NotFoundError("Property not found")
    PropertyService(db).admin_review(admin, prop, payload.decision, payload.notes)
    return PropertySubmitResponse(id=prop.id, status=prop.status)


@router.post("/properties/{property_id}/publish", response_model=PropertySubmitResponse)
def publish(property_id: UUID, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    prop = db.get(Property, property_id)
    if not prop:
        raise NotFoundError("Property not found")
    PropertyService(db).transition(admin, prop, PropertyStatus.LIVE)
    return PropertySubmitResponse(id=prop.id, status=prop.status)


@router.patch("/properties/{property_id}/verification")
def update_verification(property_id: UUID, payload: VerificationUpdateRequest, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return PropertyVerificationService(db).update(admin, property_id, payload)
