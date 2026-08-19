from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services.trust_score_service import TrustScoreService


REFERENCE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def evidence(evidence_type="SUPPLIER_DOCUMENT", active=True, evidence_id=None):
    return SimpleNamespace(id=evidence_id or uuid4(), evidence_type=evidence_type, is_active=active)


def verification(status="VERIFIED", method="SUPPLIER_DOCUMENT", verified_at=REFERENCE, expires_at=None, evidence_items=None):
    items = evidence_items or [evidence()]
    return SimpleNamespace(
        id=uuid4(),
        verification_status=status,
        verification_method=method,
        verified_at=verified_at,
        expires_at=expires_at,
        evidence_snapshot=[{"evidence_id": str(item.id), "evidence_type": item.evidence_type, "title": item.evidence_type} for item in items],
    )


def claim(status="VERIFIED", verifications=None, evidence_items=None, claim_type="MATERIAL"):
    items = evidence_items or [evidence()]
    return SimpleNamespace(
        id=uuid4(),
        claim_type=claim_type,
        verification_status=status,
        verifications=verifications or [verification(evidence_items=items)],
        evidence_links=[SimpleNamespace(evidence_id=item.id, evidence=item) for item in items],
    )


def score(claims):
    return TrustScoreService(None).calculate_claims(claims, reference_time=REFERENCE)


def test_no_claims_is_zero_and_insufficient():
    result = score([])
    assert result.score == 0
    assert result.data_sufficiency == "NONE"
    assert result.label == "Insufficient evidence"
    assert result.reason_codes == ("NO_TRUST_DATA",)


def test_one_verified_supplier_claim_calculates_all_dimensions():
    result = score([claim()])
    assert result.score == 86
    assert result.dimensions["evidence_coverage"].points == Decimal("30")
    assert result.dimensions["evidence_strength"].points == Decimal("21.00")
    assert result.dimensions["verification_freshness"].points == Decimal("20")
    assert result.dimensions["verification_quality"].points == Decimal("15.00")
    assert result.data_sufficiency == "LIMITED"
    assert result.policy_version == "v1"


def test_rejected_excluded_but_expired_remains_in_coverage_denominator():
    expired = claim(status="EXPIRED", verifications=[verification(expires_at=REFERENCE - timedelta(days=1))])
    rejected = claim(status="REJECTED")
    supported = claim()
    result = score([expired, rejected, supported])
    assert result.dimensions["evidence_coverage"].ratio == Decimal("0.5")
    assert result.data_sufficiency == "LIMITED"
    assert "EXPIRED_VERIFICATION" in result.reason_codes


@pytest.mark.parametrize("status", ["PENDING", "UNVERIFIED", "REJECTED", "EXPIRED"])
def test_non_verified_statuses_do_not_contribute(status):
    result = score([claim(status=status)])
    assert result.score == 0
    assert result.data_sufficiency == "NONE"


def test_verified_claim_without_active_evidence_does_not_contribute():
    inactive = evidence(active=False)
    result = score([claim(evidence_items=[inactive])])
    assert result.score == 0
    assert result.data_sufficiency == "NONE"


def test_strongest_unique_active_evidence_is_used_once():
    duplicate_id = uuid4()
    supplier_one = evidence("SUPPLIER_DOCUMENT", evidence_id=duplicate_id)
    supplier_duplicate = evidence("SUPPLIER_DOCUMENT", evidence_id=duplicate_id)
    report = evidence("TEST_REPORT")
    result = score([claim(evidence_items=[supplier_one, supplier_duplicate, report])])
    assert result.dimensions["evidence_strength"].ratio == Decimal("1.00")


def test_unknown_evidence_and_verification_methods_use_approved_defaults():
    unknown = evidence("FUTURE_DOCUMENT")
    result = score([claim(evidence_items=[unknown], verifications=[verification(method="FUTURE_METHOD", evidence_items=[unknown])])])
    assert result.dimensions["evidence_strength"].ratio == Decimal("0.30")
    assert result.dimensions["verification_quality"].ratio == Decimal("0.40")


@pytest.mark.parametrize(
    ("evidence_type", "expected"),
    [
        ("TEST_REPORT", Decimal("1.00")),
        ("CERTIFICATION", Decimal("0.95")),
        ("MANUFACTURER_DOCUMENT", Decimal("0.90")),
        ("SUPPLIER_DOCUMENT", Decimal("0.70")),
        ("INTERNAL_REVIEW", Decimal("0.60")),
        ("SYSTEM_REVIEW", Decimal("0.60")),
        ("CUSTOMER_FEEDBACK", Decimal("0.45")),
        ("OTHER", Decimal("0.30")),
    ],
)
def test_evidence_strength_mapping(evidence_type, expected):
    item = evidence(evidence_type)
    result = score([claim(evidence_items=[item], verifications=[verification(evidence_items=[item])])])
    assert result.dimensions["evidence_strength"].ratio == expected


@pytest.mark.parametrize(
    ("method", "expected"),
    [
        ("TEST_REPORT", Decimal("0.95")),
        ("CERTIFICATION", Decimal("0.95")),
        ("MANUFACTURER_DOCUMENT", Decimal("0.90")),
        ("SUPPLIER_DOCUMENT", Decimal("0.75")),
        ("INTERNAL_REVIEW", Decimal("0.70")),
        ("SYSTEM_REVIEW", Decimal("0.65")),
        ("CUSTOMER_FEEDBACK", Decimal("0.50")),
        ("OTHER", Decimal("0.40")),
    ],
)
def test_verification_quality_mapping(method, expected):
    item = evidence()
    result = score([claim(evidence_items=[item], verifications=[verification(method=method, evidence_items=[item])])])
    assert result.dimensions["verification_quality"].ratio == expected


@pytest.mark.parametrize(
    ("age", "expected"),
    [(0, Decimal("1")), (180, Decimal("185") / Decimal("365")), (365, Decimal("0")), (400, Decimal("0"))],
)
def test_freshness_formula(age, expected):
    item = evidence()
    result = score([claim(evidence_items=[item], verifications=[verification(verified_at=REFERENCE - timedelta(days=age), evidence_items=[item])])])
    assert result.dimensions["verification_freshness"].ratio == expected


def test_expired_verification_has_zero_freshness_and_no_support():
    result = score([claim(verifications=[verification(expires_at=REFERENCE)])])
    assert result.score == 0
    assert result.dimensions["verification_freshness"].ratio == Decimal("0")
    assert "EXPIRED_VERIFICATION" in result.reason_codes


def test_latest_historical_verification_controls_current_contribution():
    item = evidence()
    earlier = verification(verified_at=REFERENCE - timedelta(days=10), evidence_items=[item])
    later = verification(status="REJECTED", verified_at=REFERENCE, evidence_items=[item])
    result = score([claim(verifications=[earlier, later], evidence_items=[item])])
    assert result.score == 0


def test_multiple_supported_claims_can_be_strong():
    result = score([claim(claim_type="MATERIAL"), claim(claim_type="DIMENSIONS"), claim(claim_type="ORIGIN")])
    assert result.data_sufficiency == "STRONG"
    assert result.dimensions["evidence_coverage"].ratio == Decimal("1")
    assert "MULTIPLE_VERIFIED_CLAIMS" in result.reason_codes


def test_final_score_rounds_and_is_bounded():
    result = score([claim(verifications=[verification(method="CUSTOMER_FEEDBACK")])])
    assert 0 <= result.score <= 100
    assert result.score == round(float(result.dimensions["evidence_coverage"].points + result.dimensions["evidence_strength"].points + result.dimensions["verification_freshness"].points + result.dimensions["verification_quality"].points))


def test_same_data_and_reference_are_deterministic():
    item = evidence("TEST_REPORT")
    current = claim(evidence_items=[item])
    first = score([current])
    second = score([current])
    assert first == second
