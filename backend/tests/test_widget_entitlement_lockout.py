from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.widget_events import create_widget_event, hide_widget_event, list_widget_events
from app.api.v1.endpoints.widgets import create_widget, delete_widget, get_widget, list_widgets, update_widget
from app.schemas.widgets import WidgetCreate, WidgetEventCreate, WidgetUpdate


@pytest.fixture()
def expired_context():
    user = SimpleNamespace(
        id=uuid4(),
        trial_ends_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )
    db = MagicMock()
    db.scalar.return_value = None
    return user, db


def test_expired_user_cannot_manage_widgets(expired_context):
    user, db = expired_context
    widget_id = uuid4()

    operations = [
        lambda: create_widget(WidgetCreate(name="Widget", domain_name="example.com"), user, db),
        lambda: list_widgets(user, db),
        lambda: get_widget(widget_id, user, db),
        lambda: update_widget(widget_id, WidgetUpdate(name="Updated"), user, db),
        lambda: delete_widget(widget_id, user, db),
    ]

    for operation in operations:
        with pytest.raises(HTTPException) as error:
            operation()
        assert error.value.status_code == 403


def test_expired_user_cannot_manage_widget_events(expired_context):
    user, db = expired_context
    widget_id = uuid4()
    event_id = uuid4()
    payload = WidgetEventCreate(customer_name="Customer", action_text="joined")

    operations = [
        lambda: create_widget_event(widget_id, payload, user, db),
        lambda: list_widget_events(widget_id, user, db),
        lambda: hide_widget_event(event_id, user, db),
    ]

    for operation in operations:
        with pytest.raises(HTTPException) as error:
            operation()
        assert error.value.status_code == 403