"""complete supplier candidate workflow audit data

Revision ID: 20260817_11
Revises: 20260816_10
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260817_11"
down_revision: str | None = "20260816_10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("supplier_candidates", sa.Column("data_snapshot", postgresql.JSON(), nullable=True))
    op.add_column("supplier_candidates", sa.Column("decision_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("supplier_candidates", sa.Column("decision_by_user_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("supplier_candidates", sa.Column("rejection_reason", sa.String(length=500), nullable=True))
    op.add_column("supplier_candidates", sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("supplier_candidates", sa.Column("import_result", sa.String(length=40), nullable=True))
    op.add_column("supplier_candidates", sa.Column("import_failure_reason", sa.Text(), nullable=True))
    op.create_foreign_key("fk_supplier_candidates_decision_by_user_id", "supplier_candidates", "users", ["decision_by_user_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_supplier_candidates_decision_by_user_id", "supplier_candidates", ["decision_by_user_id"])


def downgrade() -> None:
    op.drop_index("ix_supplier_candidates_decision_by_user_id", table_name="supplier_candidates")
    op.drop_constraint("fk_supplier_candidates_decision_by_user_id", "supplier_candidates", type_="foreignkey")
    for column in ("import_failure_reason", "import_result", "imported_at", "rejection_reason", "decision_by_user_id", "decision_at", "data_snapshot"):
        op.drop_column("supplier_candidates", column)