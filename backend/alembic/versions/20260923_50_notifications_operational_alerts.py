"""Add notification navigation and idempotency fields."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260923_50"
down_revision: str | None = "20260923_49"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("notifications", sa.Column("related_entity_type", sa.String(40), nullable=True))
    op.add_column("notifications", sa.Column("related_entity_id", sa.String(100), nullable=True))
    op.add_column("notifications", sa.Column("event_key", sa.String(180), nullable=True))
    op.create_unique_constraint("uq_notifications_user_event", "notifications", ["user_id", "event_key"])


def downgrade() -> None:
    op.drop_constraint("uq_notifications_user_event", "notifications", type_="unique")
    op.drop_column("notifications", "event_key")
    op.drop_column("notifications", "related_entity_id")
    op.drop_column("notifications", "related_entity_type")