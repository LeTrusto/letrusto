from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import BadRequestError
from app.db.session import SessionLocal
from app.models.entities import MarketingSpend, Order, OrderMarketingAttribution, User
from app.schemas.marketing import AttributionCreate, MarketingSpendCreate
from app.services.marketing_service import MarketingService


def test_marketing_spend_crud_and_cac_modes():
    db = SessionLocal()
    suffix = uuid4().hex[:8]
    user = User(email=f"marketing-{suffix}@example.com", full_name="Marketing Test")
    db.add(user)
    db.commit()
    try:
        service = MarketingService(db)
        spend = service.create_spend(MarketingSpendCreate(spend_date=datetime.now(timezone.utc).date(), channel="META", campaign="Hair", spend_amount=Decimal("15000"), currency="INR"))
        assert spend.spend_amount == Decimal("15000.00")
        start, end = service.periods("today")
        no_attr = service.cac(start, end)
        assert no_attr.blended_cac is None
        assert no_attr.actual_cac_status == "NOT_CONFIGURED"
        service.delete_spend(spend.id)
        assert db.query(MarketingSpend).filter(MarketingSpend.id == spend.id).count() == 0
    finally:
        db.delete(user)
        db.commit()
        db.close()


def test_negative_spend_rejected():
    with pytest.raises(Exception):
        MarketingSpendCreate(spend_date=datetime.now(timezone.utc).date(), channel="META", spend_amount=Decimal("-1"))


def test_attribution_rejects_unknown_order():
    db = SessionLocal()
    try:
        with pytest.raises(Exception):
            MarketingService(db).attribute(AttributionCreate(order_id=uuid4(), channel="META", attribution_method="admin"))
    finally:
        db.close()


def test_target_cac_is_not_actual_cac():
    db = SessionLocal()
    try:
        start, end = MarketingService.periods("today")
        report = MarketingService(db).cac(start, end)
        assert report.target_cac == Decimal("150.00")
        assert report.attributed_cac is None
        assert report.blended_cac is None
    finally:
        db.close()
