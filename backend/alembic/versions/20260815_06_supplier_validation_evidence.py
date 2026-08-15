"""persist supplier validation evidence

Revision ID: 20260815_06
Revises: 20260815_05
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260815_06"
down_revision: str | None = "20260815_05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("products", sa.Column("supplier_validation_score", sa.Integer(), nullable=True))
    op.add_column("products", sa.Column("supplier_validation_notes", sa.JSON(), nullable=True))
    op.add_column("products", sa.Column("supplier_validation_details", sa.JSON(), nullable=True))
    op.add_column("products", sa.Column("supplier_validated_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("products", "supplier_validated_at")
    op.drop_column("products", "supplier_validation_details")
    op.drop_column("products", "supplier_validation_notes")
    op.drop_column("products", "supplier_validation_score")