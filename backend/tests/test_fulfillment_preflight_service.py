from __future__ import annotations

import asyncio
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest

from app.services.fulfillment_preflight_service import FulfillmentPreflightService
from app.api.v1.endpoints.supplier_validation import _preflight_dto
from app.suppliers.base import ShippingOption, ShippingResult, ShippingValidation


PRODUCT_ID = uuid4()
VARIANT_ID = uuid4()
VID = "0E582339-83F4-4D0A-8838-9E41584B05F2"


class FakeResult:
    def __init__(self, value):
        self.value = value

    def one_or_none(self):
        return self.value


class FakeDB:
    def __init__(self, warehouses, supplier="cj"):
        self.product = SimpleNamespace(id=PRODUCT_ID, status="ACTIVE", supplier=supplier)
        self.variant = SimpleNamespace(id=VARIANT_ID, supplier_variant_id=VID, active=True)
        self.warehouses = warehouses

    def execute(self, _statement):
        return FakeResult((self.product, self.variant))

    def scalars(self, _statement):
        return self.warehouses


class FakeAdapter:
    def __init__(self, routes=None, error=None):
        self.routes = routes or {}
        self.error = error
        self.calls = []

    async def calculate_shipping(self, variant_id, destination_country, *, origin_country="", quantity=1):
        self.calls.append((variant_id, destination_country, origin_country, quantity))
        if self.error:
            raise self.error
        return self.routes.get(
            origin_country,
            ShippingResult(
                can_ship=False,
                validation=ShippingValidation.NOT_AVAILABLE,
                origin_country=origin_country,
                destination_country=destination_country,
            ),
        )


def warehouse(country, sellable, factory=0, storage_id=None, identity=None):
    return SimpleNamespace(
        warehouse_country=country,
        storage_id=storage_id if storage_id is not None else country,
        warehouse_name=f"{country} warehouse",
        warehouse_identity=identity if identity is not None else storage_id or country,
        cj_sellable_inventory=sellable,
        factory_inventory=factory,
    )


def route(name="CJ Standard", cost=4.0, days="8-12"):
    return ShippingResult(
        can_ship=True,
        validation=ShippingValidation.VERIFIED,
        options=[ShippingOption(carrier=name, method=name, cost_usd=cost, estimated_days=days)],
    )


async def check(warehouses, adapter, quantity=1, **kwargs):
    return await FulfillmentPreflightService(FakeDB(warehouses), adapter).check(
        product_id=PRODUCT_ID,
        variant_id=VARIANT_ID,
        quantity=quantity,
        destination_country="IN",
        **kwargs,
    )


async def check_printful(adapter, quantity=1):
    return await FulfillmentPreflightService(FakeDB([], supplier="printful"), adapter).check(
        product_id=PRODUCT_ID,
        variant_id=VARIANT_ID,
        quantity=quantity,
        destination_country="IN",
    )


def test_product_1_is_not_fulfillable_when_only_us_stock_has_no_route():
    adapter = FakeAdapter(routes={"CN": route()})
    result = asyncio.run(check([warehouse("CN", 0, factory=50031), warehouse("US", 243)], adapter))
    assert result.status == "NOT_FULFILLABLE"
    assert result.error_classification == "NO_LOGISTICS"
    assert "both" in result.reason
    assert adapter.calls == [(VID, "IN", "US", 1)]


def test_china_sellable_stock_and_route_is_fulfillable():
    result = asyncio.run(check([warehouse("CN", 5, factory=50031)], FakeAdapter(routes={"CN": route()})))
    assert result.status == "FULFILLABLE"
    assert result.origin_country == "CN"
    assert result.sellable_inventory == 5


def test_printful_on_demand_does_not_require_warehouse_inventory():
    adapter = FakeAdapter(routes={"": route(name="Printful Standard")})
    result = asyncio.run(check_printful(adapter))
    assert result.status == "FULFILLABLE"
    assert result.sellable_inventory == 0
    assert result.logistics_name == "Printful Standard"
    assert adapter.calls == [(VID, "IN", "", 1)]


def test_factory_inventory_is_not_sellable():
    result = asyncio.run(check([warehouse("CN", 0, factory=50031)], FakeAdapter(routes={"CN": route()})))
    assert result.status == "NOT_FULFILLABLE"
    assert result.error_classification == "INVENTORY"


def test_missing_warehouse_identity_fails_safely():
    result = asyncio.run(check([warehouse("CN", 5, storage_id="", identity="")], FakeAdapter(routes={"CN": route()})))
    assert result.status == "NOT_FULFILLABLE"
    assert result.error_classification == "INVENTORY"


def test_only_valid_warehouse_is_selected():
    result = asyncio.run(check(
        [warehouse("US", 5), warehouse("CN", 5, storage_id="cn-1")],
        FakeAdapter(routes={"CN": route()}),
    ))
    assert result.status == "FULFILLABLE"
    assert result.storage_id == "cn-1"


def test_multiple_valid_warehouses_choose_lowest_cost_then_delivery():
    result = asyncio.run(check(
        [warehouse("CN", 5, storage_id="cn-slow"), warehouse("CN", 5, storage_id="cn-fast")],
        FakeAdapter(routes={"CN": route(cost=5, days="3-5")}),
    ))
    assert result.storage_id == "cn-fast"


def test_insufficient_inventory_and_no_warehouses_fail():
    insufficient = asyncio.run(check([warehouse("CN", 1)], FakeAdapter(routes={"CN": route()}), quantity=2))
    empty = asyncio.run(check([], FakeAdapter(routes={"CN": route()})))
    assert insufficient.error_classification == "INVENTORY"
    assert empty.error_classification == "INVENTORY"


def test_missing_logistic_name_is_not_usable():
    result = asyncio.run(check(
        [warehouse("CN", 5)],
        FakeAdapter(routes={"CN": route(name="")}),
    ))
    assert result.status == "NOT_FULFILLABLE"
    assert result.error_classification == "NO_LOGISTICS"


def test_freight_failure_and_429_are_safe_temporary_failures():
    failure = asyncio.run(check([warehouse("CN", 5)], FakeAdapter(error=httpx.HTTPError("failed"))))
    rate_limit = asyncio.run(check(
        [warehouse("CN", 5)],
        FakeAdapter(error=httpx.HTTPStatusError("429", request=httpx.Request("GET", "https://cj"), response=httpx.Response(429))),
    ))
    assert failure.error_classification == "TEMPORARY_SUPPLIER_ERROR"
    assert rate_limit.error_classification == "TEMPORARY_SUPPLIER_ERROR"


def test_exact_vid_is_forwarded_and_never_replaced():
    adapter = FakeAdapter(routes={"CN": route()})
    asyncio.run(check([warehouse("CN", 5)], adapter))
    assert adapter.calls[0][0] == VID


def test_preflight_endpoint_mapping_is_read_only_result_shape():
    result = asyncio.run(check([warehouse("CN", 5)], FakeAdapter(routes={"CN": route()})))
    dto = _preflight_dto(result)
    assert dto.fulfillable is True
    assert dto.vid == VID
    assert dto.warehouse_id == "CN"
    assert dto.logistic_name == "CJ Standard"