from decimal import Decimal

from app.models.entities import Product
from app.schemas.product import (
    ProductBuyLinkDTO,
    ProductDTO,
    ProductPriceHistoryDTO,
    ProductReviewDTO,
    ProductSpecificationDTO,
)


PRICE_LABEL_ORDER = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Now": 6,
}


def format_inr(value: Decimal) -> str:
    normalized = int(value)
    return f"₹{normalized:,}"


def to_product_dto(product: Product, similar_slugs: list[str] | None = None) -> ProductDTO:
    images = [item.url for item in sorted(product.images, key=lambda item: item.position)]
    fallback_image = images[0] if images else ""

    parent_category = product.category.parent.slug if product.category.parent else None

    return ProductDTO(
        id=product.slug,
        name=product.name,
        brand=product.brand.name,
        price=format_inr(product.price_value),
        priceValue=product.price_value,
        image=fallback_image,
        images=images,
        fallbackImage=fallback_image,
        category=product.category.slug,
        parentCategory=parent_category,
        availability=product.availability,
        description=product.description,
        features=[item.value for item in sorted(product.features, key=lambda item: item.position)],
        aiScore=product.ai_score,
        rating=product.rating,
        specs=[
            ProductSpecificationDTO(label=item.label, value=item.value)
            for item in sorted(product.specifications, key=lambda item: item.position)
        ],
        pros=[item.value for item in sorted(product.pros, key=lambda item: item.position)],
        cons=[item.value for item in sorted(product.cons, key=lambda item: item.position)],
        aiSummary=product.ai_summary,
        bestFor=[item.value for item in sorted(product.best_for, key=lambda item: item.position)],
        notRecommendedFor=[
            item.value
            for item in sorted(product.not_recommended_for, key=lambda item: item.position)
        ],
        tags=[item.value for item in product.tags],
        priceHistory=[
            ProductPriceHistoryDTO(label=item.label, price=item.price)
            for item in sorted(
                product.price_history,
                key=lambda item: PRICE_LABEL_ORDER.get(item.label, 99),
            )
        ],
        reviews=[
            ProductReviewDTO(
                author=item.author,
                title=item.title,
                rating=item.rating,
                comment=item.comment,
                date=item.date,
            )
            for item in sorted(product.reviews, key=lambda item: item.date)
        ],
        reviewSummary=product.review_summary,
        buyLinks=[
            ProductBuyLinkDTO(
                id=item.id,
                label=item.label,
                href=item.href,
                retailer_type=item.retailer_type,
                is_affiliate=item.is_affiliate,
                click_count=item.click_count,
            )
            for item in sorted(product.buy_links, key=lambda item: item.label)
        ],
        similarProductIds=similar_slugs or [],
        series=product.series,
        modelName=product.model_name,
        variant=product.variant,
        storage=product.storage,
        ram=product.ram,
        color=product.color,
    )
