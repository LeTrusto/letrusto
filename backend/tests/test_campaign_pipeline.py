from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import BadRequestError
from app.schemas.campaign import CampaignCreate
from app.services.campaign_service import CampaignService, generate_posts


def property_fixture(status="LIVE"):
    return SimpleNamespace(
        id=uuid4(),
        status=status,
        title="Garden House",
        slug="garden-house-jayanagar",
        price_amount=18500000,
        bhk=3,
        built_up_area_sqft=2100,
        location=SimpleNamespace(name="Jayanagar", city_name="Bengaluru"),
        media=[],
    )


def test_generated_content_uses_public_property_data_and_campaign_key():
    posts = generate_posts(property_fixture(), "INSTAGRAM", "social", "property-reel")
    assert len(posts) == 4
    assert all("Garden House" in post.body for post in posts)
    assert all("Jayanagar" in post.body for post in posts)
    assert all("18500000" not in post.body for post in posts)
    assert any(post.platform == "WHATSAPP" for post in posts)


def test_non_live_campaign_is_rejected():
    db = MagicMock()
    db.scalar.return_value = property_fixture(status="DRAFT")
    payload = CampaignCreate(campaign_title="Launch", campaign_key="garden-launch", source="INSTAGRAM", medium="social")
    with pytest.raises(BadRequestError, match="LIVE"):
        CampaignService(db).create(uuid4(), uuid4(), payload)


def test_invalid_channel_and_status_are_rejected():
    service = CampaignService(MagicMock())
    with pytest.raises(BadRequestError):
        service._validate("TIKTOK", "DRAFT")
    with pytest.raises(BadRequestError):
        service._validate("INSTAGRAM", "PUBLISHED")


def test_campaign_payload_rejects_invalid_key():
    with pytest.raises(ValueError):
        CampaignCreate(campaign_title="Launch", campaign_key="Garden Launch", source="INSTAGRAM", medium="social")
