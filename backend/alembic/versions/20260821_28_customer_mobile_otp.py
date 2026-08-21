"""add customer mobile identity and otp challenges

Revision ID: 20260821_28
Revises: 20260821_27
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260821_28"
down_revision: str | None = "20260821_27"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("users", "email", existing_type=sa.String(length=255), nullable=True)
    op.add_column("users", sa.Column("mobile_number", sa.String(length=15), nullable=True))
    op.create_index("ix_users_mobile_number", "users", ["mobile_number"], unique=True)
    op.create_table(
        "otp_challenges",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("mobile_number", sa.String(length=15), nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("request_ip", sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_otp_challenges_mobile_number", "otp_challenges", ["mobile_number"], unique=False)
    op.create_index("ix_otp_challenges_mobile_created", "otp_challenges", ["mobile_number", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_otp_challenges_mobile_created", table_name="otp_challenges")
    op.drop_index("ix_otp_challenges_mobile_number", table_name="otp_challenges")
    op.drop_table("otp_challenges")
    op.drop_index("ix_users_mobile_number", table_name="users")
    op.drop_column("users", "mobile_number")
    op.alter_column("users", "email", existing_type=sa.String(length=255), nullable=False)
