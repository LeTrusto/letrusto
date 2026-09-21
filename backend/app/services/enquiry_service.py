from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError, UnauthorizedError
from app.models.entities import LeadStatus, Property, PropertyEnquiry, LeadStatusHistory, SellerProfile, User
from app.schemas.enquiry import EnquiryCreate, LeadStatusUpdate
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
        return list(self.db.scalars(select(PropertyEnquiry).join(Property).join(SellerProfile).where(
            PropertyEnquiry.property_id == property_id, SellerProfile.user_id == user.id
        ).order_by(PropertyEnquiry.created_at.desc())))

    def update_status(self, user: User, enquiry_id: UUID, payload: LeadStatusUpdate) -> PropertyEnquiry:
        enquiry = self.db.scalar(select(PropertyEnquiry).join(Property).join(SellerProfile).where(
            PropertyEnquiry.id == enquiry_id, SellerProfile.user_id == user.id
        ))
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
        return enquiry
