from dataclasses import dataclass
from decimal import Decimal
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class TrustScorePolicy:
    version: str
    coverage_weight: Decimal
    strength_weight: Decimal
    freshness_weight: Decimal
    quality_weight: Decimal
    freshness_period_days: Decimal
    evidence_strength: Mapping[str, Decimal]
    verification_quality: Mapping[str, Decimal]
    sufficiency_min_supported_claims: int
    sufficiency_adequate_coverage: Decimal
    sufficiency_strong_supported_claims: int
    sufficiency_strong_coverage: Decimal
    score_labels: tuple[tuple[int, str], ...]


TRUST_SCORE_POLICY = TrustScorePolicy(
    version="v1",
    coverage_weight=Decimal("30"),
    strength_weight=Decimal("30"),
    freshness_weight=Decimal("20"),
    quality_weight=Decimal("20"),
    freshness_period_days=Decimal("365"),
    evidence_strength=MappingProxyType({
        "TEST_REPORT": Decimal("1.00"),
        "CERTIFICATION": Decimal("0.95"),
        "MANUFACTURER_DOCUMENT": Decimal("0.90"),
        "SUPPLIER_DOCUMENT": Decimal("0.70"),
        "INTERNAL_REVIEW": Decimal("0.60"),
        "SYSTEM_REVIEW": Decimal("0.60"),
        "CUSTOMER_FEEDBACK": Decimal("0.45"),
        "OTHER": Decimal("0.30"),
    }),
    verification_quality=MappingProxyType({
        "TEST_REPORT": Decimal("0.95"),
        "CERTIFICATION": Decimal("0.95"),
        "MANUFACTURER_DOCUMENT": Decimal("0.90"),
        "SUPPLIER_DOCUMENT": Decimal("0.75"),
        "INTERNAL_REVIEW": Decimal("0.70"),
        "SYSTEM_REVIEW": Decimal("0.65"),
        "CUSTOMER_FEEDBACK": Decimal("0.50"),
        "OTHER": Decimal("0.40"),
    }),
    sufficiency_min_supported_claims=2,
    sufficiency_adequate_coverage=Decimal("0.50"),
    sufficiency_strong_supported_claims=3,
    sufficiency_strong_coverage=Decimal("0.75"),
    score_labels=(
        (90, "Very strong evidence"),
        (75, "Strong evidence"),
        (50, "Moderate evidence"),
        (25, "Limited evidence"),
        (0, "Insufficient evidence"),
    ),
)

EVIDENCE_STRENGTH_UNKNOWN = Decimal("0.30")
VERIFICATION_QUALITY_UNKNOWN = Decimal("0.40")

REASON_CODES = (
    "NO_TRUST_DATA",
    "PARTIAL_EVIDENCE_COVERAGE",
    "STRONG_EVIDENCE_COVERAGE",
    "STRONG_SUPPORTING_EVIDENCE",
    "LIMITED_SUPPORTING_EVIDENCE",
    "RECENT_VERIFICATION",
    "AGING_VERIFICATION",
    "EXPIRED_VERIFICATION",
    "MULTIPLE_VERIFIED_CLAIMS",
)
