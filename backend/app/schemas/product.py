from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import Pagination


ProductSortOption = Literal["relevance", "price-low", "price-high", "rating-high", "ai-high"]
ProductPriceFilter = Literal["all", "under-30000", "30000-80000", "above-80000"]
ProductRatingFilter = Literal["all", "4-plus", "4.5-plus"]
ProductAiScoreFilter = Literal["all", "above-90"]


class ProductSpecificationDTO(BaseModel):
    label: str
    value: str


class ProductPriceHistoryDTO(BaseModel):
    label: str
    price: Decimal


class ProductReviewDTO(BaseModel):
    author: str
    title: str
    rating: Decimal
    comment: str
    date: str


class ProductBuyLinkDTO(BaseModel):
    id: int = 0
    label: str
    href: str
    retailer_type: str = "marketplace"
    is_affiliate: bool = True
    click_count: int = 0


class ProductDTO(BaseModel):
    id: str
    name: str
    brand: str
    price: str
    priceValue: Decimal
    image: str
    images: list[str]
    fallbackImage: str
    category: str
    parentCategory: str | None = None
    availability: str
    description: str
    features: list[str]
    aiScore: int
    rating: Decimal
    specs: list[ProductSpecificationDTO]
    pros: list[str]
    cons: list[str]
    aiSummary: str
    bestFor: list[str]
    notRecommendedFor: list[str]
    tags: list[str]
    amazonAsin: str | None = None
    amazonAffiliateUrl: str | None = None
    flipkartAffiliateUrl: str | None = None
    # Phase 6.1 catalog fields
    series: str | None = None
    modelName: str | None = None
    variant: str | None = None
    storage: str | None = None
    ram: str | None = None
    color: str | None = None
    priceHistory: list[ProductPriceHistoryDTO]
    reviews: list[ProductReviewDTO]
    reviewSummary: str
    buyLinks: list[ProductBuyLinkDTO]
    similarProductIds: list[str]


class ProductSearchQuery(BaseModel):
    q: str = ""
    sort: ProductSortOption = "relevance"
    category: str = "all"
    subcategory: str | None = None
    series: str | None = None
    price: ProductPriceFilter = "all"
    rating: ProductRatingFilter = "all"
    aiScore: ProductAiScoreFilter = "all"
    brand: str | None = None
    minPrice: int | None = Field(default=None, ge=0)
    maxPrice: int | None = Field(default=None, ge=0)
    minRating: float | None = Field(default=None, ge=0, le=5)
    minAiScore: int | None = Field(default=None, ge=0, le=100)
    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=12, ge=1, le=100)


class PaginatedProductsResponse(BaseModel):
    items: list[ProductDTO]
    pagination: Pagination


class CompareResponse(BaseModel):
    firstProduct: ProductDTO
    secondProduct: ProductDTO


class CatalogMetadataResponse(BaseModel):
    categoryLabels: dict[str, str]
    categoryPluralLabels: dict[str, str]
    productSpotlightBadges: dict[str, str]
    brands: list[str]


class HomeCollectionsResponse(BaseModel):
    featured: list[ProductDTO]
    newArrivals: list[ProductDTO]
    topAiPicks: list[ProductDTO]
    trending: list[ProductDTO]
