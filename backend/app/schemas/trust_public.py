from datetime import datetime

from pydantic import BaseModel


class PublicTrustEvidenceSummary(BaseModel):
    evidence_type: str
    title: str
    description: str | None


class PublicTrustClaimDTO(BaseModel):
    claim_type: str
    claim_value: str
    status: str
    verified_at: datetime | None
    verification_method: str | None
    evidence_summary: list[PublicTrustEvidenceSummary]


class PublicTrustScoreDimensionDTO(BaseModel):
    points: float
    maximum: float
    ratio: float


class PublicTrustScoreDTO(BaseModel):
    score: int
    label: str
    data_sufficiency: str
    dimensions: dict[str, PublicTrustScoreDimensionDTO]
    reason_codes: list[str]


class PublicTrustResponse(BaseModel):
    product_id: str
    claims: list[PublicTrustClaimDTO]
    trust_score: PublicTrustScoreDTO