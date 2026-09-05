"""add widget quiz marketing leads

Revision ID: 20260905_42
Revises: 20260905_41
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260905_42"
down_revision: str | None = "20260905_41"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "marketing_leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=True),
        sa.Column("business_type", sa.String(length=60), nullable=False),
        sa.Column("primary_goal", sa.String(length=60), nullable=False),
        sa.Column("monthly_visitors", sa.String(length=40), nullable=False),
        sa.Column("recommended_widget", sa.String(length=60), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False, server_default="widget_quiz"),
        sa.Column("consented_to_updates", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", "source", name="uq_marketing_leads_email_source"),
    )
    op.create_index("ix_marketing_leads_email", "marketing_leads", ["email"])


def downgrade() -> None:
    op.drop_index("ix_marketing_leads_email", table_name="marketing_leads")
    op.drop_table("marketing_leads")