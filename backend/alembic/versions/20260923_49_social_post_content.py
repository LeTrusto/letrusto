"""Add social post content attribution field."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260923_49"
down_revision: str | None = "20260923_48"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("social_posts", sa.Column("content", sa.String(120), nullable=True))


def downgrade() -> None:
    op.drop_column("social_posts", "content")