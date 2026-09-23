from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.api.v1.endpoints.public_properties import public_dto
from app.models.entities import VerificationStatus
from app.schemas.property import public_verification


def test_public_verification_maps_each_operational_status_without_private_fields():
    for status, expected_label in {
        VerificationStatus.NOT_REVIEWED.value: "Verification not yet reviewed",
        VerificationStatus.CONTACT_VERIFIED.value: "Contact verified",
        VerificationStatus.RELATIONSHIP_REVIEWED.value: "Seller/property relationship reviewed",
        VerificationStatus.DOCUMENT_EVIDENCE_REVIEWED.value: "Document evidence reviewed",
        VerificationStatus.EXPIRED.value: "Verification requires re-review",
    }.items():
        result = public_verification(status, datetime.now(timezone.utc))
        assert result.status.value == status
        assert result.label == expected_label


def test_public_property_verification_excludes_admin_fields():
    verified_at = datetime.now(timezone.utc)
    prop = SimpleNamespace(
        id=uuid4(), slug="garden-home", title="Garden Home", description="A home.", property_type="VILLA",
        price_amount=100, currency="INR", built_up_area_sqft=None, carpet_area_sqft=None, plot_area_sqft=None,
        bhk=None, floor_number=None, total_floors=None, facing=None, parking_details=None, maintenance_amount=None,
        possession_status=None, plot_dimensions=None, corner_site=None, address_visibility="LOCALITY_ONLY",
        status="LIVE", published_at=None, location=SimpleNamespace(id=uuid4(), name="Jayanagar", slug="jayanagar", location_type="LOCALITY", parent_id=None, city_name="Bengaluru"),
        media=[], verification=SimpleNamespace(verification_status="CONTACT_VERIFIED", verified_at=verified_at, notes="private", verified_by=uuid4(), verification_method="CONTACT", expires_at=None),
    )

    result = public_dto(prop)
    payload = result.model_dump()

    assert payload["verification"]["label"] == "Contact verified"
    assert payload["verification"]["checks"] == {"contact_verified": True, "relationship_reviewed": False, "document_evidence_reviewed": False}
    assert payload["verification"]["reviewed_at"] == verified_at
    assert "notes" not in payload["verification"]
    assert "verified_by" not in payload["verification"]
    assert "verification_method" not in payload["verification"]
    assert "expires_at" not in payload["verification"]


def test_unknown_public_verification_state_fails_safe_to_not_reviewed():
    result = public_verification("UNKNOWN")
    assert result.status is VerificationStatus.NOT_REVIEWED
    assert not any(result.checks.model_dump().values())
