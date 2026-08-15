"""CJDropshipping API adapter — Phase 2 validation prototype."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from app.suppliers.base import (
    InventorySnapshot,
    RawSupplierProduct,
    RawVariant,
    ShippingOption,
    ShippingResult,
    ShippingValidation,
    SupplierCategory,
)

logger = logging.getLogger(__name__)

_BASE_URL = "https://developers.cjdropshipping.com/api2.0/v1"
_DEFAULT_TOKEN_TTL_SECONDS = 900
_TOKEN_REFRESH_SKEW_SECONDS = 30
_cached_access_token = ""
_cached_token_expires_at = 0.0


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

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{_BASE_URL}{path}", headers=self._headers(), params=params)
            if resp.status_code == 401 and path != "/authentication/getAccessToken":
                await self.authenticate(force=True)
                resp = await client.get(f"{_BASE_URL}{path}", headers=self._headers(), params=params)
            resp.raise_for_status()
            return resp.json()

    async def _post(self, path: str, json_body: dict | None = None) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{_BASE_URL}{path}", headers=self._headers(), json=json_body or {})
            if resp.status_code == 401 and path != "/authentication/getAccessToken":
                await self.authenticate(force=True)
                resp = await client.post(f"{_BASE_URL}{path}", headers=self._headers(), json=json_body or {})
            resp.raise_for_status()
            return resp.json()

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
            supplier_product_id=item.get("id", ""),
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

    async def get_product(self, product_id: str) -> RawSupplierProduct | None:
        data = await self._get("/product/query", {"pid": product_id})
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
        for inv in v.get("inventories") or []:
            has_inventory = True
            inv_total = _safe_int(inv.get("totalInventory")) or 0
            inv_cj = _safe_int(inv.get("cjInventory"))
            total_inventory += inv_total
            cj_inventory += inv_cj if inv_cj is not None else inv_total
            factory_inventory += _safe_int(inv.get("factoryInventory")) or 0
            if (inv_cj if inv_cj is not None else inv_total) > 0:
                warehouse = inv.get("countryCode", "CN")

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
        )

    # ── variants ─────────────────────────────────────────

    async def get_variants(self, product_id: str) -> list[RawVariant]:
        data = await self._get("/product/variant/query", {"pid": product_id})
        if not data.get("result"):
            return []
        return [self._parse_variant(v) for v in data.get("data", [])]

    # ── inventory ────────────────────────────────────────

    async def get_inventory(self, variant_id: str) -> InventorySnapshot | None:
        data = await self._get("/product/stock/queryByVid", {"vid": variant_id})
        if not data.get("result"):
            return None
        total = 0
        cj_inventory = 0
        factory_inventory = 0
        verification_status: str | None = None
        for entry in data.get("data", []):
            total += _safe_int(entry.get("totalInventoryNum")) or 0
            cj_inventory += _safe_int(entry.get("cjInventoryNum")) or 0
            factory_inventory += _safe_int(entry.get("factoryInventoryNum")) or 0
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
