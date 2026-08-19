from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from app.core.exceptions import NotFoundError
from app.core.trust_score_policy import (
    EVIDENCE_STRENGTH_UNKNOWN,
    REASON_CODES,
    TRUST_SCORE_POLICY,
    VERIFICATION_QUALITY_UNKNOWN,
)
from app.models.entities import TrustClaim, TrustEvidence, TrustVerification
from app.repositories.trust_repository import TrustRepository


@dataclass(frozen=True)
class TrustScoreDimension:
    points: Decimal
    maximum: Decimal
    ratio: Decimal


@dataclass(frozen=True)
class TrustScoreResult:
    score: int
    label: str
    policy_version: str
    data_sufficiency: str
    dimensions: dict[str, TrustScoreDimension]
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class _SupportedClaim:
    claim: TrustClaim
    verification: TrustVerification
    evidence: tuple[TrustEvidence, ...]
    freshness: Decimal
    strength: Decimal
    quality: Decimal


class TrustScoreService:
    def __init__(self, db) -> None:
        self.repository = TrustRepository(db)

    def calculate_product_score(
        self,
        product_id: UUID,
        reference_time: datetime | None = None,
    ) -> TrustScoreResult:
        if self.repository.get_product(product_id) is None:
            raise NotFoundError("Product not found")
        return self.calculate_claims(self.repository.list_product_claims(product_id), reference_time=reference_time)

    def calculate_claims(
        self,
        claims: list[TrustClaim],
        *,
        reference_time: datetime | None = None,
    ) -> TrustScoreResult:
        reference = self._utc(reference_time or datetime.now(timezone.utc))
        applicable_claims = [claim for claim in claims if claim.verification_status != "REJECTED"]
        supported_claims = [
            supported
            for claim in applicable_claims
            if (supported := self._supported_claim(claim, reference)) is not None
        ]

        coverage_ratio = self._ratio(len(supported_claims), len(applicable_claims))
        strength_ratio = self._average([item.strength for item in supported_claims])
        freshness_ratio = self._average([item.freshness for item in supported_claims])
        quality_ratio = self._average([item.quality for item in supported_claims])

        dimensions = {
            "evidence_coverage": self._dimension(coverage_ratio, TRUST_SCORE_POLICY.coverage_weight),
            "evidence_strength": self._dimension(strength_ratio, TRUST_SCORE_POLICY.strength_weight),
            "verification_freshness": self._dimension(freshness_ratio, TRUST_SCORE_POLICY.freshness_weight),
            "verification_quality": self._dimension(quality_ratio, TRUST_SCORE_POLICY.quality_weight),
        }
        total = sum((dimension.points for dimension in dimensions.values()), Decimal("0"))
        score = int(total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        score = max(0, min(100, score))
        return TrustScoreResult(
            score=score,
            label=self._score_label(score),
            policy_version=TRUST_SCORE_POLICY.version,
            data_sufficiency=self._data_sufficiency(len(supported_claims), coverage_ratio),
            dimensions=dimensions,
            reason_codes=self._reason_codes(claims, supported_claims, coverage_ratio, strength_ratio, freshness_ratio, reference),
        )

    @staticmethod
    def _utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _ratio(numerator: int, denominator: int) -> Decimal:
        if denominator == 0:
            return Decimal("0")
        return Decimal(numerator) / Decimal(denominator)

    @staticmethod
    def _average(values: list[Decimal]) -> Decimal:
        if not values:
            return Decimal("0")
        return sum(values, Decimal("0")) / Decimal(len(values))

    @staticmethod
    def _dimension(ratio: Decimal, maximum: Decimal) -> TrustScoreDimension:
        bounded_ratio = max(Decimal("0"), min(Decimal("1"), ratio))
        return TrustScoreDimension(points=bounded_ratio * maximum, maximum=maximum, ratio=bounded_ratio)

    @staticmethod
    def _latest_verification(claim: TrustClaim) -> TrustVerification | None:
        return max(claim.verifications, key=lambda item: (item.verified_at, str(item.id)), default=None)

    def _supported_claim(self, claim: TrustClaim, reference: datetime) -> _SupportedClaim | None:
        if claim.verification_status != "VERIFIED":
            return None
        verification = self._latest_verification(claim)
        if verification is None or verification.verification_status != "VERIFIED":
            return None
        if verification.expires_at and self._utc(verification.expires_at) <= reference:
            return None

        referenced_ids = {
            str(item.get("evidence_id"))
            for item in (verification.evidence_snapshot or [])
            if item.get("evidence_id")
        }
        evidence_by_id = {
            str(link.evidence_id): link.evidence
            for link in claim.evidence_links
            if link.evidence is not None
        }
        active_evidence = tuple(
            evidence_by_id[evidence_id]
            for evidence_id in sorted(referenced_ids)
            if evidence_id in evidence_by_id and evidence_by_id[evidence_id].is_active
        )
        if not active_evidence:
            return None

        age_days = max(Decimal("0"), Decimal(str((reference - self._utc(verification.verified_at)).total_seconds())) / Decimal("86400"))
        freshness = max(Decimal("0"), Decimal("1") - age_days / TRUST_SCORE_POLICY.freshness_period_days)
        strength = max(
            (TRUST_SCORE_POLICY.evidence_strength.get(item.evidence_type, EVIDENCE_STRENGTH_UNKNOWN) for item in active_evidence),
            default=EVIDENCE_STRENGTH_UNKNOWN,
        )
        quality = TRUST_SCORE_POLICY.verification_quality.get(verification.verification_method, VERIFICATION_QUALITY_UNKNOWN)
        return _SupportedClaim(claim, verification, active_evidence, freshness, strength, quality)

    @staticmethod
    def _score_label(score: int) -> str:
        for threshold, label in TRUST_SCORE_POLICY.score_labels:
            if score >= threshold:
                return label
        return TRUST_SCORE_POLICY.score_labels[-1][1]

    @staticmethod
    def _data_sufficiency(supported_count: int, coverage: Decimal) -> str:
        if supported_count == 0:
            return "NONE"
        if supported_count >= TRUST_SCORE_POLICY.sufficiency_strong_supported_claims and coverage >= TRUST_SCORE_POLICY.sufficiency_strong_coverage:
            return "STRONG"
        if supported_count >= TRUST_SCORE_POLICY.sufficiency_min_supported_claims and coverage >= TRUST_SCORE_POLICY.sufficiency_adequate_coverage:
            return "ADEQUATE"
        return "LIMITED"

    @staticmethod
    def _reason_codes(
        claims: list[TrustClaim],
        supported: list[_SupportedClaim],
        coverage: Decimal,
        strength: Decimal,
        freshness: Decimal,
        reference: datetime,
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        if not supported:
            reasons.append("NO_TRUST_DATA")
        else:
            reasons.append("STRONG_EVIDENCE_COVERAGE" if coverage >= Decimal("0.75") else "PARTIAL_EVIDENCE_COVERAGE")
            reasons.append("STRONG_SUPPORTING_EVIDENCE" if strength >= Decimal("0.75") else "LIMITED_SUPPORTING_EVIDENCE")
            reasons.append("RECENT_VERIFICATION" if freshness >= Decimal("0.75") else "AGING_VERIFICATION")
            if len(supported) >= 2:
                reasons.append("MULTIPLE_VERIFIED_CLAIMS")
        expired_current_verification = any(
            claim.verification_status == "EXPIRED"
            or (
                (latest := TrustScoreService._latest_verification(claim)) is not None
                and latest.expires_at is not None
                and TrustScoreService._utc(latest.expires_at) <= reference
            )
            for claim in claims
        )
        if expired_current_verification:
            reasons.append("EXPIRED_VERIFICATION")
        return tuple(reason for reason in reasons if reason in REASON_CODES)
