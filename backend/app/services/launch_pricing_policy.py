from dataclasses import dataclass
from decimal import Decimal

from app.core.config import Settings, get_settings


PERCENT_BASE = Decimal("100")


@dataclass(frozen=True)
class LaunchPricingPolicy:
    pricing_fx_rate: Decimal
    payment_gateway_pct: Decimal
    rto_reserve_pct: Decimal
    target_contribution_margin_pct: Decimal
    target_cac_inr: Decimal

    def __post_init__(self) -> None:
        if self.pricing_fx_rate <= 0:
            raise ValueError("Pricing FX rate must be greater than zero")
        if self.target_cac_inr < 0:
            raise ValueError("Target CAC must be nonnegative")
        percentages = (
            self.payment_gateway_pct,
            self.rto_reserve_pct,
            self.target_contribution_margin_pct,
        )
        if any(value < 0 or value >= PERCENT_BASE for value in percentages):
            raise ValueError("Pricing policy percentages must be between zero and 100")
        if self.total_percentage_deduction >= Decimal("1"):
            raise ValueError("Total pricing policy percentage deduction must be less than one")

    @property
    def total_percentage_deduction(self) -> Decimal:
        return (
            self.payment_gateway_pct
            + self.rto_reserve_pct
            + self.target_contribution_margin_pct
        ) / PERCENT_BASE

    @property
    def denominator(self) -> Decimal:
        return Decimal("1") - self.total_percentage_deduction


def load_launch_pricing_policy(settings: Settings | None = None) -> LaunchPricingPolicy:
    config = settings or get_settings()
    return LaunchPricingPolicy(
        pricing_fx_rate=config.PRICING_FX_RATE,
        payment_gateway_pct=config.PAYMENT_GATEWAY_PCT,
        rto_reserve_pct=config.RTO_RESERVE_PCT,
        target_contribution_margin_pct=config.TARGET_CONTRIBUTION_MARGIN_PCT,
        target_cac_inr=config.TARGET_CAC_INR,
    )