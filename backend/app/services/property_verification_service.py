from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, UnauthorizedError
from app.models.entities import Property, PropertyVerification, User
from app.schemas.property import VerificationUpdateRequest
from app.services.property_audit_service import AuditService


class PropertyVerificationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.audit = AuditService(db)

    def update(self, admin: User, property_id: UUID, payload: VerificationUpdateRequest) -> PropertyVerification:
        if admin.role != "admin":
            raise UnauthorizedError("Admin access required")
        prop = self.db.get(Property, property_id)
        if not prop:
            raise NotFoundError("Property not found")
        verification = self.db.scalar(select(PropertyVerification).where(PropertyVerification.property_id == property_id))
        if not verification:
            verification = PropertyVerification(property_id=property_id)
            self.db.add(verification)
        verification.verification_status = payload.verification_status.value
        verification.verification_method = payload.verification_method.value if payload.verification_method else None
        verification.notes = payload.notes
        verification.expires_at = payload.expires_at
        verification.verified_by = admin.id
        verification.verified_at = datetime.now(timezone.utc)
        self.audit.record(actor_user_id=admin.id, entity_type="PROPERTY", entity_id=property_id, action="VERIFICATION_CHANGED", metadata={"status": payload.verification_status.value})
        self.db.commit()
        self.db.refresh(verification)
        return verification
