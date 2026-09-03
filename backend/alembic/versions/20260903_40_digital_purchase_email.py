"""track digital purchase email delivery

Revision ID: 20260903_40
Revises: 20260902_39
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260903_40"
down_revision: str | None = "20260902_39"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("digital_entitlements", sa.Column("email_sent_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("digital_entitlements", "email_sent_at")
