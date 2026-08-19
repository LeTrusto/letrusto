from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.trust import TRUST_CLAIM_STATUSES, TRUST_VERIFICATION_METHODS


class TrustClaimCreate(BaseModel):
    product_id: UUID
    claim_type: str = Field(min_length=1, max_length=80)
    claim_value: str = Field(min_length=1, max_length=5000)
    claim_description: str | None = Field(default=None, max_length=10000)
    source: str | None = Field(default=None, max_length=80)
    confidence: Decimal | None = Field(default=None, ge=0, le=100, max_digits=5, decimal_places=2)
    assessment_metadata: dict[str, Any] | None = None


class TrustClaimUpdate(BaseModel):
    claim_type: str | None = Field(default=None, min_length=1, max_length=80)
    claim_value: str | None = Field(default=None, min_length=1, max_length=5000)
    claim_description: str | None = Field(default=None, max_length=10000)
    source: str | None = Field(default=None, max_length=80)
    confidence: Decimal | None = Field(default=None, ge=0, le=100, max_digits=5, decimal_places=2)
    assessment_metadata: dict[str, Any] | None = None


class TrustEvidenceCreate(BaseModel):
    evidence_type: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=240)
    description: str | None = Field(default=None, max_length=10000)
    source: str | None = Field(default=None, max_length=80)
    reference_url: str | None = Field(default=None, max_length=5000)
    storage_reference: str | None = Field(default=None, max_length=5000)
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    evidence_metadata: dict[str, Any] | None = None

    @model_validator(mode="after")
    def require_reference(self):
        if not self.reference_url and not self.storage_reference:
            raise ValueError("reference_url or storage_reference is required")
        return self


class TrustEvidenceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    description: str | None = Field(default=None, max_length=10000)
    source: str | None = Field(default=None, max_length=80)
    reference_url: str | None = Field(default=None, max_length=5000)
    storage_reference: str | None = Field(default=None, max_length=5000)
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    evidence_metadata: dict[str, Any] | None = None
    is_active: bool | None = None


class TrustClaimEvidenceCreate(BaseModel):
    evidence_id: UUID
    assessment_metadata: dict[str, Any] | None = None


class TrustVerificationCreate(BaseModel):
    verification_status: str = Field(min_length=1, max_length=20)
    verification_method: str = Field(min_length=1, max_length=80)
    notes: str | None = Field(default=None, max_length=10000)
    evidence_ids: list[UUID] = Field(default_factory=list, max_length=100)
    verification_metadata: dict[str, Any] | None = None
    expires_at: datetime | None = None

    @field_validator("verification_status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in TRUST_CLAIM_STATUSES:
            raise ValueError("invalid trust verification status")
        return normalized

    @field_validator("verification_method")
    @classmethod
    def validate_method(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in TRUST_VERIFICATION_METHODS:
            raise ValueError("invalid trust verification method")
        return normalized


class TrustEvidenceDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    evidence_type: str
    title: str
    description: str | None
    source: str | None
    reference_url: str | None
    storage_reference: str | None
    issued_at: datetime | None
    expires_at: datetime | None
    evidence_metadata: dict[str, Any] | None
    is_active: bool
    created_by_user_id: UUID | None
    updated_by_user_id: UUID | None
    created_at: datetime
    updated_at: datetime


class TrustClaimEvidenceDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    evidence_id: UUID
    assessment_metadata: dict[str, Any] | None
    attached_by_user_id: UUID | None
    created_at: datetime
    evidence: TrustEvidenceDTO


class TrustVerificationDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    claim_id: UUID
    verification_status: str
    verification_method: str
    notes: str | None
    evidence_snapshot: list[dict[str, Any]] | None
    verification_metadata: dict[str, Any] | None
    verified_by_user_id: UUID | None
    verified_at: datetime
    expires_at: datetime | None


class TrustAuditEventDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    claim_id: UUID
    evidence_id: UUID | None
    verification_id: UUID | None
    event_type: str
    actor_user_id: UUID | None
    previous_state: dict[str, Any] | None
    current_state: dict[str, Any] | None
    reason: str | None
    event_metadata: dict[str, Any] | None
    created_at: datetime


class TrustClaimDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    claim_type: str
    claim_value: str
    claim_description: str | None
    source: str | None
    verification_status: str
    confidence: Decimal | None
    assessment_metadata: dict[str, Any] | None
    created_by_user_id: UUID | None
    updated_by_user_id: UUID | None
    created_at: datetime
    updated_at: datetime
    evidence_links: list[TrustClaimEvidenceDTO] = Field(default_factory=list)


class TrustClaimDetailDTO(TrustClaimDTO):
    verifications: list[TrustVerificationDTO] = Field(default_factory=list)
    audit_events: list[TrustAuditEventDTO] = Field(default_factory=list)
