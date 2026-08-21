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
