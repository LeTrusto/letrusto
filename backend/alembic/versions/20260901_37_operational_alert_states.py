"""add operational alert state

Revision ID: 20260901_37
Revises: 20260901_36
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260901_37"
down_revision: str | None = "20260901_36"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "operational_alert_states",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("alert_type", sa.String(length=40), nullable=False),
        sa.Column("alert_key", sa.String(length=240), nullable=False),
        sa.Column("fingerprint", sa.String(length=240), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("last_alert_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("recovered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivery_failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivery_failure_reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alert_type", "alert_key", name="uq_operational_alert_state_key"),
    )
    op.create_index("ix_operational_alert_states_active", "operational_alert_states", ["alert_type", "is_active"])


def downgrade() -> None:
    op.drop_index("ix_operational_alert_states_active", table_name="operational_alert_states")
    op.drop_table("operational_alert_states")