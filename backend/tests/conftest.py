from __future__ import annotations

import pytest

from app.suppliers.base import ShippingOption, ShippingResult, ShippingValidation


_ORDER_MODULES = {
    "test_admin_analytics",
    "test_cashfree_payments",
    "test_fulfillment_service",
    "test_inventory_reservations",
    "test_order_foundation",
}


class OrderFreightAdapter:
    """Deterministic freight fake for order-path tests; never calls CJ."""

    async def calculate_shipping(self, variant_id, destination_country, *, origin_country="CN", quantity=1):
        if origin_country != "CN" or destination_country != "IN":
            return ShippingResult(
                can_ship=False,
                validation=ShippingValidation.NOT_AVAILABLE,
                origin_country=origin_country,
                destination_country=destination_country,
            )
        return ShippingResult(
            can_ship=True,
            validation=ShippingValidation.VERIFIED,
            options=[ShippingOption(carrier="CJPacket Eub", method="CJPacket Eub", cost_usd=4.0, estimated_days="8-12", storage_id="CN")],
            origin_country=origin_country,
            destination_country=destination_country,
        )


@pytest.fixture(autouse=True)
def inject_order_freight_adapter(monkeypatch, request):
    if request.module.__name__.split(".")[-1] in _ORDER_MODULES:
        monkeypatch.setattr(
            "app.services.fulfillment_preflight_service.build_supplier_adapter",
            lambda _: OrderFreightAdapter(),
        )
