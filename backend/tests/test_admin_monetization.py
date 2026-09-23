from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from app.api.v1.endpoints.admin_monetization import list_plans, update_plan
from app.schemas.admin import MonetizationPlanUpdate


def test_admin_can_list_plan_configuration():
    plan = SimpleNamespace(code="FREE")
    db = MagicMock()
    db.scalars.return_value.all.return_value = [plan]

    assert list_plans(SimpleNamespace(role="admin"), db) == [plan]


def test_plan_update_cannot_enable_customer_purchases():
    plan = SimpleNamespace(id=uuid4(), code="PREMIUM", customer_purchase_enabled=False)
    db = MagicMock()
    db.scalar.return_value = plan

    result = update_plan(
        "premium",
        MonetizationPlanUpdate(is_active=True),
        SimpleNamespace(role="admin"),
        db,
    )

    assert result is plan
    assert plan.is_active is True
    assert plan.customer_purchase_enabled is False
    db.commit.assert_called_once_with()