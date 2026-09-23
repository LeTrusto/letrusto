from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from app.api.v1.endpoints.admin_properties import dashboard


def _scalars(items):
    result = MagicMock()
    result.unique.return_value.all.return_value = items
    result.all.return_value = items
    return result


def test_admin_dashboard_summary_uses_operational_counts_and_queues():
    db = MagicMock()
    db.scalar.side_effect = [7, 4, 2, 3, 1, 4, 2, 5, 3, 2, 1]
    review_property = SimpleNamespace(id=uuid4(), title="Review home", status="SUBMITTED", location=SimpleNamespace(name="Jayanagar"))
    change_property = SimpleNamespace(id=uuid4(), title="Change home", status="CHANGES_REQUESTED", location=SimpleNamespace(name="HSR Layout"))
    campaign = SimpleNamespace(id=uuid4(), campaign_title="Launch campaign", property_id=uuid4(), property=SimpleNamespace(title="Live home"))
    enquiry = SimpleNamespace(
        id=uuid4(), property_id=uuid4(), property=SimpleNamespace(title="Live home", seller_profile=SimpleNamespace(display_name="Seller")),
        buyer_name="Buyer", buyer_phone="9876543210", buyer_email=None, whatsapp_available=False, budget_amount=None,
        buying_timeline=None, message=None, preferred_contact_method="PHONE", source="WEBSITE", status="NEW",
        consent_to_share=True, created_at=datetime.now(timezone.utc),
    )
    db.scalars.side_effect = [_scalars([enquiry]), _scalars([review_property]), _scalars([change_property]), _scalars([campaign])]

    result = dashboard(SimpleNamespace(role="admin"), db)

    assert result.properties == {"draft": 2, "submitted": 3, "under_review": 1, "live": 4, "changes_requested": 2}
    assert result.leads == {"new": 5, "contacted": 3, "follow_up": 2, "visited": 1}
    assert result.sellers == {"active": 7}
    assert result.campaigns == {"active": 4}
    assert result.attention["review"][0]["title"] == "Review home"
    assert result.attention["changes_requested"][0]["title"] == "Change home"
    assert result.attention["campaigns"][0]["title"] == "Launch campaign"