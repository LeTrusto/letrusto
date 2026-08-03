from dataclasses import dataclass
from decimal import Decimal

from app.core.exceptions import NotFoundError
from app.models.entities import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.common import Pagination
from app.schemas.product import (
    CatalogMetadataResponse,
    CompareResponse,
    HomeCollectionsResponse,
    PaginatedProductsResponse,
    ProductDTO,
    ProductSearchQuery,
)
from app.services.product_mapper import to_product_dto


CATEGORY_LABELS = {
    # Existing leaf categories
    "phone": "Phone",
    "laptop": "Laptop",
    "headphones": "Headphones",
    "smartwatch": "Smart Watch",
    "television": "Television",
    "refrigerator": "Refrigerator",
    "washing-machine": "Washing Machine",
    "gaming": "Gaming",
    "tablet": "Tablet",
    "camera": "Camera",
    # Phase 6.1 top-level
    "electronics": "Electronics",
    "home-kitchen": "Home & Kitchen",
    "beauty": "Beauty",
    "baby-care": "Baby Care",
    "pet-care": "Pet Care",
    "fitness": "Fitness",
    "furniture": "Furniture",
    # Phase 6.1 sub-categories
    "smartphones": "Smartphones",
    "laptops-ultrabooks": "Laptops",
    "tablets-ipads": "Tablets",
    "earbuds-tws": "Earbuds",
    "smartwatches-bands": "Smartwatches",
    "digital-cameras": "Cameras",
    "bluetooth-speakers": "Speakers",
    "monitors-displays": "Monitors",
    "televisions-oleds": "Televisions",
}

CATEGORY_PLURAL_LABELS = {
    "phone": "Phones",
    "laptop": "Laptops",
    "headphones": "Headphones",
    "smartwatch": "Smart Watches",
    "television": "Televisions",
    "refrigerator": "Refrigerators",
    "washing-machine": "Washing Machines",
    "gaming": "Gaming",
    "tablet": "Tablets",
    "camera": "Cameras",
    "electronics": "Electronics",
    "home-kitchen": "Home & Kitchen",
    "smartphones": "Smartphones",
    "laptops-ultrabooks": "Laptops & Ultrabooks",
    "tablets-ipads": "Tablets & iPads",
    "earbuds-tws": "Earbuds & TWS",
    "smartwatches-bands": "Smartwatches & Bands",
    "digital-cameras": "Cameras",
    "bluetooth-speakers": "Speakers",
    "monitors-displays": "Monitors",
    "televisions-oleds": "Televisions",
}


@dataclass
class RankedProduct:
    product: Product
    score: float


class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository

    def list_products(self, ids: list[str] | None = None) -> list[ProductDTO]:
        products = self.repository.list_products(ids)
        return [self._to_dto(product) for product in products]

    def get_product(self, product_slug: str) -> ProductDTO:
        product = self.repository.get_by_slug(product_slug)
        if not product:
            raise NotFoundError(f"Product '{product_slug}' not found")
        return self._to_dto(product)

    def get_search(self, query: ProductSearchQuery) -> PaginatedProductsResponse:
        products = self.repository.search_candidates(query)
        ranked = [RankedProduct(product=p, score=self._score_product(p, query.q)) for p in products]

        ranked = self._sort_ranked(ranked, query.sort)
        total_items = len(ranked)
        total_pages = max(1, (total_items + query.pageSize - 1) // query.pageSize)
        page = min(query.page, total_pages)
        start = (page - 1) * query.pageSize
        end = start + query.pageSize
        paged = ranked[start:end]

        return PaginatedProductsResponse(
            items=[self._to_dto(item.product) for item in paged],
            pagination=Pagination(
                page=page,
                pageSize=query.pageSize,
                totalItems=total_items,
                totalPages=total_pages,
                hasNextPage=page < total_pages,
                hasPreviousPage=page > 1,
            ),
        )

    def get_recommendations(self, q: str, limit: int = 4) -> list[ProductDTO]:
        # Keep this aligned with ProductSearchQuery constraints (pageSize <= 100).
        query = ProductSearchQuery(q=q, page=1, pageSize=100)
        products = self.repository.search_candidates(query)

        ranked = [RankedProduct(product=p, score=self._score_product(p, q) + p.ai_score / 10) for p in products]
        ranked = sorted(ranked, key=lambda item: item.score, reverse=True)

        return [self._to_dto(item.product) for item in ranked[: max(1, limit)]]

    def get_related(self, product_slug: str, limit: int = 4) -> list[ProductDTO]:
        product = self.repository.get_by_slug(product_slug)
        if not product:
            raise NotFoundError(f"Product '{product_slug}' not found")

        similar_slugs = self.repository.get_similar_slugs(product.id)
        if similar_slugs:
            similar = [p for p in self.repository.list_products(similar_slugs) if p.slug != product_slug]
            return [self._to_dto(item) for item in similar[: max(1, limit)]]

        fallback = [
            p for p in self.repository.list_products() if p.slug != product_slug and p.category_id == product.category_id
        ]
        fallback = sorted(fallback, key=lambda item: (item.ai_score, item.rating), reverse=True)
        return [self._to_dto(item) for item in fallback[: max(1, limit)]]

    def get_compare(self, first: str | None, second: str | None) -> CompareResponse:
        all_products = self.repository.list_products()
        if not all_products:
            raise NotFoundError("No products found in catalog")

        first_product = self.repository.get_by_slug(first) if first else all_products[0]
        if not first_product:
            first_product = all_products[0]

        if second:
            second_product = self.repository.get_by_slug(second)
            if second_product and second_product.slug == first_product.slug:
                second_product = None
        else:
            second_product = None

        if not second_product:
            second_product = next((p for p in all_products if p.slug != first_product.slug), first_product)

        return CompareResponse(
            firstProduct=self._to_dto(first_product),
            secondProduct=self._to_dto(second_product),
        )

    def get_suggestions(self, limit: int = 24) -> list[str]:
        products = self.repository.list_products()
        return [p.name for p in products[: max(1, limit)]]

    def get_home_collections(self) -> HomeCollectionsResponse:
        products = self.repository.list_products()
        featured = products[:4]
        top_ai = sorted(products, key=lambda p: p.ai_score, reverse=True)

        return HomeCollectionsResponse(
            featured=[self._to_dto(product) for product in featured],
            newArrivals=[self._to_dto(product) for product in top_ai[4:8]],
            topAiPicks=[self._to_dto(product) for product in top_ai[:4]],
            trending=[self._to_dto(product) for product in products[:8]],
        )

    def get_metadata(self) -> CatalogMetadataResponse:
        brands = self.repository.get_brands()
        spotlight = {
            "iphone16pro": "Flagship Pick",
            "galaxy-s25": "Best Seller",
            "nothing-phone-2a": "Budget Favorite",
            "macbook-air-m4": "AI Pick",
            "asus-zenbook-14-oled": "Creator Choice",
            "sony-wh-1000xm6": "Top Rated",
            "bose-qc-ultra": "Travel Favorite",
            "ps5-slim": "Gaming Hit",
            "ipad-air-m2": "Student Pick",
            "sony-a7-iv": "Pro Camera",
        }

        return CatalogMetadataResponse(
            categoryLabels=CATEGORY_LABELS,
            categoryPluralLabels=CATEGORY_PLURAL_LABELS,
            productSpotlightBadges=spotlight,
            brands=brands,
        )

    def _to_dto(self, product: Product) -> ProductDTO:
        similar_slugs = self.repository.get_similar_slugs(product.id)
        return to_product_dto(product, similar_slugs=similar_slugs)

    def _score_product(self, product: Product, query: str) -> float:
        normalized = query.lower().strip()
        if not normalized:
            return 0

        tokens = [token for token in normalized.split() if token]
        score = 0.0

        haystack = " ".join(
            filter(None, [
                product.name.lower(),
                product.description.lower(),
                product.brand.name.lower(),
                product.category.slug.lower(),
                product.series.lower() if product.series else None,
                product.model_name.lower() if product.model_name else None,
                " ".join(item.value.lower() for item in product.tags),
                " ".join(item.value.lower() for item in product.features),
            ])
        )

        if normalized in product.name.lower():
            score += 60
        if normalized in product.brand.name.lower():
            score += 24
        if product.series and normalized in product.series.lower():
            score += 20
        if product.model_name and normalized in product.model_name.lower():
            score += 18
        if normalized in product.category.slug.lower():
            score += 16

        for token in tokens:
            if token in haystack:
                score += 9
            if token in product.name.lower():
                score += 12

        return score

    def _sort_ranked(self, ranked: list[RankedProduct], sort_option: str) -> list[RankedProduct]:
        if sort_option == "price-low":
            return sorted(ranked, key=lambda item: item.product.price_value)
        if sort_option == "price-high":
            return sorted(ranked, key=lambda item: item.product.price_value, reverse=True)
        if sort_option == "rating-high":
            return sorted(ranked, key=lambda item: item.product.rating, reverse=True)
        if sort_option == "ai-high":
            return sorted(ranked, key=lambda item: item.product.ai_score, reverse=True)

        return sorted(
            ranked,
            key=lambda item: (item.score, item.product.ai_score, item.product.rating),
            reverse=True,
        )
