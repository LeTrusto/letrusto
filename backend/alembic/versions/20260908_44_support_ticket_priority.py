"""add support ticket priority for SaaS support workflow

Revision ID: 20260908_44
Revises: 20260906_43
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260908_44"
down_revision: str | None = "20260906_43"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "support_tickets",
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="normal"),
    )


def downgrade() -> None:
    op.drop_column("support_tickets", "priority")
