"""CJDropshipping API adapter — Phase 2 validation prototype."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.suppliers.base import (
    RawSupplierProduct,
    RawVariant,
    ShippingOption,
    ShippingResult,
    ShippingValidation,
    SupplierCategory,
)

logger = logging.getLogger(__name__)

_BASE_URL = "https://developers.cjdropshipping.com/api2.0/v1"


class CJAdapter:
    supplier_name = "cj"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._access_token: str = ""

    # ── helpers ──────────────────────────────────────────

    def _headers(self) -> dict[str, str]:
        h: dict[str, str] = {"Content-Type": "application/json"}
        if self._access_token:
            h["CJ-Access-Token"] = self._access_token
        return h

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{_BASE_URL}{path}", headers=self._headers(), params=params)
            resp.raise_for_status()
            return resp.json()

    async def _post(self, path: str, json_body: dict | None = None) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{_BASE_URL}{path}", headers=self._headers(), json=json_body or {})
            resp.raise_for_status()
            return resp.json()

    # ── authentication ───────────────────────────────────

    async def authenticate(self) -> bool:
        data = await self._post("/authentication/getAccessToken", {"apiKey": self._api_key})
        if data.get("result") and data.get("data"):
            self._access_token = data["data"]["accessToken"]
            logger.info("CJ authentication successful")
            return True
        logger.error("CJ authentication failed: %s", data.get("message"))
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
            inventory_total=_safe_int(item.get("warehouseInventoryNum")),
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
        variants = [self._parse_variant(v) for v in item.get("variants", [])]

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
            inventory_total=sum(v.inventory or 0 for v in variants) if variants else None,
            warehouse_country="CN",
            delivery_cycle_days=item.get("deliveryCycle", ""),
            logistics_properties=item.get("productProEnSet", []) or [],
            raw_payload=item,
        )

    def _parse_variant(self, v: dict) -> RawVariant:
        inventory = 0
        warehouse = "CN"
        for inv in v.get("inventories", []):
            inventory += inv.get("totalInventory", 0)
            if inv.get("totalInventory", 0) > 0:
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
            inventory=inventory,
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

    async def get_inventory(self, variant_id: str) -> int | None:
        data = await self._get("/product/stock/queryByVid", {"vid": variant_id})
        if not data.get("result"):
            return None
        total = 0
        for entry in data.get("data", []):
            total += entry.get("totalInventoryNum", 0)
        return total

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
