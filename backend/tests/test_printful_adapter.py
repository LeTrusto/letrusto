import asyncio

import pytest

from app.suppliers.adapters.printful_adapter import PrintfulAdapter
from app.suppliers.base import ShippingValidation


def test_printful_requires_api_key():
    with pytest.raises(ValueError, match="Printful API key"):
        PrintfulAdapter("")


def test_search_products_parses_and_filters_catalog(monkeypatch):
    adapter = PrintfulAdapter("test-key")

    async def request(method, path, *, params=None, body=None):
        assert method == "GET"
        assert path == "/products"
        assert params["limit"] == 20
        return {"products": [{"id": 71, "title": "Unisex T-Shirt", "model": "TSHIRT", "image": "https://img/tee"}, {"id": 72, "title": "Mug", "model": "MUG"}]}

    monkeypatch.setattr(adapter, "_request", request)
    result = asyncio.run(adapter.search_products("shirt"))

    assert len(result) == 1
    assert result[0].supplier_product_id == "71"
    assert result[0].supplier_id == "printful"


def test_shipping_rates_map_to_shared_contract(monkeypatch):
    adapter = PrintfulAdapter("test-key")

    async def request(method, path, *, params=None, body=None):
        assert method == "POST"
        assert path == "/shipping/rates"
        assert body["recipient"]["country_code"] == "US"
        assert body["items"] == [{"variant_id": 101, "quantity": 2}]
        return {"rates": [{"id": "STANDARD", "name": "Standard", "carrier": "Printful", "rate": "6.50", "delivery_days": "5-8"}]}

    monkeypatch.setattr(adapter, "_request", request)
    result = asyncio.run(adapter.calculate_shipping("101", "US", quantity=2))

    assert result.can_ship is True
    assert result.validation == ShippingValidation.VERIFIED
    assert result.options[0].cost_usd == 6.5
    assert result.options[0].estimated_days == "5-8"


def test_create_order_maps_shared_fulfillment_payload(monkeypatch):
    adapter = PrintfulAdapter("test-key")

    async def request(method, path, *, params=None, body=None):
        assert method == "POST"
        assert path == "/orders"
        assert body["external_id"] == "LT-1001"
        assert body["recipient"]["country_code"] == "US"
        assert body["items"] == [{"variant_id": 101, "quantity": 1}]
        assert body["confirm"] is False
        return {"id": 9001, "status": "draft"}

    monkeypatch.setattr(adapter, "_request", request)
    result = asyncio.run(adapter.create_order({
        "orderNumber": "LT-1001",
        "shippingCustomerName": "Buyer",
        "shippingPhone": "+15550000000",
        "shippingAddress": "1 Main Street",
        "shippingCity": "Austin",
        "shippingProvince": "TX",
        "shippingZip": "78701",
        "shippingCountryCode": "US",
        "products": [{"pid": "71", "vid": "101", "quantity": 1}],
    }))

    assert result.accepted is True
    assert result.supplier_order_id == "9001"
    assert result.status == "draft"
