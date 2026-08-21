import asyncio
from types import SimpleNamespace

import pytest

from app.suppliers.adapters import cj_adapter
from app.suppliers.adapters.cj_adapter import (
    CJAPIError,
    CJAdapter,
    CJErrorDetails,
    CJOrderProduct,
    CJOrderRequest,
    build_cj_order_payload,
)


@pytest.fixture
def order_request() -> CJOrderRequest:
    return CJOrderRequest(
        order_number="LT-ORDER-1",
        shipping_customer_name="Buyer",
        shipping_phone="9876543210",
        shipping_address="1 Main Street",
        shipping_city="Bengaluru",
        shipping_province="Karnataka",
        shipping_zip="560001",
        shipping_country="India",
        shipping_country_code="IN",
        from_country_code="CN",
        logistic_name="CJPacket Eub",
        products=(CJOrderProduct(vid="VID-1", quantity=2),),
    )


def test_v3_payload_preserves_required_fields_and_product_values(order_request):
    assert build_cj_order_payload(order_request) == {
        "orderNumber": "LT-ORDER-1",
        "shippingCustomerName": "Buyer",
        "shippingPhone": "9876543210",
        "shippingAddress": "1 Main Street",
        "shippingCity": "Bengaluru",
        "shippingProvince": "Karnataka",
        "shippingZip": "560001",
        "shippingCountry": "India",
        "shippingCountryCode": "IN",
        "fromCountryCode": "CN",
        "logisticName": "CJPacket Eub",
        "products": [{"vid": "VID-1", "quantity": 2}],
    }


def test_multiple_product_lines_are_preserved(order_request):
    request = CJOrderRequest(**{**order_request.__dict__, "products": (CJOrderProduct("VID-1", 2), CJOrderProduct("VID-2", 7))})

    assert build_cj_order_payload(request)["products"] == [
        {"vid": "VID-1", "quantity": 2},
        {"vid": "VID-2", "quantity": 7},
    ]


@pytest.mark.parametrize(
    "field",
    [
        "shipping_country",
        "shipping_country_code",
        "from_country_code",
        "logistic_name",
    ],
)
def test_missing_required_order_fields_fail_before_http(order_request, field):
    request = CJOrderRequest(**{**order_request.__dict__, field: ""})

    with pytest.raises(ValueError, match="missing"):
        build_cj_order_payload(request)


def test_missing_products_fails_before_http(order_request):
    request = CJOrderRequest(**{**order_request.__dict__, "products": ()})

    with pytest.raises(ValueError, match="products"):
        build_cj_order_payload(request)


def test_missing_vid_and_invalid_quantity_fail_before_http(order_request):
    with pytest.raises(ValueError, match="vid"):
        build_cj_order_payload(CJOrderRequest(**{**order_request.__dict__, "products": (CJOrderProduct("", 1),)}))
    with pytest.raises(ValueError, match="quantity"):
        build_cj_order_payload(CJOrderRequest(**{**order_request.__dict__, "products": (CJOrderProduct("VID-1", 0),)}))


@pytest.mark.parametrize(
    ("version", "path"),
    [("V2", "/shopping/order/createOrderV2"), ("V3", "/shopping/order/createOrderV3")],
)
def test_order_endpoint_construction(monkeypatch, order_request, version, path):
    calls = []

    async def fake_post(endpoint, payload):
        calls.append((endpoint, payload))
        return {"result": True, "data": {"orderId": "CJ-1"}}

    adapter = CJAdapter("test-key")
    monkeypatch.setattr(adapter, "_post", fake_post)

    result = asyncio.run(adapter.create_order(order_request, version=version))

    assert result.accepted is True
    assert calls[0][0] == path


def test_pay_balance_v2_requires_shipment_order_and_returns_pending(monkeypatch):
    calls = []

    async def fake_post(endpoint, payload):
        calls.append((endpoint, payload))
        return {"result": True, "data": "PAYMENT-RESULT", "requestId": "request-1"}

    adapter = CJAdapter("test-key")
    monkeypatch.setattr(adapter, "_post", fake_post)

    result = asyncio.run(adapter.pay_balance("SHIP-1", "PAY-1"))

    assert calls == [
        ("/shopping/pay/payBalanceV2", {"shipmentOrderId": "SHIP-1", "payId": "PAY-1"})
    ]
    assert result.payment_state == "PENDING"
    assert result.provider_metadata["payment_result"] == "PAYMENT-RESULT"


def test_get_balance_parses_official_usd_fields(monkeypatch):
    async def fake_get(endpoint, params=None):
        assert endpoint == "/shopping/pay/getBalance"
        assert params is None
        return {"result": True, "data": {"amount": 100.5, "noWithdrawalAmount": 4.5, "freezeAmount": 10}}

    adapter = CJAdapter("test-key")
    monkeypatch.setattr(adapter, "_get", fake_get)

    result = asyncio.run(adapter.get_balance())

    assert result.supported is True
    assert result.amount_usd == 100.5
    assert result.no_withdrawal_amount_usd == 4.5
    assert result.freeze_amount_usd == 10.0


def test_freight_result_parsing(monkeypatch):
    async def fake_post(endpoint, payload):
        assert endpoint == "/logistic/freightCalculate"
        return {
            "result": True,
            "data": [
                {
                    "logisticName": "CJPacket Eub",
                    "logisticPrice": 3.37,
                    "logisticAging": "12-50",
                    "storageId": "CN-WAREHOUSE-1",
                    "channelId": "channel-1",
                    "optionId": "option-1",
                }
            ],
        }

    adapter = CJAdapter("test-key")
    monkeypatch.setattr(adapter, "_post", fake_post)

    result = asyncio.run(adapter.calculate_shipping("VID-1", "IN", origin_country="CN"))

    option = result.options[0]
    assert result.origin_country == "CN"
    assert result.destination_country == "IN"
    assert option.method == "CJPacket Eub"
    assert option.cost_usd == 3.37
    assert option.estimated_days == "12-50"
    assert option.storage_id == "CN-WAREHOUSE-1"
    assert option.provider_metadata == {"channelId": "channel-1", "optionId": "option-1"}


@pytest.mark.parametrize(
    ("vid", "entries", "expected_total", "expected_cj", "expected_factory"),
    [
        (
            "0E582339-83F4-4D0A-8838-9E41584B05F2",
            [
                {
                    "areaId": "1",
                    "areaEn": "China Warehouse",
                    "countryCode": "CN",
                    "totalInventoryNum": 50031,
                    "cjInventoryNum": 0,
                    "factoryInventoryNum": 50031,
                    "stock": [{"stockId": "cn-sub-1"}],
                },
                {
                    "areaId": "2",
                    "areaEn": "US Warehouse",
                    "countryCode": "US",
                    "totalInventoryNum": 243,
                    "cjInventoryNum": 243,
                    "factoryInventoryNum": 0,
                    "stock": [{"stockId": "us-sub-1"}],
                },
            ],
            50274,
            243,
            50031,
        ),
        (
            "C2E09731-9358-4273-A763-D0C8C70DD4E2",
            [
                {
                    "areaId": "1",
                    "areaEn": "China Warehouse",
                    "countryCode": "CN",
                    "totalInventoryNum": 54105,
                    "cjInventoryNum": 0,
                    "factoryInventoryNum": 54105,
                    "stock": [{"stockId": "cn-sub-2"}],
                },
                {
                    "areaId": "2",
                    "areaEn": "US Warehouse",
                    "countryCode": "US",
                    "totalInventoryNum": 1,
                    "cjInventoryNum": 1,
                    "factoryInventoryNum": 0,
                    "stock": [{"stockId": "us-sub-2"}],
                },
            ],
            54106,
            1,
            54105,
        ),
        (
            "E821D001-A0D1-41C3-B492-244A482BD63E",
            [
                {
                    "areaId": "1",
                    "areaEn": "China Warehouse",
                    "countryCode": "CN",
                    "totalInventoryNum": 53967,
                    "cjInventoryNum": 4,
                    "factoryInventoryNum": 53963,
                    "stock": [{"stockId": "cn-sub-3"}],
                }
            ],
            53967,
            4,
            53963,
        ),
    ],
)
def test_get_inventory_preserves_documented_warehouse_identity_and_inventory_split(
    monkeypatch, vid, entries, expected_total, expected_cj, expected_factory
):
    async def fake_get(endpoint, params=None):
        assert endpoint == "/product/stock/queryByVid"
        assert params == {"vid": vid}
        return {"result": True, "data": entries}

    adapter = CJAdapter("test-key")
    monkeypatch.setattr(adapter, "_get", fake_get)

    snapshot = asyncio.run(adapter.get_inventory(vid, strict=True))

    assert snapshot is not None
    assert snapshot.total_inventory == expected_total
    assert snapshot.cj_inventory == expected_cj
    assert snapshot.factory_inventory == expected_factory
    assert sum(warehouse.cj_inventory for warehouse in snapshot.warehouses) == expected_cj
    assert sum(warehouse.factory_inventory for warehouse in snapshot.warehouses) == expected_factory
    assert [
        (warehouse.storage_id, warehouse.warehouse_name, warehouse.warehouse_country)
        for warehouse in snapshot.warehouses
    ] == [
        (entry["areaId"], entry["areaEn"], entry["countryCode"]) for entry in entries
    ]
    assert all(entry["stock"][0]["stockId"] for entry in entries)


def test_parse_variant_preserves_documented_warehouse_identity_and_aggregate_split():
    adapter = CJAdapter("test-key")
    variant = adapter._parse_variant(
        {
            "vid": "0E582339-83F4-4D0A-8838-9E41584B05F2",
            "inventories": [
                {
                    "areaId": "1",
                    "areaEn": "China Warehouse",
                    "countryCode": "CN",
                    "totalInventory": 50031,
                    "cjInventory": 0,
                    "factoryInventory": 50031,
                    "stock": [{"stockId": "cn-sub-1"}],
                },
                {
                    "areaId": "2",
                    "areaEn": "US Warehouse",
                    "countryCode": "US",
                    "totalInventory": 243,
                    "cjInventory": 243,
                    "factoryInventory": 0,
                    "stock": [{"stockId": "us-sub-1"}],
                },
            ],
        }
    )

    assert variant.inventory == 243
    assert variant.total_inventory == 50274
    assert variant.cj_inventory == 243
    assert variant.factory_inventory == 50031
    assert [
        (warehouse.storage_id, warehouse.warehouse_name, warehouse.warehouse_country)
        for warehouse in variant.warehouses
    ] == [
        ("1", "China Warehouse", "CN"),
        ("2", "US Warehouse", "US"),
    ]


def test_get_product_fallback_propagates_factory_only_warehouse_identity(monkeypatch):
    product = {
        "pid": "PRODUCT-FALLBACK",
        "productSku": "SKU-FALLBACK",
        "productNameEn": "Factory Only Product",
        "variants": [{
            "vid": "VID-FALLBACK",
            "variantSku": "VARIANT-FALLBACK",
            "variantNameEn": "Default",
            "variantSellPrice": 1.25,
            "inventories": None,
        }],
    }
    inventory = {
        "result": True,
        "data": [{
            "areaId": "1",
            "areaEn": "China Warehouse",
            "countryCode": "CN",
            "totalInventoryNum": 40000,
            "cjInventoryNum": 0,
            "factoryInventoryNum": 40000,
            "verifiedWarehouse": 2,
        }],
    }

    async def fake_get(endpoint, params=None):
        if endpoint == "/product/query":
            assert params == {"pid": "PRODUCT-FALLBACK"}
            return {"result": True, "data": product}
        if endpoint == "/product/stock/queryByVid":
            assert params == {"vid": "VID-FALLBACK"}
            return inventory
        raise AssertionError(endpoint)

    adapter = CJAdapter("test-key")
    monkeypatch.setattr(adapter, "_get", fake_get)

    result = asyncio.run(adapter.get_product("PRODUCT-FALLBACK"))

    assert result is not None
    variant = result.variants[0]
    assert variant.cj_inventory == 0
    assert variant.factory_inventory == 40000
    assert [(warehouse.storage_id, warehouse.warehouse_name, warehouse.warehouse_country) for warehouse in variant.warehouses] == [
        ("1", "China Warehouse", "CN")
    ]


def test_get_product_embedded_inventory_remains_unchanged_without_fallback(monkeypatch):
    product = {
        "pid": "PRODUCT-EMBEDDED",
        "productSku": "SKU-EMBEDDED",
        "productNameEn": "Embedded Inventory Product",
        "variants": [{
            "vid": "VID-EMBEDDED",
            "variantSku": "VARIANT-EMBEDDED",
            "variantNameEn": "Default",
            "variantSellPrice": 1.25,
            "inventories": [{
                "areaId": "2",
                "areaEn": "US Warehouse",
                "countryCode": "US",
                "totalInventory": 12,
                "cjInventory": 12,
                "factoryInventory": 0,
            }],
        }],
    }

    async def fake_get(endpoint, params=None):
        assert endpoint == "/product/query"
        return {"result": True, "data": product}

    adapter = CJAdapter("test-key")
    monkeypatch.setattr(adapter, "_get", fake_get)

    result = asyncio.run(adapter.get_product("PRODUCT-EMBEDDED"))

    assert result is not None
    variant = result.variants[0]
    assert variant.cj_inventory == 12
    assert [(warehouse.storage_id, warehouse.warehouse_name, warehouse.warehouse_country) for warehouse in variant.warehouses] == [
        ("2", "US Warehouse", "US")
    ]


def test_http_error_preserves_cj_body_code_message_request_id_and_redacts_credentials():
    response = SimpleNamespace(
        is_success=False,
        status_code=400,
        reason_phrase="Bad Request",
        json=lambda: {
            "code": 1600100,
            "message": "Param error",
            "requestId": "REQ-400",
            "data": {"token": "secret-token"},
        },
    )

    with pytest.raises(CJAPIError) as raised:
        CJAdapter._raise_for_cj_error(response, "/shopping/order/createOrderV3", "POST")

    error = raised.value
    assert error.details.http_status == 400
    assert error.details.cj_code == 1600100
    assert error.details.cj_message == "Param error"
    assert error.details.request_id == "REQ-400"
    assert error.details.endpoint == "/shopping/order/createOrderV3"
    assert error.details.operation == "POST"
    assert "secret-token" not in str(error)
    assert "CJ-Access-Token" not in str(error)


def test_http_429_is_structured():
    response = SimpleNamespace(
        is_success=False,
        status_code=429,
        reason_phrase="Too Many Requests",
        json=lambda: {"code": 1600200, "message": "Too Many Requests", "requestId": "REQ-429"},
    )

    with pytest.raises(CJAPIError) as raised:
        CJAdapter._raise_for_cj_error(response, "/logistic/freightCalculate", "POST")

    assert raised.value.details.http_status == 429
    assert raised.value.details.cj_code == 1600200
    assert raised.value.details.request_id == "REQ-429"


def test_existing_request_throttle_is_retained(monkeypatch):
    sleeps = []

    async def fake_sleep(delay):
        sleeps.append(delay)

    monkeypatch.setattr(cj_adapter.asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(cj_adapter, "_last_request_at", cj_adapter.time.monotonic())

    asyncio.run(CJAdapter("test-key")._throttle_requests())

    assert sleeps
    assert sleeps[0] > 0
    assert cj_adapter._CJ_REQUEST_INTERVAL_SECONDS == 2.0
