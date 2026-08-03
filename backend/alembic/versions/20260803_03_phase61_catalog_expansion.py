"""phase 6.1 catalog expansion

Revision ID: 20260803_03
Revises: 20260802_02
Create Date: 2026-08-03
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260803_03"
down_revision: str | None = "20260802_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Category hierarchy ────────────────────────────────────────────────────
    op.add_column("categories", sa.Column("parent_id", sa.Integer(), nullable=True))
    op.add_column("categories", sa.Column("icon", sa.String(length=80), nullable=True))
    op.add_column("categories", sa.Column("position", sa.Integer(), nullable=False, server_default="0"))
    op.create_foreign_key(
        "fk_categories_parent_id", "categories", "categories",
        ["parent_id"], ["id"], ondelete="SET NULL",
    )
    op.create_index("ix_categories_parent_id", "categories", ["parent_id"])

    # ── Product catalog enrichment columns ───────────────────────────────────
    op.add_column("products", sa.Column("series", sa.String(length=120), nullable=True))
    op.add_column("products", sa.Column("model_name", sa.String(length=120), nullable=True))
    op.add_column("products", sa.Column("variant", sa.String(length=120), nullable=True))
    op.add_column("products", sa.Column("storage", sa.String(length=40), nullable=True))
    op.add_column("products", sa.Column("ram", sa.String(length=20), nullable=True))
    op.add_column("products", sa.Column("color", sa.String(length=60), nullable=True))
    op.create_index("ix_products_series", "products", ["series"])

    # ── Seed top-level + expanded category tree ───────────────────────────────
    conn = op.get_bind()

    # Insert top-level parent categories (safe: all new names/slugs)
    top_level = [
        ("Electronics", "electronics", "💻", 1),
        ("Home & Kitchen", "home-kitchen", "🏠", 2),
        ("Beauty", "beauty", "✨", 3),
        ("Baby Care", "baby-care", "👶", 4),
        ("Pet Care", "pet-care", "🐾", 5),
        ("Fitness", "fitness", "💪", 6),
        ("Furniture", "furniture", "🪑", 7),
    ]
    for name, slug, icon, pos in top_level:
        conn.execute(
            sa.text(
                "INSERT INTO categories (name, slug, icon, position) "
                "VALUES (:name, :slug, :icon, :pos) "
                "ON CONFLICT (slug) DO UPDATE SET icon=EXCLUDED.icon, position=EXCLUDED.position"
            ),
            {"name": name, "slug": slug, "icon": icon, "pos": pos},
        )

    electronics_id = conn.execute(
        sa.text("SELECT id FROM categories WHERE slug = 'electronics'")
    ).scalar()
    home_id = conn.execute(
        sa.text("SELECT id FROM categories WHERE slug = 'home-kitchen'")
    ).scalar()

    # Insert NEW sub-categories that don't conflict with existing names
    electronics_subs = [
        ("Smartphones", "smartphones", "📱", 1),
        ("Laptops & Ultrabooks", "laptops-ultrabooks", "💻", 2),
        ("Tablets & iPads", "tablets-ipads", "📲", 3),
        ("Earbuds & TWS", "earbuds-tws", "🎧", 4),
        ("Smartwatches & Bands", "smartwatches-bands", "⌚", 6),
        ("Digital Cameras", "digital-cameras", "📷", 7),
        ("Bluetooth Speakers", "bluetooth-speakers", "🔊", 8),
        ("Monitors & Displays", "monitors-displays", "🖥️", 9),
        ("Televisions & OLEDs", "televisions-oleds", "📺", 11),
    ]
    for name, slug, icon, pos in electronics_subs:
        conn.execute(
            sa.text(
                "INSERT INTO categories (name, slug, parent_id, icon, position) "
                "VALUES (:name, :slug, :parent_id, :icon, :pos) "
                "ON CONFLICT (name) DO NOTHING"
            ),
            {"name": name, "slug": slug, "parent_id": electronics_id, "icon": icon, "pos": pos},
        )

    home_subs = [
        ("Refrigerators & Freezers", "refrigerators-freezers", "🧊", 1),
        ("Washing Machines & Dryers", "washing-machines-dryers", "🫧", 2),
        ("Air Conditioners", "air-conditioners", "❄️", 3),
        ("Microwave Ovens", "microwave-ovens", "📡", 4),
    ]
    for name, slug, icon, pos in home_subs:
        conn.execute(
            sa.text(
                "INSERT INTO categories (name, slug, parent_id, icon, position) "
                "VALUES (:name, :slug, :parent_id, :icon, :pos) "
                "ON CONFLICT (name) DO NOTHING"
            ),
            {"name": name, "slug": slug, "parent_id": home_id, "icon": icon, "pos": pos},
        )

    # Link existing leaf categories to Electronics / Home
    existing_links = [
        ("phone", electronics_id),
        ("laptop", electronics_id),
        ("headphones", electronics_id),
        ("smartwatch", electronics_id),
        ("television", electronics_id),
        ("refrigerator", home_id),
        ("washing-machine", home_id),
        ("gaming", electronics_id),
        ("tablet", electronics_id),
        ("camera", electronics_id),
    ]
    for slug, pid in existing_links:
        conn.execute(
            sa.text("UPDATE categories SET parent_id = :pid WHERE slug = :slug AND parent_id IS NULL"),
            {"pid": pid, "slug": slug},
        )


def downgrade() -> None:
    op.drop_index("ix_products_series", table_name="products")
    op.drop_column("products", "series")
    op.drop_column("products", "model_name")
    op.drop_column("products", "variant")
    op.drop_column("products", "storage")
    op.drop_column("products", "ram")
    op.drop_column("products", "color")

    op.drop_index("ix_categories_parent_id", table_name="categories")
    op.drop_constraint("fk_categories_parent_id", "categories", type_="foreignkey")
    op.drop_column("categories", "parent_id")
    op.drop_column("categories", "icon")
    op.drop_column("categories", "position")
