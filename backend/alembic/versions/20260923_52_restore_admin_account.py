"""Restore the designated production administrator account."""

from collections.abc import Sequence

from alembic import op


revision: str = "20260923_52"
down_revision: str | None = "20260923_51"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "UPDATE users SET role = 'admin', updated_at = now() "
        "WHERE lower(email) = 'admin@letrusto.dev'"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE users SET role = 'user', updated_at = now() "
        "WHERE lower(email) = 'admin@letrusto.dev'"
    )