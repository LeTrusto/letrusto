from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError, UnauthorizedError
from app.models.entities import AdminReview, AdminReviewDecision, Location, Property, PropertyStatus, PropertyType, PropertyVerification, SellerProfile, User
from app.repositories.property_repository import PropertyRepository
from app.schemas.property import PropertyCreate, PropertyUpdate
from app.services.property_audit_service import AuditService

_ALLOWED: dict[str, set[str]] = {
    "DRAFT": {"SUBMITTED"}, "SUBMITTED": {"UNDER_REVIEW"},
    "UNDER_REVIEW": {"CHANGES_REQUESTED", "APPROVED", "REJECTED"},
    "APPROVED": {"LIVE"}, "LIVE": {"SUSPENDED", "SOLD", "WITHDRAWN", "EXPIRED"},
    "SUSPENDED": {"LIVE"}, "CHANGES_REQUESTED": {"SUBMITTED"}, "EXPIRED": {"SUBMITTED"},
}


class PropertyService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = PropertyRepository(db)
        self.audit = AuditService(db)

    def _profile(self, user: User) -> SellerProfile:
        profile = self.repo.seller_profile(user.id)
        if not profile:
            raise BadRequestError("Create a seller profile first")
        return profile

    def create_draft(self, user: User, payload: PropertyCreate) -> Property:
        profile = self._profile(user)
        if not self.db.scalar(select(Location).where(Location.id == payload.location_id, Location.is_active.is_(True))):
            raise BadRequestError("Active location not found")
        prop = Property(seller_profile_id=profile.id, slug="pending", **payload.model_dump())
        self.db.add(prop)
        self.db.flush()
        prop.slug = f"{payload.title.lower().replace(' ', '-')[:120]}-{str(prop.id)[-8:]}"
        self.db.add(PropertyVerification(property=prop))
        self.audit.record(actor_user_id=user.id, entity_type="PROPERTY", entity_id=prop.id, action="PROPERTY_CREATED")
        self.db.commit()
        self.db.refresh(prop)
        return prop

    def get_owned(self, user: User, property_id: UUID) -> Property:
        prop = self.repo.property_for_seller(property_id, user.id)
        if not prop:
            raise NotFoundError("Property not found")
        return prop

    def update_draft(self, user: User, property_id: UUID, payload: PropertyUpdate) -> Property:
        prop = self.get_owned(user, property_id)
        if prop.status not in {PropertyStatus.DRAFT.value, PropertyStatus.CHANGES_REQUESTED.value}:
            raise BadRequestError("Only drafts or requested changes can be edited")
        for key, value in payload.model_dump().items():
            setattr(prop, key, value)
        self.db.commit()
        self.db.refresh(prop)
        return prop

    def transition(self, actor: User, prop: Property, target: PropertyStatus) -> Property:
        current = prop.status.value if isinstance(prop.status, PropertyStatus) else prop.status
        if target.value not in _ALLOWED.get(current, set()):
            raise BadRequestError(f"Invalid property transition: {current} to {target.value}")
        if actor.role != "admin" and target not in {PropertyStatus.SUBMITTED, PropertyStatus.WITHDRAWN, PropertyStatus.SOLD}:
            raise UnauthorizedError("Admin access required for this transition")
        prop.status = target.value
        now = datetime.now(timezone.utc)
        if target == PropertyStatus.SUBMITTED:
            prop.submitted_at = now
        if target == PropertyStatus.LIVE:
            prop.published_at = now
        self.audit.record(actor_user_id=actor.id, entity_type="PROPERTY", entity_id=prop.id, action="PROPERTY_STATUS_CHANGED", metadata={"from": current, "to": target.value})
        self.db.commit()
        self.db.refresh(prop)
        return prop

    def submit(self, user: User, property_id: UUID) -> Property:
        return self.transition(user, self.get_owned(user, property_id), PropertyStatus.SUBMITTED)

    def admin_review(self, admin: User, prop: Property, decision: str, notes: str | None) -> AdminReview:
        if admin.role != "admin":
            raise UnauthorizedError("Admin access required")
        decision_value = decision.value if isinstance(decision, AdminReviewDecision) else decision
        if prop.status == PropertyStatus.SUBMITTED.value:
            self.transition(admin, prop, PropertyStatus.UNDER_REVIEW)
        if decision_value == AdminReviewDecision.REINSTATED.value:
            self.transition(admin, prop, PropertyStatus.LIVE)
        elif decision_value == AdminReviewDecision.SUSPENDED.value:
            self.transition(admin, prop, PropertyStatus.SUSPENDED)
        else:
            target = PropertyStatus(decision_value)
            self.transition(admin, prop, target)
        review = AdminReview(property_id=prop.id, reviewer_id=admin.id, decision=decision_value, notes=notes)
        self.db.add(review)
        self.audit.record(actor_user_id=admin.id, entity_type="PROPERTY", entity_id=prop.id, action="PROPERTY_REVIEWED", metadata={"decision": decision_value})
        self.db.commit()
        self.db.refresh(review)
        return review
