"""register approved LeTrusto catalog taxonomy and generic brand

Revision ID: 20260819_24
Revises: 20260819_23
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260819_24"
down_revision: str | None = "20260819_23"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


CATEGORIES = (
    ("Jewellery", "jewellery"),
    ("Hair & Style", "hair-style"),
    ("Beauty Tools", "beauty-tools"),
    ("Fashion Accessories", "accessories"),
    ("Gifts", "gifts"),
    ("Home & Kitchen", "home-kitchen"),
    ("Fitness", "fitness"),
    ("Baby & Kids", "baby-care"),
    ("Pet Care", "pet-care"),
)


def upgrade() -> None:
    connection = op.get_bind()
    for name, slug in CATEGORIES:
        connection.execute(
            sa.text(
                "INSERT INTO categories (name, slug, parent_id, position) "
                "VALUES (:name, :slug, NULL, 0) "
                "ON CONFLICT (slug) DO NOTHING"
            ),
            {"name": name, "slug": slug},
        )
    connection.execute(
        sa.text(
            "INSERT INTO brands (name, slug) VALUES (:name, :slug) "
            "ON CONFLICT (slug) DO NOTHING"
        ),
        {"name": "Generic / Unbranded", "slug": "generic-unbranded"},
    )


def downgrade() -> None:
    # Taxonomy rows are shared reference data; never remove them automatically.
    pass
