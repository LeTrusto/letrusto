from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class CatalogEnrichmentRequest:
    product_id: str
    title: str
    description: str
    supplier_category: str | None
    variants: list[dict[str, Any]]


@dataclass(frozen=True, slots=True)
class CatalogEnrichmentResult:
    content: dict[str, Any]
    provider: str


class CatalogEnrichmentProvider(Protocol):
    name: str

    def generate(self, request: CatalogEnrichmentRequest) -> CatalogEnrichmentResult:
        ...


class MockCatalogEnrichmentProvider:
    name = "mock-catalog-enrichment"

    def generate(self, request: CatalogEnrichmentRequest) -> CatalogEnrichmentResult:
        title = request.title.strip()
        return CatalogEnrichmentResult(
            provider=self.name,
            content={
                "category": "home-kitchen",
                "subcategory": "bar-accessories",
                "title": f"{title} for Kitchen and Bar Use",
                "description": (
                    f"Make everyday hosting easier with the {title.lower()}, designed for convenient use "
                    "at home, in the kitchen, or behind the bar."
                ),
                "key_features": [
                    "Practical kitchen and bar accessory",
                    "Easy to use for everyday hosting",
                    "Compact design for convenient storage",
                ],
                "attributes": {
                    "product_type": "Bottle opener",
                    "recommended_use": "Kitchen and bar",
                    "material": "Metal",
                },
                "seo_title": f"{title} | LeTrusto",
                "seo_meta_description": f"Shop the {title.lower()} for convenient kitchen and bar use.",
                "search_keywords": ["bottle opener", "bar accessories", "kitchen tools"],
            },
        )


def build_catalog_enrichment_provider() -> CatalogEnrichmentProvider:
    return MockCatalogEnrichmentProvider()
