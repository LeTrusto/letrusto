import hashlib
import hmac
import json
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.config import Settings
from app.services.subscription_service import SubscriptionService


def _webhook(event_name: str) -> tuple[bytes, str]:
    body = json.dumps(
        {
            "id": f"evt_{event_name.replace('.', '_')}",
            "event": event_name,
            "payload": {
                "subscription": {
                    "entity": {
                        "id": "sub_test_123",
                        "current_end": int(datetime.now(timezone.utc).timestamp()) + 86400,
                        "notes": {"letrusto_user_id": "user-id"},
                    }
                }
            },
        }
    ).encode()
    signature = hmac.new(b"webhook-secret", body, hashlib.sha256).hexdigest()
    return body, signature


def test_existing_trialing_subscription_is_reused_for_checkout():
    existing = SimpleNamespace(
        razorpay_subscription_id="sub_existing_trialing",
        plan_name="pro",
        status="trialing",
    )
    db = MagicMock()
    db.scalar.return_value = existing
    service = SubscriptionService(
        db,
        Settings(
            RAZORPAY_KEY_ID="rzp_test_checkout",
            RAZORPAY_KEY_SECRET="test-secret",
            RAZORPAY_PRO_PLAN_ID="plan_pro",
        ),
    )
    service._client = MagicMock()  # type: ignore[method-assign]

    response = service.create_subscription(SimpleNamespace(id="user-id"), "pro")

    assert response.subscription_id == "sub_existing_trialing"
    assert response.status == "trialing"
    service._client.assert_not_called()
    db.commit.assert_not_called()


@pytest.mark.parametrize(
    ("event_name", "expected_status"),
    [
        ("subscription.authenticated", "trialing"),
        ("subscription.activated", "active"),
        ("subscription.charged", "active"),
    ],
)
def test_subscription_lifecycle_events_update_state(event_name, expected_status):
    record = SimpleNamespace(
        razorpay_subscription_id="sub_test_123",
        status="created",
        current_period_end=None,
        cancelled_at=None,
        failed_at=None,
        failure_reason=None,
    )
    db = MagicMock()
    db.scalar.side_effect = [None, record]
    body, signature = _webhook(event_name)

    SubscriptionService(db, Settings(RAZORPAY_WEBHOOK_SECRET="webhook-secret")).process_webhook(body, signature)

    assert record.status == expected_status
    assert record.current_period_end is not None
    db.commit.assert_called_once()


def test_duplicate_subscription_webhook_is_ignored_without_second_commit():
    record = SimpleNamespace(
        razorpay_subscription_id="sub_test_123",
        status="active",
        current_period_end=None,
        cancelled_at=None,
        failed_at=None,
        failure_reason=None,
    )
    event = SimpleNamespace(provider_event_id="evt_subscription_charged", event_name="subscription.charged")
    db = MagicMock()
    db.scalar.side_effect = [None, record, event]
    body, signature = _webhook("subscription.charged")
    service = SubscriptionService(db, Settings(RAZORPAY_WEBHOOK_SECRET="webhook-secret"))

    service.process_webhook(body, signature)
    service.process_webhook(body, signature)

    assert record.status == "active"
    assert db.commit.call_count == 1


def test_concurrent_duplicate_subscription_webhook_is_ignored():
    record = SimpleNamespace(
        razorpay_subscription_id="sub_test_123",
        status="active",
        current_period_end=None,
        cancelled_at=None,
        failed_at=None,
        failure_reason=None,
    )
    db = MagicMock()
    db.scalar.side_effect = [None, record]
    db.flush.side_effect = IntegrityError("duplicate", {}, Exception())
    body, signature = _webhook("subscription.charged")

    SubscriptionService(db, Settings(RAZORPAY_WEBHOOK_SECRET="webhook-secret")).process_webhook(body, signature)

    assert db.commit.call_count == 0
    assert record.status == "active"


def test_non_duplicate_integrity_error_is_not_swallowed():
    db = MagicMock()
    db.scalar.side_effect = [None, None]
    error = IntegrityError("database failure", {}, Exception())
    db.flush.side_effect = error
    body, signature = _webhook("subscription.charged")

    with pytest.raises(IntegrityError) as raised:
        SubscriptionService(db, Settings(RAZORPAY_WEBHOOK_SECRET="webhook-secret")).process_webhook(
            body, signature
        )

    assert raised.value is error