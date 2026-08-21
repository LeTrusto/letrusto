"""add deterministic supplier candidate readiness state

Revision ID: 20260821_29
Revises: 20260821_28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260821_29"
down_revision: str | None = "20260821_28"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "supplier_candidates",
        sa.Column(
            "readiness_status",
            sa.String(length=20),
            nullable=False,
            server_default="DISCOVERED",
        ),
    )
    op.execute(
        sa.text(
            """
            UPDATE supplier_candidates
            SET readiness_status = CASE
                WHEN approval_status = 'REJECTED'
                    OR supplier_validation_status = 'REJECT'
                    OR commercial_status = 'REJECTED'
                    THEN 'REJECTED'
                WHEN approval_status IN ('APPROVED', 'IMPORTED')
                    OR supplier_validation_status = 'PASS'
                    THEN 'VALIDATED'
                ELSE 'REVIEW'
            END
            """
        )
    )
    op.create_index(
        "ix_supplier_candidates_readiness_status",
        "supplier_candidates",
        ["readiness_status"],
    )


def downgrade() -> None:
    op.drop_index("ix_supplier_candidates_readiness_status", table_name="supplier_candidates")
    op.drop_column("supplier_candidates", "readiness_status")