"""stage 3 recommendation foundation

Revision ID: 20260808_03
Revises: 20260808_02
Create Date: 2026-08-08
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260808_03"
down_revision: str | None = "20260808_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_tool_fact_provenance",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ai_tool_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fact_type", sa.String(length=40), nullable=False),
        sa.Column("fact_key", sa.String(length=160), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("source_kind", sa.String(length=40), nullable=False, server_default="official_provider"),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["ai_tool_id"], ["ai_tools.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_tool_fact_provenance_ai_tool_id", "ai_tool_fact_provenance", ["ai_tool_id"], unique=False)
    op.create_index(
        "ix_ai_tool_fact_provenance_tool_fact",
        "ai_tool_fact_provenance",
        ["ai_tool_id", "fact_type", "fact_key"],
        unique=False,
    )

    op.add_column("analytics_events", sa.Column("ai_tool_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("analytics_events", sa.Column("ai_tool_slug", sa.String(length=160), nullable=True))
    op.add_column("analytics_events", sa.Column("recommendation_id", sa.String(length=64), nullable=True))

    op.create_foreign_key(
        "fk_analytics_events_ai_tool_id",
        "analytics_events",
        "ai_tools",
        ["ai_tool_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_analytics_events_ai_tool_id", "analytics_events", ["ai_tool_id"], unique=False)
    op.create_index("ix_analytics_events_ai_tool_slug", "analytics_events", ["ai_tool_slug"], unique=False)
    op.create_index(
        "ix_analytics_events_recommendation_created",
        "analytics_events",
        ["recommendation_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_analytics_events_recommendation_created", table_name="analytics_events")
    op.drop_index("ix_analytics_events_ai_tool_slug", table_name="analytics_events")
    op.drop_index("ix_analytics_events_ai_tool_id", table_name="analytics_events")
    op.drop_constraint("fk_analytics_events_ai_tool_id", "analytics_events", type_="foreignkey")

    op.drop_column("analytics_events", "recommendation_id")
    op.drop_column("analytics_events", "ai_tool_slug")
    op.drop_column("analytics_events", "ai_tool_id")

    op.drop_index("ix_ai_tool_fact_provenance_tool_fact", table_name="ai_tool_fact_provenance")
    op.drop_index("ix_ai_tool_fact_provenance_ai_tool_id", table_name="ai_tool_fact_provenance")
    op.drop_table("ai_tool_fact_provenance")
