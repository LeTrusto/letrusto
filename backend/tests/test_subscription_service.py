import hashlib
import hmac
import json
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

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