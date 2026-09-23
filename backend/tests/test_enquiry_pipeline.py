from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.entities import LeadStatus, Notification
from app.schemas.enquiry import EnquiryCreate, LeadStatusUpdate
from app.services.enquiry_service import EnquiryService


def enquiry_payload(**overrides):
    values = {
        "buyer_name": "Asha Rao",
        "buyer_phone": "9876543210",
        "source": "INSTAGRAM",
        "source_medium": "social",
        "source_content": "carousel-1",
        "landing_path": "/properties/example?utm_source=instagram",
        "consent_to_share": True,
    }
    values.update(overrides)
    return EnquiryCreate(**values)


def live_property():
    return SimpleNamespace(
        id=uuid4(),
        status="LIVE",
        seller_profile_id=uuid4(),
        title="The Garden House",
        slug="the-garden-house",
        property_type="VILLA",
        location=SimpleNamespace(name="Jayanagar"),
    )


def test_live_enquiry_persists_attribution_and_notifies_seller():
    db = MagicMock()
    prop = live_property()
    db.scalar.side_effect = [prop, None, uuid4()]
    db.query.return_value.filter.return_value.first.return_value = None
    service = EnquiryService(db)

    created = service.create(prop.id, enquiry_payload())
    added = [call.args[0] for call in db.add.call_args_list]
    notification = next(item for item in added if isinstance(item, Notification))

    assert created.property_id == prop.id
    assert created.status == LeadStatus.NEW.value
    assert created.consent_to_share is True
    assert created.consent_at is not None
    assert created.source == "INSTAGRAM"
    assert created.source_medium == "social"
    assert created.source_content == "carousel-1"
    assert notification.user_id is not None
    assert notification.type == "NEW_ENQUIRY"
    assert notification.body == "You received a new enquiry for The Garden House."
    assert notification.related_entity_type == "ENQUIRY"


def test_non_live_property_cannot_receive_public_enquiry():
    db = MagicMock()
    db.scalar.return_value = None

    with pytest.raises(NotFoundError):
        EnquiryService(db).create(uuid4(), enquiry_payload())

    db.add.assert_not_called()


def test_consent_and_required_fields_are_enforced():
    with pytest.raises(ValidationError):
        EnquiryCreate(buyer_name="Buyer", buyer_phone="9876543210")
    with pytest.raises(ValidationError):
        EnquiryCreate(buyer_name="", buyer_phone="9876543210", consent_to_share=True)
    db = MagicMock()
    db.scalar.return_value = live_property()
    with pytest.raises(BadRequestError):
        EnquiryService(db).create(uuid4(), EnquiryCreate(buyer_name="Buyer", buyer_phone="9876543210", consent_to_share=False))


def test_duplicate_enquiry_links_to_previous_enquiry():
    db = MagicMock()
    prop = live_property()
    previous = SimpleNamespace(id=uuid4())
    db.scalar.side_effect = [prop, previous, uuid4()]

    created = EnquiryService(db).create(prop.id, enquiry_payload())

    assert created.duplicate_of_id == previous.id


def test_seller_dto_contains_context_and_hides_contact_without_consent():
    db = MagicMock()
    service = EnquiryService(db)
    enquiry = SimpleNamespace(
        id=uuid4(),
        property_id=uuid4(),
        duplicate_of_id=None,
        property=SimpleNamespace(
            slug="garden-house",
            title="The Garden House",
            property_type="VILLA",
            location=SimpleNamespace(name="Jayanagar"),
        ),
        buyer_name="Asha Rao",
        buyer_phone="9876543210",
        buyer_email="asha@example.com",
        whatsapp_available=True,
        budget_amount=None,
        buying_timeline=None,
        message="Please share the floor plan.",
        preferred_contact_method="PHONE",
        source="WEBSITE",
        source_medium=None,
        source_content=None,
        campaign_id=None,
        landing_path="/properties/garden-house",
        consent_to_share=False,
        status="NEW",
        created_at=datetime.now(timezone.utc),
        status_history=[],
    )

    result = service.to_seller_dto(enquiry)

    assert result.property_type == "VILLA"
    assert result.locality == "Jayanagar"
    assert result.buyer_phone is None
    assert result.buyer_email is None
    assert result.whatsapp_available is False


def test_status_update_records_history_and_rejects_invalid_status():
    db = MagicMock()
    enquiry = SimpleNamespace(id=uuid4(), status="NEW")
    user = SimpleNamespace(id=uuid4(), role="seller")
    db.scalar.return_value = enquiry
    service = EnquiryService(db)

    updated = service.update_status(user, enquiry.id, LeadStatusUpdate(status="CONTACTED", note="Called buyer"))
    history = next(item for item in (call.args[0] for call in db.add.call_args_list) if item.__class__.__name__ == "LeadStatusHistory")

    assert updated.status == "CONTACTED"
    assert history.old_status == "NEW"
    assert history.new_status == "CONTACTED"
    assert history.changed_by == user.id
    assert history.note == "Called buyer"

    with pytest.raises(ValidationError):
        LeadStatusUpdate(status="INVALID")
