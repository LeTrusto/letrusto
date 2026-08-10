"""set ElevenLabs affiliate URL and enable affiliate flag

Revision ID: 20260810_01
Revises: 20260808_03
Create Date: 2026-08-10
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260810_01"
down_revision: str | None = "20260808_03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ELEVENLABS_AFFILIATE_URL = "https://try.elevenlabs.io/l893urztlad5"


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE ai_tools "
            "SET affiliate_available = true, "
            "    affiliate_url = :url "
            "WHERE slug = 'elevenlabs'"
        ),
        {"url": ELEVENLABS_AFFILIATE_URL},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE ai_tools "
            "SET affiliate_available = false, "
            "    affiliate_url = NULL "
            "WHERE slug = 'elevenlabs'"
        )
    )
