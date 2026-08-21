"""CJDropshipping API adapter — Phase 2 validation prototype."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal

import httpx

from app.suppliers.base import (
    InventorySnapshot,
    RawSupplierProduct,
    RawVariant,
    ShippingOption,
    ShippingResult,
    SupplierOrderResult,
    SupplierTrackingResult,
    ShippingValidation,
    SupplierCategory,
    WarehouseInventorySnapshot,
)

logger = logging.getLogger(__name__)

_BASE_URL = "https://developers.cjdropshipping.com/api2.0/v1"
_DEFAULT_TOKEN_TTL_SECONDS = 900
_TOKEN_REFRESH_SKEW_SECONDS = 30
_CJ_REQUEST_INTERVAL_SECONDS = 2.0
_cached_access_token = ""
_cached_token_expires_at = 0.0
_request_lock = asyncio.Lock()
_last_request_at = 0.0

CJ_ORDER_ENDPOINTS = {
    "V2": "/shopping/order/createOrderV2",
    "V3": "/shopping/order/createOrderV3",
}


@dataclass(frozen=True)
class CJOrderProduct:
    vid: str
    quantity: int


@dataclass(frozen=True)
class CJOrderRequest:
    order_number: str
    shipping_customer_name: str
    shipping_phone: str
    shipping_address: str
    shipping_city: str
    shipping_province: str
    shipping_zip: str
    shipping_country: str
    shipping_country_code: str
    from_country_code: str
    logistic_name: str
    products: tuple[CJOrderProduct, ...]


@dataclass(frozen=True)
class CJErrorDetails:
    http_status: int | None
    cj_code: int | str | None
    cj_message: str
    request_id: str | None
    endpoint: str
    timestamp: str
    operation: str


class CJAPIError(httpx.HTTPError):
    def __init__(self, details: CJErrorDetails) -> None:
        self.details = details
        super().__init__(self._message())

    def _message(self) -> str:
        status = f"HTTP {self.details.http_status}" if self.details.http_status else "CJ error"
        code = f" code={self.details.cj_code}" if self.details.cj_code is not None else ""
        request_id = f" request_id={self.details.request_id}" if self.details.request_id else ""
        return f"{status}{code}: {self.details.cj_message}{request_id}"


def build_cj_order_payload(request: CJOrderRequest) -> dict[str, object]:
    required = {
        "orderNumber": request.order_number,
        "shippingCustomerName": request.shipping_customer_name,
        "shippingPhone": request.shipping_phone,
        "shippingAddress": request.shipping_address,
        "shippingCity": request.shipping_city,
        "shippingProvince": request.shipping_province,
        "shippingZip": request.shipping_zip,
        "shippingCountry": request.shipping_country,
        "shippingCountryCode": request.shipping_country_code,
        "fromCountryCode": request.from_country_code,
        "logisticName": request.logistic_name,
    }
    missing = [name for name, value in required.items() if not str(value).strip()]
    if missing:
        raise ValueError(f"CJ order request is missing: {', '.join(missing)}")
    if not request.products:
        raise ValueError("CJ order request is missing: products")

    products: list[dict[str, object]] = []
    for index, product in enumerate(request.products):
        if not product.vid.strip():
            raise ValueError(f"CJ order product {index} is missing: vid")
        if isinstance(product.quantity, bool) or not isinstance(product.quantity, int) or product.quantity <= 0:
            raise ValueError(f"CJ order product {index} has invalid quantity")
        products.append({"vid": product.vid, "quantity": product.quantity})

    return {**required, "products": products}


class CJAdapter:
    supplier_name = "cj"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key.strip()
        if not self._api_key:
            raise ValueError("CJ API key is not configured")

    # ── helpers ──────────────────────────────────────────

    def _headers(self) -> dict[str, str]:
        h: dict[str, str] = {"Content-Type": "application/json"}
        if _token_is_valid():
            h["CJ-Access-Token"] = _cached_access_token
        return h

    @staticmethod
    def _raise_for_cj_error(resp: httpx.Response, path: str, operation: str) -> None:
        if resp.status_code < 400:
            return
        body: dict[str, Any] = {}
        try:
            parsed = resp.json()
            if isinstance(parsed, dict):
                body = parsed
        except (ValueError, TypeError):
            pass
        details = CJErrorDetails(
            http_status=resp.status_code,
            cj_code=body.get("code"),
            cj_message=str(body.get("message") or resp.reason_phrase or "CJ request failed"),
            request_id=body.get("requestId") or body.get("request_id"),
            endpoint=path,
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation=operation,
        )
        raise CJAPIError(details)

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        transport = httpx.AsyncHTTPTransport(retries=1)
        async with httpx.AsyncClient(timeout=30, transport=transport) as client:
            await self._throttle_requests()
            resp = await client.get(f"{_BASE_URL}{path}", headers=self._headers(), params=params)
            if resp.status_code == 401 and path != "/authentication/getAccessToken":
                await self.authenticate(force=True)
                await self._throttle_requests()
                resp = await client.get(f"{_BASE_URL}{path}", headers=self._headers(), params=params)
            self._raise_for_cj_error(resp, path, "GET")
            return resp.json()

    async def _post(self, path: str, json_body: dict | None = None) -> dict:
        transport = httpx.AsyncHTTPTransport(retries=1)
        async with httpx.AsyncClient(timeout=30, transport=transport) as client:
            await self._throttle_requests()
            resp = await client.post(f"{_BASE_URL}{path}", headers=self._headers(), json=json_body or {})
            if resp.status_code == 401 and path != "/authentication/getAccessToken":
                await self.authenticate(force=True)
                await self._throttle_requests()
                resp = await client.post(f"{_BASE_URL}{path}", headers=self._headers(), json=json_body or {})
            self._raise_for_cj_error(resp, path, "POST")
            return resp.json()

    async def _throttle_requests(self) -> None:
        global _last_request_at
        async with _request_lock:
            delay = _CJ_REQUEST_INTERVAL_SECONDS - (time.monotonic() - _last_request_at)
            if delay > 0:
                await asyncio.sleep(delay)
            _last_request_at = time.monotonic()

    # ── authentication ───────────────────────────────────

    async def authenticate(self, *, force: bool = False) -> bool:
        global _cached_access_token, _cached_token_expires_at

        if not force and _token_is_valid():
            return True
        if force:
            _cached_access_token = ""
            _cached_token_expires_at = 0.0

        try:
            data = await self._post("/authentication/getAccessToken", {"apiKey": self._api_key})
        except (httpx.HTTPError, ValueError, TypeError):
            logger.warning("CJ authentication request failed")
            return False

        token_data = data.get("data") if isinstance(data, dict) else None
        token = token_data.get("accessToken") if isinstance(token_data, dict) else None
        if isinstance(data, dict) and data.get("result") is True and isinstance(token, str) and token:
            _cached_access_token = token
            _cached_token_expires_at = time.monotonic() + _token_ttl_seconds(token_data)
            logger.info("CJ authentication successful")
            return True

        logger.warning("CJ authentication failed")
        return False

    # ── categories ───────────────────────────────────────

    async def get_categories(self) -> list[SupplierCategory]:
        data = await self._get("/product/getCategory")
        if not data.get("result"):
            return []
        categories: list[SupplierCategory] = []
        for first in data.get("data", []):
            first_name = first.get("categoryFirstName", "")
            for second in first.get("categoryFirstList", []):
                second_name = second.get("categorySecondName", "")
                for third in second.get("categorySecondList", []):
                    categories.append(
                        SupplierCategory(
                            category_id=third.get("categoryId", ""),
                            name=third.get("categoryName", ""),
                            parent_id="",
                            parent_name=f"{first_name} > {second_name}",
                            level=3,
                        )
                    )
        return categories

    # ── product search ───────────────────────────────────

    async def search_products(
        self, keyword: str, *, category_id: str = "", page: int = 1, page_size: int = 20
    ) -> list[RawSupplierProduct]:
        params: dict[str, Any] = {
            "keyWord": keyword,
            "page": page,
            "size": min(page_size, 50),
            "features": "enable_description,enable_category",
        }
        if category_id:
            params["categoryId"] = category_id

        data = await self._get("/product/listV2", params)
        if not data.get("result"):
            logger.warning("CJ search failed: %s", data.get("message"))
            return []

        products: list[RawSupplierProduct] = []
        for content in data.get("data", {}).get("content", []):
            for item in content.get("productList", []):
                products.append(self._parse_list_product(item))
        return products

    def _parse_list_product(self, item: dict) -> RawSupplierProduct:
        return RawSupplierProduct(
            supplier_id="cj",
            supplier_product_id=item.get("id") or item.get("pid", ""),
            supplier_sku=item.get("sku") or item.get("spu", ""),
            title=item.get("nameEn", ""),
            description=item.get("description", ""),
            images=[item["bigImage"]] if item.get("bigImage") else [],
            category_name=item.get("threeCategoryName", ""),
            category_id=item.get("categoryId", ""),
            price_usd=_safe_float(item.get("sellPrice")),
            weight_grams=_safe_float(item.get("productWeight")),
            inventory_total=_safe_int(item.get("totalVerifiedInventory"))
            if item.get("totalVerifiedInventory") is not None
            else _safe_int(item.get("warehouseInventoryNum")),
            total_inventory=_safe_int(item.get("warehouseInventoryNum")),
            cj_inventory=_safe_int(item.get("totalVerifiedInventory")),
            factory_inventory=_safe_int(item.get("totalUnVerifiedInventory")),
            inventory_verification=_inventory_verification(item.get("verifiedWarehouse")),
            warehouse_country="CN",
            delivery_cycle_days=item.get("deliveryCycle", ""),
            raw_payload=item,
        )

    # ── product detail ───────────────────────────────────

    async def get_product(self, product_id: str, *, strict: bool = False) -> RawSupplierProduct | None:
        try:
            data = await self._get("/product/query", {"pid": product_id})
        except (CJAPIError, httpx.HTTPStatusError) as exc:
            status_code = (
                exc.details.http_status if isinstance(exc, CJAPIError) else exc.response.status_code
            )
            if status_code != 404:
                raise
            data = {"result": False, "data": None}
        if not data.get("result") or not data.get("data"):
            if strict:
                return None
            matches = await self.search_products(product_id, page_size=50)
            match = next(
                (
                    product
                    for product in matches
                    if product.supplier_product_id == product_id or product.supplier_sku == product_id
                ),
                None,
            )
            if match is None or match.supplier_product_id == product_id:
                return None
            data = await self._get("/product/query", {"pid": match.supplier_product_id})
        if not data.get("result") or not data.get("data"):
            return None

        item = data["data"]
        variants = [self._parse_variant(v) for v in item.get("variants") or []]
        for variant in variants:
            if variant.total_inventory is None:
                snapshot = await self.get_inventory(variant.supplier_variant_id)
                if snapshot is not None:
                    variant.total_inventory = snapshot.total_inventory
                    variant.cj_inventory = snapshot.cj_inventory
                    variant.factory_inventory = snapshot.factory_inventory
                    variant.inventory_verification = snapshot.verification_status
                    variant.inventory = snapshot.cj_inventory

        total_inventory = sum(v.total_inventory or 0 for v in variants) if variants else None
        cj_inventory = sum(v.cj_inventory or 0 for v in variants) if variants else None
        factory_inventory = sum(v.factory_inventory or 0 for v in variants) if variants else None

        return RawSupplierProduct(
            supplier_id="cj",
            supplier_product_id=item.get("pid", ""),
            supplier_sku=item.get("productSku", ""),
            title=item.get("productNameEn", ""),
            description=item.get("description", ""),
            images=item.get("productImageSet", []) or ([item["bigImage"]] if item.get("bigImage") else []),
            category_name=item.get("categoryName", ""),
            category_id=item.get("categoryId", ""),
            price_usd=_safe_float(item.get("sellPrice")),
            weight_grams=_safe_float(item.get("productWeight")),
            packing_weight_grams=_safe_float(item.get("packingWeight")),
            variants=variants,
            inventory_total=cj_inventory,
            total_inventory=total_inventory,
            cj_inventory=cj_inventory,
            factory_inventory=factory_inventory,
            inventory_verification=_inventory_verification(
                next((v.inventory_verification for v in variants if v.inventory_verification), None)
            ),
            warehouse_country="CN",
            delivery_cycle_days=item.get("deliveryCycle", ""),
            logistics_properties=item.get("productProEnSet", []) or [],
            raw_payload=item,
        )

    def _parse_variant(self, v: dict) -> RawVariant:
        inventory = 0
        total_inventory = 0
        cj_inventory = 0
        factory_inventory = 0
        has_inventory = False
        warehouse = "CN"
        warehouses: list[WarehouseInventorySnapshot] = []
        for inv in v.get("inventories") or []:
            has_inventory = True
            inv_total = _safe_int(inv.get("totalInventory")) or 0
            inv_cj = _safe_int(inv.get("cjInventory"))
            sellable = inv_cj if inv_cj is not None else inv_total
            country = str(inv.get("countryCode") or inv.get("warehouseCountry") or "CN")
            storage_id = _first_string(inv, "storageId", "warehouseId", "storageCode")
            warehouse_name = _first_string(inv, "storageName", "warehouseName", "name", "storage")
            status = _inventory_verification(inv.get("verifiedWarehouse"))
            warehouses.append(
                WarehouseInventorySnapshot(
                    warehouse_country=country,
                    storage_id=storage_id,
                    warehouse_name=warehouse_name,
                    total_inventory=inv_total,
                    cj_inventory=sellable,
                    factory_inventory=_safe_int(inv.get("factoryInventory")) or 0,
                    verification_status=status,
                )
            )
            total_inventory += inv_total
            cj_inventory += sellable
            factory_inventory += _safe_int(inv.get("factoryInventory")) or 0
            if sellable > 0:
                warehouse = country

        return RawVariant(
            supplier_variant_id=v.get("vid", ""),
            supplier_variant_sku=v.get("variantSku", ""),
            name=v.get("variantNameEn", ""),
            option_key=v.get("variantKey", ""),
            image=v.get("variantImage", ""),
            price_usd=_safe_float(v.get("variantSellPrice")),
            weight_grams=_safe_float(v.get("variantWeight")),
            length_mm=_safe_int(v.get("variantLength")),
            width_mm=_safe_int(v.get("variantWidth")),
            height_mm=_safe_int(v.get("variantHeight")),
            inventory=cj_inventory,
            total_inventory=total_inventory if has_inventory else None,
            cj_inventory=cj_inventory if has_inventory else None,
            factory_inventory=factory_inventory if has_inventory else None,
            inventory_verification=_inventory_verification(
                next((inv.get("verifiedWarehouse") for inv in v.get("inventories") or []), None)
            ),
            warehouse_country=warehouse,
            barcode=v.get("barcode", ""),
            warehouses=warehouses,
        )

    # ── variants ─────────────────────────────────────────

    async def get_variants(self, product_id: str) -> list[RawVariant]:
        data = await self._get("/product/variant/query", {"pid": product_id})
        if not data.get("result"):
            return []
        return [self._parse_variant(v) for v in data.get("data", [])]

    # ── inventory ────────────────────────────────────────

    async def get_inventory(self, variant_id: str, *, strict: bool = False) -> InventorySnapshot | None:
        data = await self._get("/product/stock/queryByVid", {"vid": variant_id})
        if not data.get("result"):
            return None
        entries = data.get("data")
        if strict and (not isinstance(entries, list) or not entries):
            return None
        total = 0
        cj_inventory = 0
        factory_inventory = 0
        verification_status: str | None = None
        warehouses: list[WarehouseInventorySnapshot] = []
        for entry in entries or []:
            if strict and any(
                type(entry.get(field)) is not int
                for field in ("totalInventoryNum", "cjInventoryNum", "factoryInventoryNum")
            ):
                return None
            entry_total = _safe_int(entry.get("totalInventoryNum")) or 0
            entry_cj = _safe_int(entry.get("cjInventoryNum")) or 0
            entry_factory = _safe_int(entry.get("factoryInventoryNum")) or 0
            country = str(entry.get("countryCode") or entry.get("warehouseCountry") or "CN")
            storage_id = _first_string(entry, "storageId", "warehouseId", "storageCode")
            warehouse_name = _first_string(entry, "storageName", "warehouseName", "storage")
            warehouses.append(
                WarehouseInventorySnapshot(
                    warehouse_country=country,
                    storage_id=storage_id,
                    warehouse_name=warehouse_name,
                    total_inventory=entry_total,
                    cj_inventory=entry_cj,
                    factory_inventory=entry_factory,
                    verification_status=_inventory_verification(entry.get("verifiedWarehouse")),
                )
            )
            total += entry_total
            cj_inventory += entry_cj
            factory_inventory += entry_factory
            status = _inventory_verification(entry.get("verifiedWarehouse"))
            if status == "verified":
                verification_status = status
            elif verification_status is None:
                verification_status = status
        return InventorySnapshot(
            total_inventory=total,
            cj_inventory=cj_inventory,
            factory_inventory=factory_inventory,
            verification_status=verification_status,
            warehouses=warehouses,
        )

    # ── shipping ─────────────────────────────────────────

    async def calculate_shipping(
        self,
        variant_id: str,
        destination_country: str,
        *,
        origin_country: str = "CN",
        quantity: int = 1,
    ) -> ShippingResult:
        try:
            data = await self._post(
                "/logistic/freightCalculate",
                {
                    "startCountryCode": origin_country,
                    "endCountryCode": destination_country,
                    "products": [{"vid": variant_id, "quantity": quantity}],
                },
            )
        except httpx.HTTPStatusError as exc:
            return ShippingResult(
                can_ship=False,
                validation=ShippingValidation.UNKNOWN,
                origin_country=origin_country,
                destination_country=destination_country,
                error=f"HTTP {exc.response.status_code}",
            )
        except CJAPIError as exc:
            return ShippingResult(
                can_ship=False,
                validation=ShippingValidation.UNKNOWN,
                origin_country=origin_country,
                destination_country=destination_country,
                error=exc.details.cj_message,
                error_details=exc.details,
            )

        if not data.get("result") or not data.get("data"):
            return ShippingResult(
                can_ship=False,
                validation=ShippingValidation.NOT_AVAILABLE,
                origin_country=origin_country,
                destination_country=destination_country,
                error=data.get("message", "No shipping options"),
            )

        options = [
            ShippingOption(
                carrier=opt.get("logisticName", "Unknown"),
                method=opt.get("logisticName", ""),
                cost_usd=_safe_float(opt.get("logisticPrice")) or 0.0,
                estimated_days=opt.get("logisticAging", "UNKNOWN"),
                storage_id=opt.get("storageId"),
                provider_metadata={
                    key: opt[key]
                    for key in ("channelId", "optionId", "logisticsModel")
                    if opt.get(key) is not None
                },
            )
            for opt in data["data"]
        ]

        return ShippingResult(
            can_ship=len(options) > 0,
            validation=ShippingValidation.VERIFIED if options else ShippingValidation.NOT_AVAILABLE,
            options=sorted(options, key=lambda o: o.cost_usd),
            origin_country=origin_country,
            destination_country=destination_country,
        )

    async def create_order(
        self, request: CJOrderRequest, *, version: Literal["V2", "V3"] = "V3"
    ) -> SupplierOrderResult:
        """Create an order using the verified current CJ V2/V3 contract.

        Payment is intentionally not selected here. The caller must implement and
        explicitly authorize the supplier-side payment flow before using this API.
        """
        try:
            path = CJ_ORDER_ENDPOINTS[version]
        except KeyError as exc:
            raise ValueError(f"Unsupported CJ order API version: {version}") from exc
        data = await self._post(path, build_cj_order_payload(request))
        if not data.get("result"):
            details = CJErrorDetails(
                http_status=None,
                cj_code=data.get("code"),
                cj_message=str(data.get("message", "CJ rejected order")),
                request_id=data.get("requestId"),
                endpoint=path,
                timestamp=datetime.now(timezone.utc).isoformat(),
                operation="POST",
            )
            return SupplierOrderResult(
                accepted=False,
                error=details.cj_message,
                error_details=details,
            )
        body = data.get("data") or {}
        supplier_order_id = body.get("orderId") or body.get("orderNum") or body.get("orderNumber")
        if not supplier_order_id:
            return SupplierOrderResult(accepted=False, error="CJ response did not include an order ID")
        return SupplierOrderResult(accepted=True, supplier_order_id=str(supplier_order_id), status="SUBMITTED")

    async def get_tracking(self, supplier_order_id: str) -> SupplierTrackingResult:
        # The repository has no verified CJ tracking endpoint or response contract.
        return SupplierTrackingResult(supported=False, error="CJ tracking endpoint is not verified in this integration")


def _safe_float(val: Any) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _safe_int(val: Any) -> int | None:
    if val is None:
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _token_is_valid() -> bool:
    return bool(_cached_access_token) and time.monotonic() < (
        _cached_token_expires_at - _TOKEN_REFRESH_SKEW_SECONDS
    )


def _inventory_verification(value: Any) -> str | None:
    if value in (1, "1", True):
        return "verified"
    if value in (2, "2", False):
        return "unverified"
    return None


def _first_string(payload: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if value is not None and str(value).strip():
            return str(value)
    return None


def _token_ttl_seconds(token_data: dict[str, Any]) -> float:
    expiry = token_data.get("accessTokenExpiryDate") or token_data.get("accessTokenExpiry")
    if isinstance(expiry, (int, float)):
        if expiry > time.time():
            return max(expiry - time.time(), _TOKEN_REFRESH_SKEW_SECONDS)
        return max(float(expiry), _TOKEN_REFRESH_SKEW_SECONDS)
    if isinstance(expiry, str):
        try:
            expiry_time = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
            if expiry_time.tzinfo is None:
                expiry_time = expiry_time.replace(tzinfo=timezone.utc)
            return max(expiry_time.timestamp() - time.time(), _TOKEN_REFRESH_SKEW_SECONDS)
        except ValueError:
            pass
    return _DEFAULT_TOKEN_TTL_SECONDS
