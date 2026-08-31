from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.entities import PrintfulShippingRate, Product

REGIONS = ("IN", "US", "GB", "EU", "CA", "AU_NZ", "JP", "BR", "WORLDWIDE")
REGION_LABELS = {
    "IN": "India", "US": "United States", "GB": "United Kingdom", "EU": "European Union",
    "CA": "Canada", "AU_NZ": "Australia / New Zealand", "JP": "Japan", "BR": "Brazil",
    "WORLDWIDE": "Rest of World",
}
EU_COUNTRIES = {"AT", "BE", "BG", "HR", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}
FALLBACK_COUNTRIES = {"CH", "NO", "IS", "LI", "SG", "MY", "MX", "ZA", "AE", "HK", "TW", "KR"}
STALE_AFTER_DAYS = 30
COUNTRY_REGION = {"IN": "IN", "US": "US", "GB": "GB", "CA": "CA", "AU": "AU_NZ", "NZ": "AU_NZ", "JP": "JP", "BR": "BR"}
COUNTRY_REGION.update({country: "EU" for country in EU_COUNTRIES})
COUNTRY_REGION.update({country: "WORLDWIDE" for country in FALLBACK_COUNTRIES})


def region_for_country(country: str) -> str | None:
    code = country.strip().upper()
    return COUNTRY_REGION.get(code)


class PrintfulShippingService:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def category_for(product: Product) -> str:
        return "hoodies-sweatshirts" if "hoodie" in product.name.lower() else "default"

    def _rows(self, product: Product) -> list[PrintfulShippingRate]:
        category = self.category_for(product)
        rows = list(self.db.scalars(select(PrintfulShippingRate).where(
            PrintfulShippingRate.source == "printful", PrintfulShippingRate.active.is_(True),
            PrintfulShippingRate.category_key == category,
            (PrintfulShippingRate.product_id == product.id) | PrintfulShippingRate.product_id.is_(None),
        ).order_by(PrintfulShippingRate.product_id.desc())).all())
        return rows

    def review(self, product: Product) -> tuple[bool, list[str]]:
        rows = {row.destination_region: row for row in self._rows(product)}
        blockers = []
        for region in REGIONS:
            row = rows.get(region)
            if row is None:
                blockers.append(f"SHIPPING_RATE_MISSING_{region}")
                continue
            if row.source != "printful" or (not row.country_codes and not (region == "IN" and row.requires_verification)):
                blockers.append(f"SHIPPING_DESTINATION_MAPPING_INVALID_{region}")
            if row.currency != "USD":
                blockers.append(f"SHIPPING_CURRENCY_INVALID_{region}")
            if row.requires_verification:
                if region != "IN": blockers.append(f"SHIPPING_VERIFICATION_REQUIRED_{region}")
            elif row.single_product_rate is None or row.additional_product_rate is None:
                blockers.append(f"SHIPPING_RATE_INCOMPLETE_{region}")
            if row.effective_at > datetime.now(timezone.utc):
                blockers.append(f"SHIPPING_EFFECTIVE_DATE_INVALID_{region}")
            elif (datetime.now(timezone.utc) - row.updated_at).days > STALE_AFTER_DAYS:
                blockers.append(f"SHIPPING_RATE_STALE_{region}")
        return not blockers, blockers

    def list_for_product(self, product: Product) -> list[dict]:
        rows = {row.destination_region: row for row in self._rows(product)}
        return [self._serialize(rows.get(region), region) for region in REGIONS]

    def estimate(self, product: Product, country: str, quantity: int = 1) -> dict:
        region = region_for_country(country)
        if region is None:
            raise BadRequestError("Destination country is required")
        row = {item["region"]: item for item in self.list_for_product(product)}.get(region)
        if not row or row["requires_verification"]:
            return {"country": country.upper(), "region": region, "status": "REQUIRES_VERIFICATION", "message": "Shipping rate requires Printful verification"}
        return {"country": country.upper(), "region": region, "status": "AVAILABLE", "currency": row["currency"], "shipping_method": row["shipping_method"], "shipping_price": row["single_product_rate"] + max(quantity - 1, 0) * row["additional_product_rate"], "estimated_delivery": None}

    @staticmethod
    def _serialize(row: PrintfulShippingRate | None, region: str) -> dict:
        return {
            "region": region, "label": REGION_LABELS[region], "status": "REQUIRES_VERIFICATION" if row and row.requires_verification else "AVAILABLE" if row else "MISSING",
            "shipping_method": row.shipping_method if row else None, "single_product_rate": row.single_product_rate if row else None,
            "additional_product_rate": row.additional_product_rate if row else None, "currency": row.currency if row else "USD",
            "country_codes": row.country_codes if row else [], "source": row.source if row else "printful",
            "effective_at": row.effective_at if row else None, "updated_at": row.updated_at if row else None,
            "active": row.active if row else False, "requires_verification": row.requires_verification if row else False,
        }

    def update(self, product: Product, payload: dict) -> dict:
        region = payload["region"]
        if region not in REGIONS: raise BadRequestError("Unsupported Printful destination region")
        row = self.db.scalar(select(PrintfulShippingRate).where(PrintfulShippingRate.category_key == self.category_for(product), PrintfulShippingRate.destination_region == region, PrintfulShippingRate.product_id.is_(None)))
        if row is None:
            row = PrintfulShippingRate(category_key=self.category_for(product), destination_region=region)
            self.db.add(row)
        row.source = "printful"; row.country_codes = [code.upper() for code in payload["country_codes"]]; row.shipping_method = payload["shipping_method"]
        row.single_product_rate = payload.get("single_product_rate"); row.additional_product_rate = payload.get("additional_product_rate"); row.currency = payload["currency"]; row.effective_at = payload.get("effective_at") or datetime.now(timezone.utc); row.active = payload["active"]; row.requires_verification = payload["requires_verification"]
        self.db.commit(); self.db.refresh(row)
        return self._serialize(row, region)