"""Printful API adapter for catalog, shipping, and fulfillment."""

from __future__ import annotations

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
    SupplierOrderResult,
    SupplierTrackingResult,
)

_BASE_URL = "https://api.printful.com"
FINALIZED_PRODUCT_NAMES = {
    "men's premium tank top",
    "unisex hoodie",
    "unisex premium sweatshirt",
    "unisex organic oversized high-neck t-shirt",
}


class PrintfulAdapter:
    supplier_name = "printful"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key.strip()
        if not self._api_key:
            raise ValueError("Printful API key is not configured")

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

    async def _request(
        self, method: str, path: str, *, params: dict[str, Any] | None = None, body: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(method, f"{_BASE_URL}{path}", headers=self._headers(), params=params, json=body)
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, dict) or payload.get("code", 200) >= 400:
            raise ValueError("Printful API returned an invalid response")
        result = payload.get("result", {})
        return result if isinstance(result, dict) else {"data": result}

    async def authenticate(self) -> bool:
        try:
            await self._request("GET", "/stores")
        except (httpx.HTTPError, ValueError, TypeError):
            return False
        return True

    async def connection_status(self) -> dict[str, str]:
        result = await self._request("GET", "/stores")
        stores = result.get("data", result.get("stores", []))
        store = stores[0] if isinstance(stores, list) and stores and isinstance(stores[0], dict) else {}
        return {
            "status": "Connected",
            "store": str(store.get("name") or store.get("store_name") or "Printful store"),
            "health": "Healthy",
        }

    async def list_store_products(self) -> list[RawSupplierProduct]:
        result = await self._request("GET", "/store/products")
        products = result.get("data", result.get("sync_products", []))
        if not isinstance(products, list):
            return []
        return [self._parse_store_product_summary(item) for item in products if isinstance(item, dict)]

    async def list_finalized_store_products(self) -> list[RawSupplierProduct]:
        products = await self.list_store_products()
        return [product for product in products if product.title.strip().lower() in FINALIZED_PRODUCT_NAMES]

    async def get_categories(self) -> list[SupplierCategory]:
        return []

    async def search_products(
        self, keyword: str, *, category_id: str = "", page: int = 1, page_size: int = 20
    ) -> list[RawSupplierProduct]:
        products = await self.list_store_products()
        normalized_keyword = keyword.strip().lower()
        return [
            product
            for product in products
            if not normalized_keyword or normalized_keyword in product.title.lower()
        ]

    async def get_product(self, product_id: str, *, strict: bool = False) -> RawSupplierProduct | None:
        try:
            result = await self._request("GET", f"/store/products/{product_id}")
        except (httpx.HTTPError, ValueError):
            if strict:
                raise
            return None
        product = result.get("sync_product", result.get("product", {}))
        if not isinstance(product, dict):
            return None
        variants = result.get("sync_variants", result.get("variants", []))
        return self._parse_store_product(product, variants if isinstance(variants, list) else [], result)

    async def get_variants(self, product_id: str) -> list[RawVariant]:
        product = await self.get_product(product_id)
        return product.variants if product else []

    async def get_inventory(self, variant_id: str, *, strict: bool = False) -> InventorySnapshot | None:
        try:
            result = await self._request("GET", f"/products/variant/{variant_id}")
        except (httpx.HTTPError, ValueError):
            if strict:
                raise
            return None
        variant = result.get("variant", {})
        inventory = variant.get("availability") if isinstance(variant, dict) else None
        quantity = int(inventory) if isinstance(inventory, (int, float, str)) and str(inventory).isdigit() else 0
        return InventorySnapshot(total_inventory=quantity, cj_inventory=quantity, factory_inventory=0)

    async def calculate_shipping(
        self, variant_id: str, destination_country: str, *, origin_country: str = "", quantity: int = 1
    ) -> ShippingResult:
        result = await self._request(
            "POST",
            "/shipping/rates",
            body={
                "recipient": {"country_code": destination_country.upper()},
                "items": [{"variant_id": int(variant_id), "quantity": quantity}],
            },
        )
        rates = result.get("rates", [])
        options = [
            ShippingOption(
                carrier=str(rate.get("carrier", "Printful")),
                method=str(rate.get("name", rate.get("service", "Printful shipping"))),
                cost_usd=float(rate.get("rate", 0)),
                estimated_days=str(rate.get("delivery_days", "")),
                provider_metadata={"id": rate.get("id", "")},
            )
            for rate in rates
            if isinstance(rate, dict) and rate.get("rate") is not None
        ]
        return ShippingResult(
            can_ship=bool(options),
            validation=ShippingValidation.VERIFIED if options else ShippingValidation.NOT_AVAILABLE,
            options=options,
            origin_country=origin_country,
            destination_country=destination_country.upper(),
        )

    async def create_order(self, payload: dict) -> SupplierOrderResult:
        external_id = str(payload.get("orderNumber", ""))
        if external_id:
            try:
                existing = await self._request("GET", "/orders", params={"external_id": external_id})
            except (httpx.HTTPError, ValueError, TypeError):
                existing = {}
            orders = existing.get("data", existing.get("orders", []))
            if isinstance(orders, list):
                match = next((item for item in orders if isinstance(item, dict) and str(item.get("external_id", "")) == external_id), None)
                if match and match.get("id"):
                    return SupplierOrderResult(
                        accepted=True,
                        supplier_order_id=str(match["id"]),
                        status=str(match.get("status", "SUBMITTED")),
                        supplier_status=str(match.get("status", "")) or None,
                    )
        items = [
            {"variant_id": int(item["vid"]), "quantity": item["quantity"]}
            for item in payload.get("products", [])
        ]
        result = await self._request(
            "POST",
            "/orders",
            body={
                "external_id": external_id,
                "recipient": {
                    "name": payload.get("shippingCustomerName", ""),
                    "phone": payload.get("shippingPhone", ""),
                    "address1": payload.get("shippingAddress", ""),
                    "city": payload.get("shippingCity", ""),
                    "state_code": payload.get("shippingProvince", ""),
                    "zip": payload.get("shippingZip", ""),
                    "country_code": payload.get("shippingCountryCode", ""),
                },
                "items": items,
                "confirm": False,
            },
        )
        order_id = result.get("id")
        return SupplierOrderResult(
            accepted=bool(order_id),
            supplier_order_id=str(order_id) if order_id else None,
            status=str(result.get("status", "SUBMITTED")),
            supplier_status=str(result.get("status", "")) or None,
        )

    async def get_tracking(self, supplier_order_id: str) -> SupplierTrackingResult:
        result = await self._request("GET", f"/orders/{supplier_order_id}")
        shipments = result.get("shipments", [])
        shipment = shipments[0] if shipments and isinstance(shipments[0], dict) else {}
        return SupplierTrackingResult(
            supported=True,
            supplier_status=str(result.get("status", "")) or None,
            tracking_number=shipment.get("tracking_number"),
            carrier=shipment.get("carrier"),
        )

    async def add_to_cart(self, supplier_order_id: str) -> SupplierOrderResult:
        return SupplierOrderResult(accepted=False, error="Printful does not use a cart flow")

    async def confirm_order(self, supplier_order_id: str) -> SupplierOrderResult:
        result = await self._request("POST", f"/orders/{supplier_order_id}/confirm")
        return SupplierOrderResult(accepted=True, supplier_order_id=supplier_order_id, status=str(result.get("status", "SUBMITTED")))

    async def generate_parent_order(self, supplier_order_id: str) -> SupplierOrderResult:
        return SupplierOrderResult(accepted=False, error="Printful does not use parent orders")

    async def pay_balance(self, shipment_order_id: str, pay_id: str | None = None) -> SupplierOrderResult:
        return SupplierOrderResult(accepted=False, error="Printful supplier payment is not required")

    async def get_balance(self):
        from app.suppliers.base import SupplierBalanceResult

        return SupplierBalanceResult(supported=False, error="Printful supplier payment is not required")

    async def get_order_status(self, supplier_order_id: str) -> SupplierOrderResult:
        result = await self._request("GET", f"/orders/{supplier_order_id}")
        return SupplierOrderResult(
            accepted=True,
            supplier_order_id=supplier_order_id,
            status=str(result.get("status", "UNKNOWN")),
            supplier_status=str(result.get("status", "")) or None,
        )

    @staticmethod
    def _parse_store_product_summary(product: dict[str, Any]) -> RawSupplierProduct:
        product_id = str(product.get("id", ""))
        return RawSupplierProduct(
            supplier_id="printful",
            supplier_product_id=product_id,
            supplier_sku=str(product.get("external_id", product_id)),
            title=str(product.get("name", product.get("title", ""))),
            images=[str(product["thumbnail_url"])] if product.get("thumbnail_url") else [],
            raw_payload={"sync_product": product},
        )

    @staticmethod
    def _parse_store_product(product: dict[str, Any], variants: list[dict[str, Any]], payload: dict[str, Any]) -> RawSupplierProduct:
        parsed_variants = [PrintfulAdapter._parse_store_variant(item) for item in variants if isinstance(item, dict)]
        product_id = str(product.get("id", ""))
        images = [str(product["thumbnail_url"])] if product.get("thumbnail_url") else []
        images.extend(str(variant.image) for variant in parsed_variants if variant.image and variant.image not in images)
        variant_prices = [variant.price_usd for variant in parsed_variants if variant.price_usd is not None]
        return RawSupplierProduct(
            supplier_id="printful",
            supplier_product_id=product_id,
            supplier_sku=str(product.get("external_id", product_id)),
            title=str(product.get("name", product.get("title", ""))),
            description=str(product.get("description", "")),
            images=images,
            variants=parsed_variants,
            price_usd=min(variant_prices) if variant_prices else None,
            inventory_verification="POD_ON_DEMAND",
            raw_payload=payload,
        )

    @staticmethod
    def _parse_product(product: dict[str, Any], variants: list[dict[str, Any]] | None = None) -> RawSupplierProduct:
        parsed_variants = [PrintfulAdapter._parse_variant(item) for item in (variants or product.get("variants", [])) if isinstance(item, dict)]
        product_id = str(product.get("id", ""))
        return RawSupplierProduct(
            supplier_id="printful",
            supplier_product_id=product_id,
            supplier_sku=str(product.get("model", product_id)),
            title=str(product.get("title", product.get("name", ""))),
            description=str(product.get("description", "")),
            images=[str(product["image"]) ] if product.get("image") else [],
            variants=parsed_variants,
        )

    @staticmethod
    def _parse_variant(variant: dict[str, Any]) -> RawVariant:
        variant_id = str(variant.get("id", ""))
        return RawVariant(
            supplier_variant_id=variant_id,
            supplier_variant_sku=str(variant.get("sku", variant_id)),
            name=str(variant.get("name", "")),
            image=str(variant.get("image", "")),
            price_usd=float(variant["price"]) if variant.get("price") is not None else None,
            inventory=int(variant.get("availability", 0) or 0),
        )

    @staticmethod
    def _parse_store_variant(variant: dict[str, Any]) -> RawVariant:
        sync_variant_id = str(variant.get("id", ""))
        catalog_variant_id = str(variant.get("variant_id", ""))
        options = variant.get("options") if isinstance(variant.get("options"), list) else []
        option_parts = [f"{item.get('id')}: {item.get('value')}" for item in options if isinstance(item, dict) and item.get("value")]
        if catalog_variant_id:
            option_parts.append(f"catalog_variant_id: {catalog_variant_id}")
        files = variant.get("files") if isinstance(variant.get("files"), list) else []
        image = ""
        for file_item in files:
            if isinstance(file_item, dict) and file_item.get("preview_url"):
                image = str(file_item["preview_url"])
                break
        return RawVariant(
            supplier_variant_id=sync_variant_id,
            supplier_variant_sku=str(variant.get("sku") or variant.get("external_id") or sync_variant_id),
            name=str(variant.get("name", "")),
            option_key=" / ".join(option_parts),
            image=image,
            price_usd=float(variant["retail_price"]) if variant.get("retail_price") is not None else None,
            inventory_verification=str(variant.get("availability_status") or "POD_ON_DEMAND"),
        )

