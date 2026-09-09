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


def test_pending_subscription_without_period_end_does_not_grant_paid_access():
    user = SimpleNamespace(trial_ends_at=None, id="user-id")
    subscription = SimpleNamespace(
        user_id="user-id",
        plan_name="starter",
        status="pending",
        current_period_end=None,
        grace_until=None,
    )
    db = MagicMock()
    db.scalar.return_value = subscription

    entitlement = get_entitlement(db, user)

    assert entitlement.active is True
    assert entitlement.plan == "free"
    assert entitlement.status == "free"


def test_trialing_pro_subscription_uses_pro_trial_entitlement():
    user = SimpleNamespace(trial_ends_at=datetime.now(timezone.utc) + timedelta(days=14), id="user-id")
    subscription = SimpleNamespace(
        user_id="user-id",
        plan_name="pro",
        status="trialing",
        current_period_end=None,
        grace_until=None,
    )
    db = MagicMock()
    db.scalar.return_value = subscription

    entitlement = get_entitlement(db, user)

    assert entitlement.active is True
    assert entitlement.plan == "pro"
    assert entitlement.status == "trialing"
    assert entitlement.is_trial is True
    assert entitlement.max_widgets is None
    assert entitlement.monthly_view_limit is None
    assert "video_reviews" in entitlement.features


def test_cancellation_pending_without_period_end_does_not_grant_indefinite_access():
    user = SimpleNamespace(trial_ends_at=None, id="user-id")
    subscription = SimpleNamespace(
        user_id="user-id",
        plan_name="pro",
        status="cancellation_pending",
        current_period_end=None,
        grace_until=None,
    )
    db = MagicMock()
    db.scalar.return_value = subscription

    entitlement = get_entitlement(db, user)

    assert entitlement.plan == "free"
    assert entitlement.status == "free"


def test_active_paid_subscription_with_future_period_end_keeps_access():
    user = SimpleNamespace(trial_ends_at=datetime.now(timezone.utc) - timedelta(days=1), id="user-id")
    subscription = SimpleNamespace(
        user_id="user-id",
        plan_name="pro",
        status="active",
        current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
        grace_until=None,
    )
    db = MagicMock()
    db.scalar.return_value = subscription

    entitlement = get_entitlement(db, user)

    assert entitlement.active is True
    assert entitlement.plan == "pro"
    assert entitlement.status == "active"
    assert entitlement.is_trial is False


def test_halted_subscription_does_not_fall_back_to_paid_trial_access():
    user = SimpleNamespace(trial_ends_at=datetime.now(timezone.utc) + timedelta(days=7), id="user-id")
    subscription = SimpleNamespace(
        user_id="user-id",
        plan_name="pro",
        status="failed",
        current_period_end=None,
        grace_until=None,
    )
    db = MagicMock()
    db.scalar.return_value = subscription

    entitlement = get_entitlement(db, user)

    assert entitlement.plan == "free"
    assert entitlement.active is True
    assert entitlement.is_trial is False


def test_cancelled_subscription_keeps_access_until_current_period_end():
    user = SimpleNamespace(trial_ends_at=None, id="user-id")
    subscription = SimpleNamespace(
        user_id="user-id",
        plan_name="starter",
        status="cancelled",
        current_period_end=datetime.now(timezone.utc) + timedelta(days=7),
        grace_until=None,
    )
    db = MagicMock()
    db.scalar.return_value = subscription

    entitlement = get_entitlement(db, user)

    assert entitlement.plan == "starter"
    assert entitlement.active is True
    assert entitlement.status == "cancelled"