"""initial schema

Revision ID: 20260731_01
Revises:
Create Date: 2026-07-31
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260731_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"], unique=False)

    op.create_table(
        "brands",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_brands_slug", "brands", ["slug"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(length=150), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("availability", sa.String(length=30), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("brand_id", sa.Integer(), nullable=False),
        sa.Column("price_value", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("rating", sa.Numeric(3, 1), nullable=False),
        sa.Column("ai_score", sa.Integer(), nullable=False),
        sa.Column("ai_summary", sa.Text(), nullable=False),
        sa.Column("review_summary", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_products_slug", "products", ["slug"], unique=False)
    op.create_index("ix_products_name", "products", ["name"], unique=False)
    op.create_index("ix_products_category_price", "products", ["category_id", "price_value"], unique=False)
    op.create_index("ix_products_rating_ai", "products", ["rating", "ai_score"], unique=False)

    op.create_table(
        "product_similarities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("similar_product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["similar_product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "similar_product_id", name="uq_product_similarity_pair"),
    )
    op.create_index("ix_product_similarity_product_score", "product_similarities", ["product_id", "score"], unique=False)

    # Child tables
    child_tables = [
        "product_images",
        "product_specifications",
        "product_features",
        "product_pros",
        "product_cons",
        "product_best_for",
        "product_not_recommended_for",
        "product_tags",
        "price_history",
        "reviews",
        "product_buy_links",
    ]

    for table in child_tables:
        op.create_table(
            table,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(f"ix_{table}_product_id", table, ["product_id"], unique=False)

    op.add_column("product_images", sa.Column("url", sa.Text(), nullable=False))
    op.add_column("product_images", sa.Column("position", sa.Integer(), nullable=False))
    op.create_unique_constraint("uq_product_images_product_position", "product_images", ["product_id", "position"])

    op.add_column("product_specifications", sa.Column("label", sa.String(length=120), nullable=False))
    op.add_column("product_specifications", sa.Column("value", sa.String(length=240), nullable=False))
    op.add_column("product_specifications", sa.Column("position", sa.Integer(), nullable=False))
    op.create_unique_constraint("uq_product_specifications_product_label", "product_specifications", ["product_id", "label"])

    for table in ["product_features", "product_pros", "product_cons", "product_best_for", "product_not_recommended_for"]:
        op.add_column(table, sa.Column("value", sa.String(length=240), nullable=False))
        op.add_column(table, sa.Column("position", sa.Integer(), nullable=False))

    op.add_column("product_tags", sa.Column("value", sa.String(length=80), nullable=False))
    op.create_index("ix_product_tags_value", "product_tags", ["value"], unique=False)

    op.add_column("price_history", sa.Column("label", sa.String(length=40), nullable=False))
    op.add_column("price_history", sa.Column("price", sa.Numeric(12, 2), nullable=False))
    op.create_unique_constraint("uq_price_history_product_label", "price_history", ["product_id", "label"])

    op.add_column("reviews", sa.Column("author", sa.String(length=120), nullable=False))
    op.add_column("reviews", sa.Column("title", sa.String(length=180), nullable=False))
    op.add_column("reviews", sa.Column("rating", sa.Numeric(2, 1), nullable=False))
    op.add_column("reviews", sa.Column("comment", sa.Text(), nullable=False))
    op.add_column("reviews", sa.Column("date", sa.String(length=20), nullable=False))
    op.create_index("ix_reviews_product_rating", "reviews", ["product_id", "rating"], unique=False)

    op.add_column("product_buy_links", sa.Column("label", sa.String(length=60), nullable=False))
    op.add_column("product_buy_links", sa.Column("href", sa.Text(), nullable=False))
    op.create_unique_constraint("uq_product_buy_links_product_label", "product_buy_links", ["product_id", "label"])

    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "product_id", name="uq_favorites_user_product"),
    )
    op.create_index("ix_favorites_user_id", "favorites", ["user_id"], unique=False)
    op.create_index("ix_favorites_product_id", "favorites", ["product_id"], unique=False)
    op.create_index("ix_favorites_user_created", "favorites", ["user_id", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("favorites")
    op.drop_table("product_buy_links")
    op.drop_table("reviews")
    op.drop_table("price_history")
    op.drop_table("product_tags")
    op.drop_table("product_not_recommended_for")
    op.drop_table("product_best_for")
    op.drop_table("product_cons")
    op.drop_table("product_pros")
    op.drop_table("product_features")
    op.drop_table("product_specifications")
    op.drop_table("product_images")
    op.drop_table("product_similarities")
    op.drop_table("products")
    op.drop_table("brands")
    op.drop_table("categories")
