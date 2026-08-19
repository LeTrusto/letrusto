"""enforce immutable trust history

Revision ID: 20260819_23
Revises: 20260819_22
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260819_23"
down_revision: str | None = "20260819_22"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE FUNCTION prevent_trust_history_mutation()
        RETURNS trigger AS $$
        BEGIN
            IF current_setting('letrusto.trust_history_maintenance', true) = 'on' THEN
                IF TG_OP = 'DELETE' THEN
                    RETURN OLD;
                END IF;
                RETURN NEW;
            END IF;
            RAISE EXCEPTION 'trust history is append-only' USING ERRCODE = '55000';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        "CREATE TRIGGER trg_trust_verifications_immutable BEFORE UPDATE OR DELETE ON trust_verifications "
        "FOR EACH ROW EXECUTE FUNCTION prevent_trust_history_mutation();"
    )
    op.execute(
        "CREATE TRIGGER trg_trust_audit_events_immutable BEFORE UPDATE OR DELETE ON trust_audit_events "
        "FOR EACH ROW EXECUTE FUNCTION prevent_trust_history_mutation();"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER trg_trust_audit_events_immutable ON trust_audit_events;")
    op.execute("DROP TRIGGER trg_trust_verifications_immutable ON trust_verifications;")
    op.execute("DROP FUNCTION prevent_trust_history_mutation();")
