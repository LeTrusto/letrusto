from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.entitlement_service import get_entitlement


def test_active_trial_has_starter_access():
    user = SimpleNamespace(trial_ends_at=datetime.now(timezone.utc) + timedelta(days=1), id="user-id")
    db = MagicMock()
    db.scalar.return_value = None

    entitlement = get_entitlement(db, user)

    assert entitlement.active is True
    assert entitlement.plan == "starter"
    assert entitlement.status == "trialing"
    assert entitlement.is_trial is True


def test_expired_trial_has_no_service_access():
    user = SimpleNamespace(trial_ends_at=datetime.now(timezone.utc) - timedelta(seconds=1), id="user-id")
    db = MagicMock()
    db.scalar.return_value = None

    entitlement = get_entitlement(db, user)

    assert entitlement.active is False
    assert entitlement.plan == "expired"
    assert entitlement.status == "trial_expired"
    assert entitlement.max_widgets == 0
    assert entitlement.monthly_view_limit == 0
    assert entitlement.features == frozenset()