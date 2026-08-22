"""add reusable customer checkout profile

Revision ID: 20260822_30
Revises: 20260821_29
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260822_30"
down_revision: str | None = "20260821_29"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_number", sa.String(length=15), nullable=True))
    op.add_column("users", sa.Column("shipping_address", sa.JSON(), nullable=True))
    op.execute(
        sa.text(
            """
            UPDATE users AS users
            SET phone_number = latest.customer_phone,
                shipping_address = latest.shipping_address
            FROM (
                SELECT DISTINCT ON (user_id)
                    user_id, customer_phone, shipping_address
                FROM orders
                WHERE user_id IS NOT NULL
                ORDER BY user_id, created_at DESC
            ) AS latest
            WHERE users.id = latest.user_id
              AND (users.phone_number IS NULL OR users.shipping_address IS NULL)
            """
        )
    )


def downgrade() -> None:
    op.drop_column("users", "shipping_address")
    op.drop_column("users", "phone_number")
