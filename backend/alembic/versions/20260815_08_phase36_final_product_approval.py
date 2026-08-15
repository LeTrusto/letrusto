"""add final product approval decision metadata

Revision ID: 20260815_08
Revises: 20260815_07
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260815_08"
down_revision: str | None = "20260815_07"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "products", sa.Column("approval_decided_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "products",
        sa.Column("approval_decided_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "products", sa.Column("approval_rejection_reason", sa.String(length=500), nullable=True)
    )
    op.add_column("products", sa.Column("approval_evidence", sa.JSON(), nullable=True))
    op.create_foreign_key(
        "fk_products_approval_decided_by_user_id_users",
        "products", "users", ["approval_decided_by_user_id"], ["id"], ondelete="SET NULL",
    )
    op.create_index(
        "ix_products_approval_decided_by_user_id",
        "products", ["approval_decided_by_user_id"], unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_products_approval_decided_by_user_id", table_name="products")
    op.drop_constraint(
        "fk_products_approval_decided_by_user_id_users", "products", type_="foreignkey"
    )
    op.drop_column("products", "approval_evidence")
    op.drop_column("products", "approval_rejection_reason")
    op.drop_column("products", "approval_decided_by_user_id")
    op.drop_column("products", "approval_decided_at")