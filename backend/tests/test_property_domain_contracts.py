from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.entities import AdminReviewDecision, Location, PropertyStatus, VerificationStatus
from app.schemas.enquiry import EnquiryCreate
from app.schemas.property import AdminReviewRequest, PropertyCreate, PropertyUpdate, VerificationUpdateRequest
from app.services.property_service import _ALLOWED


def test_property_update_is_partial_and_preserves_explicit_zero_values():
    payload = PropertyUpdate(price_amount=Decimal("0.01"), bhk=0)
    assert payload.model_dump(exclude_unset=True) == {"price_amount": Decimal("0.01"), "bhk": 0}


def test_property_create_requires_positive_price_and_valid_visibility():
    with pytest.raises(ValidationError):
        PropertyCreate(
            location_id=uuid4(),
            title="A home",
            description="A description",
            property_type="APARTMENT",
            price_amount=0,
        )

    with pytest.raises(ValidationError):
        PropertyCreate(
            location_id=uuid4(),
            title="A home",
            description="A description",
            property_type="APARTMENT",
            price_amount=100,
            address_visibility="PUBLIC_ADDRESS",
        )


def test_sensitive_admin_and_verification_values_are_enum_bound():
    assert AdminReviewRequest(decision="APPROVED").decision is AdminReviewDecision.APPROVED
    assert VerificationUpdateRequest(verification_status="CONTACT_VERIFIED").verification_status is VerificationStatus.CONTACT_VERIFIED
    with pytest.raises(ValidationError):
        AdminReviewRequest(decision="PUBLISHED")
    with pytest.raises(ValidationError):
        VerificationUpdateRequest(verification_status="VERIFIED")


def test_enquiry_requires_explicit_consent():
    with pytest.raises(ValidationError):
        EnquiryCreate(buyer_name="Buyer", buyer_phone="9876543210")


def test_property_lifecycle_only_allows_approved_transitions():
    assert PropertyStatus.SUBMITTED.value in _ALLOWED[PropertyStatus.DRAFT.value]
    assert PropertyStatus.LIVE.value not in _ALLOWED[PropertyStatus.SUBMITTED.value]
    assert PropertyStatus.APPROVED.value in _ALLOWED[PropertyStatus.UNDER_REVIEW.value]
    assert PropertyStatus.CHANGES_REQUESTED.value in _ALLOWED[PropertyStatus.LIVE.value]


def test_location_has_sibling_identity_constraint():
    names = {constraint.name for constraint in Location.__table__.constraints}
    assert "uq_locations_parent_normalized_name" in names
