"""add immutable order item economics snapshots

Revision ID: 20260818_20
Revises: 20260818_19
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260818_20"
down_revision: str | None = "20260818_19"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    columns = [
        ("supplier_cost_inr_snapshot", sa.Numeric(12, 2)),
        ("supplier_cost_usd_snapshot", sa.Numeric(12, 4)),
        ("supplier_cost_currency_snapshot", sa.String(8)),
        ("shipping_cost_inr_snapshot", sa.Numeric(12, 2)),
        ("landed_cost_inr_snapshot", sa.Numeric(12, 2)),
        ("pricing_fx_rate_snapshot", sa.Numeric(12, 4)),
        ("payment_gateway_policy_pct_snapshot", sa.Numeric(8, 4)),
        ("rto_reserve_policy_pct_snapshot", sa.Numeric(8, 4)),
        ("target_contribution_margin_pct_snapshot", sa.Numeric(8, 4)),
        ("target_cac_inr_snapshot", sa.Numeric(12, 2)),
        ("economics_status", sa.String(20)),
        ("economics_missing", sa.JSON()),
    ]
    for name, column_type in columns:
        op.add_column("order_items", sa.Column(name, column_type, nullable=True))


def downgrade() -> None:
    for name in (
        "economics_missing",
        "economics_status",
        "target_cac_inr_snapshot",
        "target_contribution_margin_pct_snapshot",
        "rto_reserve_policy_pct_snapshot",
        "payment_gateway_policy_pct_snapshot",
        "pricing_fx_rate_snapshot",
        "landed_cost_inr_snapshot",
        "shipping_cost_inr_snapshot",
        "supplier_cost_currency_snapshot",
        "supplier_cost_usd_snapshot",
        "supplier_cost_inr_snapshot",
    ):
        op.drop_column("order_items", name)