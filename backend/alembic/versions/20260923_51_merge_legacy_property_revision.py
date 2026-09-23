"""Join the legacy production revision to the current Bangalore schema head."""

from collections.abc import Sequence


revision: str = "20260923_51"
down_revision: tuple[str, str] = ("20260921_45", "20260923_50")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass