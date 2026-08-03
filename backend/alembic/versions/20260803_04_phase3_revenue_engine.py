"""phase 3 revenue engine — affiliate tracking + content engine

Revision ID: 20260803_04
Revises: 20260803_03
Create Date: 2026-08-03
"""

from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "20260803_04"
down_revision: str | None = "20260803_03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Affiliate tracking columns on existing product_buy_links
    op.add_column("product_buy_links", sa.Column("retailer_type", sa.String(40), nullable=False, server_default="marketplace"))
    op.add_column("product_buy_links", sa.Column("is_affiliate", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("product_buy_links", sa.Column("click_count", sa.Integer(), nullable=False, server_default="0"))

    # Content / articles table
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("category", sa.String(80), nullable=False, server_default="guide"),
        sa.Column("meta_title", sa.String(300), nullable=True),
        sa.Column("meta_description", sa.String(500), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_articles_slug", "articles", ["slug"], unique=True)
    op.create_index("ix_articles_published", "articles", ["is_published", "created_at"])


def downgrade() -> None:
    op.drop_table("articles")
    op.drop_column("product_buy_links", "click_count")
    op.drop_column("product_buy_links", "is_affiliate")
    op.drop_column("product_buy_links", "retailer_type")
