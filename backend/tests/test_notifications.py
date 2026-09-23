from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.entities import Base, Notification, User
from app.services.notification_service import NotificationService


def test_notifications_are_idempotent_private_and_readable_per_user():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[User.__table__, Notification.__table__])
    with Session(engine) as db:
        first_user = User(id=uuid4(), email="one@example.com", role="seller")
        second_user = User(id=uuid4(), email="two@example.com", role="seller")
        db.add_all([first_user, second_user]); db.commit()
        service = NotificationService(db)
        service.create_once(user_id=first_user.id, event_key="property:1:submitted", notification_type="PROPERTY_SUBMITTED", title="Property submitted for review", body="Your property has been submitted and is awaiting review.", related_entity_type="PROPERTY", related_entity_id="1")
        service.create_once(user_id=first_user.id, event_key="property:1:submitted", notification_type="PROPERTY_SUBMITTED", title="Duplicate", body="Should not be created.")
        service.create_once(user_id=second_user.id, event_key="property:1:submitted", notification_type="PROPERTY_SUBMITTED", title="Other user", body="Private.")
        db.commit()

        result = service.list_notifications(first_user.id)
        assert len(result.notifications) == 1
        assert result.notifications[0].related_entity_id == "1"
        assert "buyer" not in result.notifications[0].body.lower()
        service.mark_read(first_user.id, result.notifications[0].id)
        assert service.list_notifications(first_user.id).unread_count == 0
        assert service.list_notifications(second_user.id).unread_count == 1