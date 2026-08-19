"""add product trust data foundation

Revision ID: 20260819_22
Revises: 20260818_21
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260819_22"
down_revision: str | None = "20260818_21"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


STATUS_CHECK = "('UNVERIFIED', 'PENDING', 'VERIFIED', 'REJECTED', 'EXPIRED')"


def upgrade() -> None:
    op.create_table(
        "trust_claims",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("claim_type", sa.String(80), nullable=False),
        sa.Column("claim_value", sa.Text(), nullable=False),
        sa.Column("claim_description", sa.Text(), nullable=True),
        sa.Column("source", sa.String(80), nullable=True),
        sa.Column("verification_status", sa.String(20), nullable=False, server_default="UNVERIFIED"),
        sa.Column("confidence", sa.Numeric(5, 2), nullable=True),
        sa.Column("assessment_metadata", postgresql.JSON(), nullable=True),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(f"verification_status IN {STATUS_CHECK}", name="ck_trust_claim_status"),
        sa.CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 100)", name="ck_trust_claim_confidence"),
    )
    op.create_index("ix_trust_claims_product_id", "trust_claims", ["product_id"])
    op.create_index("ix_trust_claims_product_status", "trust_claims", ["product_id", "verification_status"])
    op.create_index("ix_trust_claims_type", "trust_claims", ["claim_type"])

    op.create_table(
        "trust_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("evidence_type", sa.String(80), nullable=False),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source", sa.String(80), nullable=True),
        sa.Column("reference_url", sa.Text(), nullable=True),
        sa.Column("storage_reference", sa.Text(), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evidence_metadata", postgresql.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("(reference_url IS NOT NULL) OR (storage_reference IS NOT NULL)", name="ck_trust_evidence_reference"),
    )
    op.create_index("ix_trust_evidence_type_active", "trust_evidence", ["evidence_type", "is_active"])

    op.create_table(
        "trust_claim_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("trust_claims.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evidence_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("trust_evidence.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("assessment_metadata", postgresql.JSON(), nullable=True),
        sa.Column("attached_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("claim_id", "evidence_id", name="uq_trust_claim_evidence"),
    )
    op.create_index("ix_trust_claim_evidence_claim_id", "trust_claim_evidence", ["claim_id"])
    op.create_index("ix_trust_claim_evidence_evidence_id", "trust_claim_evidence", ["evidence_id"])

    op.create_table(
        "trust_verifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("trust_claims.id", ondelete="CASCADE"), nullable=False),
        sa.Column("verification_status", sa.String(20), nullable=False),
        sa.Column("verification_method", sa.String(80), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("evidence_snapshot", postgresql.JSON(), nullable=True),
        sa.Column("verification_metadata", postgresql.JSON(), nullable=True),
        sa.Column("verified_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(f"verification_status IN {STATUS_CHECK}", name="ck_trust_verification_status"),
    )
    op.create_index("ix_trust_verifications_claim_id", "trust_verifications", ["claim_id"])
    op.create_index("ix_trust_verifications_claim_verified", "trust_verifications", ["claim_id", "verified_at"])

    op.create_table(
        "trust_audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("trust_claims.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evidence_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("trust_evidence.id", ondelete="SET NULL"), nullable=True),
        sa.Column("verification_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("trust_verifications.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("previous_state", postgresql.JSON(), nullable=True),
        sa.Column("current_state", postgresql.JSON(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("event_metadata", postgresql.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_trust_audit_events_claim_id", "trust_audit_events", ["claim_id"])
    op.create_index("ix_trust_audit_events_claim_created", "trust_audit_events", ["claim_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_trust_audit_events_claim_created", table_name="trust_audit_events")
    op.drop_index("ix_trust_audit_events_claim_id", table_name="trust_audit_events")
    op.drop_table("trust_audit_events")
    op.drop_index("ix_trust_verifications_claim_verified", table_name="trust_verifications")
    op.drop_index("ix_trust_verifications_claim_id", table_name="trust_verifications")
    op.drop_table("trust_verifications")
    op.drop_index("ix_trust_claim_evidence_evidence_id", table_name="trust_claim_evidence")
    op.drop_index("ix_trust_claim_evidence_claim_id", table_name="trust_claim_evidence")
    op.drop_table("trust_claim_evidence")
    op.drop_index("ix_trust_evidence_type_active", table_name="trust_evidence")
    op.drop_table("trust_evidence")
    op.drop_index("ix_trust_claims_type", table_name="trust_claims")
    op.drop_index("ix_trust_claims_product_status", table_name="trust_claims")
    op.drop_index("ix_trust_claims_product_id", table_name="trust_claims")
    op.drop_table("trust_claims")
