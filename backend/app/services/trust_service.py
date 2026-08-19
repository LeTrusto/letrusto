from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.core.trust import TRUST_AUDIT_EVENTS, TRUST_CLAIM_STATUSES, TRUST_VERIFICATION_METHODS
from app.models.entities import TrustAuditEvent, TrustClaim, TrustClaimEvidence, TrustEvidence, TrustVerification, User
from app.repositories.trust_repository import TrustRepository
from app.schemas.trust import (
    TrustClaimCreate,
    TrustClaimDetailDTO,
    TrustClaimEvidenceCreate,
    TrustClaimEvidenceDTO,
    TrustClaimDTO,
    TrustClaimUpdate,
    TrustEvidenceCreate,
    TrustEvidenceDTO,
    TrustEvidenceUpdate,
    TrustVerificationCreate,
    TrustVerificationDTO,
)


class TrustService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = TrustRepository(db)

    @staticmethod
    def _claim_state(claim: TrustClaim) -> dict:
        return {
            "claim_type": claim.claim_type,
            "claim_value": claim.claim_value,
            "verification_status": claim.verification_status,
            "confidence": str(claim.confidence) if claim.confidence is not None else None,
        }

    def _audit(
        self,
        claim: TrustClaim,
        actor: User,
        event_type: str,
        *,
        previous_state: dict | None = None,
        current_state: dict | None = None,
        reason: str | None = None,
        evidence_id: UUID | None = None,
        verification_id: UUID | None = None,
        event_metadata: dict | None = None,
    ) -> None:
        if event_type not in TRUST_AUDIT_EVENTS and event_type != "CLAIM_EXPIRED":
            raise BadRequestError("invalid trust audit event")
        self.db.add(TrustAuditEvent(
            claim=claim,
            evidence_id=evidence_id,
            verification_id=verification_id,
            event_type=event_type,
            actor_user_id=actor.id,
            previous_state=previous_state,
            current_state=current_state,
            reason=reason,
            event_metadata=event_metadata,
        ))

    def _get_claim(self, claim_id: UUID) -> TrustClaim:
        claim = self.repository.get_claim(claim_id)
        if claim is None:
            raise NotFoundError("Trust claim not found")
        return claim

    def _expire_if_due(self, claim: TrustClaim) -> None:
        if claim.verification_status != "VERIFIED" or not claim.verifications:
            return
        latest = max(claim.verifications, key=lambda item: item.verified_at)
        if latest.expires_at and latest.expires_at <= datetime.now(timezone.utc):
            previous_state = self._claim_state(claim)
            claim.verification_status = "EXPIRED"
            claim.updated_by_user_id = latest.verified_by_user_id
            self.db.add(TrustAuditEvent(
                claim=claim,
                event_type="CLAIM_EXPIRED",
                actor_user_id=latest.verified_by_user_id,
                previous_state=previous_state,
                current_state=self._claim_state(claim),
                reason="Verification expiry reached",
                verification_id=latest.id,
            ))
            self.db.commit()
            self.db.refresh(claim)

    def create_claim(self, payload: TrustClaimCreate, actor: User) -> TrustClaimDTO:
        if self.repository.get_product(payload.product_id) is None:
            raise NotFoundError("Product not found")
        claim = TrustClaim(**payload.model_dump(), created_by_user_id=actor.id, updated_by_user_id=actor.id)
        self.db.add(claim)
        self.db.flush()
        self._audit(claim, actor, "CLAIM_CREATED", current_state=self._claim_state(claim))
        self.db.commit()
        return TrustClaimDTO.model_validate(self._get_claim(claim.id))

    def get_claim(self, claim_id: UUID) -> TrustClaimDetailDTO:
        claim = self._get_claim(claim_id)
        self._expire_if_due(claim)
        return TrustClaimDetailDTO.model_validate(self._get_claim(claim_id))

    def list_product_claims(self, product_id: UUID) -> list[TrustClaimDTO]:
        if self.repository.get_product(product_id) is None:
            raise NotFoundError("Product not found")
        claims = self.repository.list_product_claims(product_id)
        for claim in claims:
            self._expire_if_due(claim)
        return [TrustClaimDTO.model_validate(self._get_claim(claim.id)) for claim in claims]

    def update_claim(self, claim_id: UUID, payload: TrustClaimUpdate, actor: User) -> TrustClaimDTO:
        claim = self._get_claim(claim_id)
        if claim.verification_status == "VERIFIED":
            raise BadRequestError("Verified trust claims cannot be edited; create a new verification workflow")
        previous_state = self._claim_state(claim)
        changes = payload.model_dump(exclude_unset=True)
        if not changes:
            raise BadRequestError("No trust claim changes provided")
        for field, value in changes.items():
            setattr(claim, field, value)
        claim.updated_by_user_id = actor.id
        self._audit(claim, actor, "CLAIM_UPDATED", previous_state=previous_state, current_state=self._claim_state(claim))
        self.db.commit()
        return TrustClaimDTO.model_validate(self._get_claim(claim.id))

    def create_evidence(self, payload: TrustEvidenceCreate, actor: User) -> TrustEvidenceDTO:
        evidence = TrustEvidence(**payload.model_dump(), created_by_user_id=actor.id, updated_by_user_id=actor.id)
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return TrustEvidenceDTO.model_validate(evidence)

    def get_evidence(self, evidence_id: UUID) -> TrustEvidenceDTO:
        evidence = self.repository.get_evidence(evidence_id)
        if evidence is None:
            raise NotFoundError("Trust evidence not found")
        return TrustEvidenceDTO.model_validate(evidence)

    def update_evidence(self, evidence_id: UUID, payload: TrustEvidenceUpdate, actor: User) -> TrustEvidenceDTO:
        evidence = self.repository.get_evidence(evidence_id)
        if evidence is None:
            raise NotFoundError("Trust evidence not found")
        changes = payload.model_dump(exclude_unset=True)
        if not changes:
            raise BadRequestError("No trust evidence changes provided")
        if "reference_url" in changes or "storage_reference" in changes:
            reference_url = changes.get("reference_url", evidence.reference_url)
            storage_reference = changes.get("storage_reference", evidence.storage_reference)
            if not reference_url and not storage_reference:
                raise BadRequestError("reference_url or storage_reference is required")
        for field, value in changes.items():
            setattr(evidence, field, value)
        evidence.updated_by_user_id = actor.id
        audit_metadata = {
            field: value.isoformat() if isinstance(value, datetime) else value
            for field, value in changes.items()
        }
        for link in evidence.claim_links:
            self._audit(
                link.claim,
                actor,
                "EVIDENCE_UPDATED",
                evidence_id=evidence.id,
                current_state={"evidence_id": str(evidence.id), "is_active": evidence.is_active},
                event_metadata=audit_metadata,
            )
        self.db.commit()
        self.db.refresh(evidence)
        return TrustEvidenceDTO.model_validate(evidence)

    def attach_evidence(self, claim_id: UUID, payload: TrustClaimEvidenceCreate, actor: User) -> TrustClaimEvidenceDTO:
        claim = self._get_claim(claim_id)
        evidence = self.repository.get_evidence(payload.evidence_id)
        if evidence is None:
            raise NotFoundError("Trust evidence not found")
        if any(link.evidence_id == evidence.id for link in claim.evidence_links):
            raise BadRequestError("Evidence is already attached to this claim")
        link = TrustClaimEvidence(
            claim=claim,
            evidence=evidence,
            assessment_metadata=payload.assessment_metadata,
            attached_by_user_id=actor.id,
        )
        self.db.add(link)
        self.db.flush()
        self._audit(
            claim,
            actor,
            "EVIDENCE_ATTACHED",
            evidence_id=evidence.id,
            current_state={"evidence_id": str(evidence.id)},
            event_metadata=payload.assessment_metadata,
        )
        self.db.commit()
        refreshed = self._get_claim(claim.id)
        return TrustClaimEvidenceDTO.model_validate(next(item for item in refreshed.evidence_links if item.id == link.id))

    def create_verification(self, claim_id: UUID, payload: TrustVerificationCreate, actor: User) -> TrustVerificationDTO:
        claim = self._get_claim(claim_id)
        if payload.verification_status not in TRUST_CLAIM_STATUSES:
            raise BadRequestError("invalid trust verification status")
        if payload.verification_method not in TRUST_VERIFICATION_METHODS:
            raise BadRequestError("invalid trust verification method")
        linked_evidence = {link.evidence_id: link.evidence for link in claim.evidence_links}
        requested_ids = payload.evidence_ids or list(linked_evidence)
        missing = [evidence_id for evidence_id in requested_ids if evidence_id not in linked_evidence]
        if missing:
            raise BadRequestError("Verification evidence must be attached to the trust claim")
        if payload.verification_status == "VERIFIED":
            if not requested_ids:
                raise BadRequestError("Verified trust claims require attached active evidence")
            if any(not linked_evidence[evidence_id].is_active for evidence_id in requested_ids):
                raise BadRequestError("Verified trust claims require active evidence")
        snapshot = [
            {
                "evidence_id": str(evidence.id),
                "evidence_type": evidence.evidence_type,
                "title": evidence.title,
                "source": evidence.source,
                "reference_url": evidence.reference_url,
                "storage_reference": evidence.storage_reference,
                "is_active": evidence.is_active,
            }
            for evidence_id in requested_ids
            for evidence in [linked_evidence[evidence_id]]
        ]
        previous_state = self._claim_state(claim)
        verification = TrustVerification(
            claim=claim,
            verification_status=payload.verification_status,
            verification_method=payload.verification_method,
            notes=payload.notes,
            evidence_snapshot=snapshot,
            verification_metadata=payload.verification_metadata,
            verified_by_user_id=actor.id,
            expires_at=payload.expires_at,
        )
        self.db.add(verification)
        self.db.flush()
        claim.verification_status = payload.verification_status
        expires_immediately = (
            payload.expires_at
            and payload.expires_at <= datetime.now(timezone.utc)
            and payload.verification_status == "VERIFIED"
        )
        if expires_immediately:
            claim.verification_status = "EXPIRED"
        claim.updated_by_user_id = actor.id
        self._audit(
            claim,
            actor,
            "VERIFICATION_CREATED",
            previous_state=previous_state,
            current_state=self._claim_state(claim),
            reason=payload.notes,
            verification_id=verification.id,
            event_metadata={"method": payload.verification_method, "evidence_ids": [str(item) for item in requested_ids]},
        )
        if expires_immediately:
            self._audit(
                claim,
                actor,
                "CLAIM_EXPIRED",
                previous_state={"verification_status": "VERIFIED"},
                current_state=self._claim_state(claim),
                reason="Verification expiry reached",
                verification_id=verification.id,
            )
        self.db.commit()
        self.db.refresh(verification)
        return TrustVerificationDTO.model_validate(verification)

    def verification_history(self, claim_id: UUID) -> list[TrustVerificationDTO]:
        claim = self._get_claim(claim_id)
        self._expire_if_due(claim)
        return [TrustVerificationDTO.model_validate(item) for item in sorted(claim.verifications, key=lambda item: item.verified_at, reverse=True)]

    def audit_history(self, claim_id: UUID):
        claim = self._get_claim(claim_id)
        self._expire_if_due(claim)
        from app.schemas.trust import TrustAuditEventDTO
        return [TrustAuditEventDTO.model_validate(item) for item in sorted(claim.audit_events, key=lambda item: item.created_at, reverse=True)]
