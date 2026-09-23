"""Add manual property campaign content fields."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260923_48"
down_revision: str | None = "20260921_47"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("property_campaigns", sa.Column("campaign_key", sa.String(120), nullable=True))
    op.add_column("property_campaigns", sa.Column("source", sa.String(24), nullable=False, server_default="INSTAGRAM"))
    op.add_column("property_campaigns", sa.Column("medium", sa.String(64), nullable=False, server_default="social"))
    op.add_column("property_campaigns", sa.Column("content", sa.String(120)))
    op.execute("UPDATE property_campaigns SET campaign_key = id::text WHERE campaign_key IS NULL")
    op.alter_column("property_campaigns", "campaign_key", nullable=False)
    op.create_index("uq_property_campaigns_property_key", "property_campaigns", ["property_id", "campaign_key"], unique=True)
    op.add_column("social_posts", sa.Column("headline", sa.String(180)))
    op.add_column("social_posts", sa.Column("body", sa.Text(), nullable=False, server_default=""))
    op.add_column("social_posts", sa.Column("cta", sa.String(120)))


def downgrade() -> None:
    op.drop_column("social_posts", "cta")
    op.drop_column("social_posts", "body")
    op.drop_column("social_posts", "headline")
    op.drop_index("uq_property_campaigns_property_key", table_name="property_campaigns")
    op.drop_column("property_campaigns", "content")
    op.drop_column("property_campaigns", "medium")
    op.drop_column("property_campaigns", "source")
    op.drop_column("property_campaigns", "campaign_key")