from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.exceptions import BadRequestError, NotFoundError, UnauthorizedError
from app.models.entities import LeadStatus, Property, PropertyEnquiry, LeadStatusHistory, SellerProfile, User
from app.schemas.enquiry import EnquiryCreate, LeadStatusUpdate, SellerEnquiryDTO, SellerEnquiryHistoryDTO
from app.services.property_audit_service import AuditService


class EnquiryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.audit = AuditService(db)

    def create(self, property_id: UUID, payload: EnquiryCreate) -> PropertyEnquiry:
        prop = self.db.scalar(select(Property).where(Property.id == property_id, Property.status == "LIVE"))
        if not prop:
            raise NotFoundError("Property not found")
        if not payload.consent_to_share:
            raise BadRequestError("Consent is required to share your enquiry with the seller")
        recent = self.db.scalar(select(PropertyEnquiry).where(
            PropertyEnquiry.property_id == property_id,
            PropertyEnquiry.buyer_phone == payload.buyer_phone,
        ).order_by(PropertyEnquiry.created_at.desc()))
        data = payload.model_dump()
        data["consent_at"] = datetime.now(timezone.utc)
        data.pop("consent_to_share", None)
        enquiry = PropertyEnquiry(property_id=property_id, consent_to_share=True, **data)
        if recent:
            enquiry.duplicate_of_id = recent.id
        self.db.add(enquiry)
        self.db.flush()
        self.audit.record(actor_user_id=None, entity_type="ENQUIRY", entity_id=enquiry.id, action="ENQUIRY_CREATED")
        self.db.commit()
        self.db.refresh(enquiry)
        return enquiry

    def list_for_seller(self, user: User, property_id: UUID) -> list[PropertyEnquiry]:
        return list(self.db.scalars(self._seller_query(user).where(PropertyEnquiry.property_id == property_id).order_by(PropertyEnquiry.created_at.desc())).unique())

    def list_all_for_seller(self, user: User) -> list[PropertyEnquiry]:
        return list(self.db.scalars(self._seller_query(user).order_by(PropertyEnquiry.created_at.desc())).unique())

    def get_for_seller(self, user: User, enquiry_id: UUID) -> PropertyEnquiry:
        enquiry = self.db.scalar(self._seller_query(user).where(PropertyEnquiry.id == enquiry_id))
        if not enquiry:
            raise NotFoundError("Enquiry not found")
        return enquiry

    def to_seller_dto(self, enquiry: PropertyEnquiry) -> SellerEnquiryDTO:
        can_share_contact = bool(enquiry.consent_to_share)
        return SellerEnquiryDTO(
            id=enquiry.id,
            property_id=enquiry.property_id,
            property_slug=enquiry.property.slug,
            property_title=enquiry.property.title,
            locality=enquiry.property.location.name,
            buyer_name=enquiry.buyer_name,
            buyer_phone=enquiry.buyer_phone if can_share_contact else None,
            buyer_email=enquiry.buyer_email if can_share_contact else None,
            whatsapp_available=enquiry.whatsapp_available if can_share_contact else False,
            budget_amount=enquiry.budget_amount,
            buying_timeline=enquiry.buying_timeline,
            message=enquiry.message,
            preferred_contact_method=enquiry.preferred_contact_method,
            source=enquiry.source,
            source_medium=enquiry.source_medium,
            source_content=enquiry.source_content,
            campaign_id=enquiry.campaign_id,
            landing_path=enquiry.landing_path,
            consent_to_share=enquiry.consent_to_share,
            status=enquiry.status,
            created_at=enquiry.created_at,
            history=[SellerEnquiryHistoryDTO(old_status=item.old_status, new_status=item.new_status, note=item.note, created_at=item.created_at) for item in sorted(enquiry.status_history, key=lambda item: item.created_at)],
        )

    def _seller_query(self, user: User):
        return select(PropertyEnquiry).options(
            joinedload(PropertyEnquiry.property).joinedload(Property.location),
            selectinload(PropertyEnquiry.status_history),
        ).join(Property).join(SellerProfile).where(SellerProfile.user_id == user.id)

    def update_status(self, user: User, enquiry_id: UUID, payload: LeadStatusUpdate) -> PropertyEnquiry:
        enquiry = self.db.scalar(self._seller_query(user).where(PropertyEnquiry.id == enquiry_id))
        if not enquiry:
            if user.role != "admin":
                raise NotFoundError("Enquiry not found")
            enquiry = self.db.get(PropertyEnquiry, enquiry_id)
        if not enquiry:
            raise NotFoundError("Enquiry not found")
        old = enquiry.status
        if old == payload.status.value:
            return enquiry
        enquiry.status = payload.status.value
        self.db.add(LeadStatusHistory(enquiry_id=enquiry.id, old_status=old, new_status=payload.status.value, changed_by=user.id, note=payload.note))
        self.audit.record(actor_user_id=user.id, entity_type="ENQUIRY", entity_id=enquiry.id, action="LEAD_STATUS_CHANGED", metadata={"from": old, "to": payload.status.value})
        self.db.commit()
        self.db.refresh(enquiry)
        enquiry = self.get_for_seller(user, enquiry.id) if user.role != "admin" else enquiry
        return enquiry
