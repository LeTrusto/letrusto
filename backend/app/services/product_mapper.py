from decimal import Decimal

from app.models.entities import Product
from app.schemas.product import (
    ProductBuyLinkDTO,
    ProductDTO,
    ProductPriceHistoryDTO,
    ProductReviewDTO,
    ProductSpecificationDTO,
    ProductVariantDTO,
)


PRICE_LABEL_ORDER = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Now": 6,
}


def build_amazon_affiliate_url(product: Product) -> str | None:
    if product.amazon_affiliate_url:
        return product.amazon_affiliate_url

    if product.amazon_asin:
        return f"https://www.amazon.in/dp/{product.amazon_asin}?tag=letrusto-21"

    return None


def build_buy_link_href(product: Product, item_label: str, fallback_href: str) -> str:
    if item_label == "Amazon":
        amazon_href = build_amazon_affiliate_url(product)
        return amazon_href or fallback_href

    if item_label == "Flipkart" and product.flipkart_affiliate_url:
        return product.flipkart_affiliate_url

    return fallback_href


def format_inr(value: Decimal) -> str:
    normalized = int(value)
    return f"₹{normalized:,}"


def to_product_dto(product: Product, similar_slugs: list[str] | None = None) -> ProductDTO:
    images = [item.url for item in sorted(product.images, key=lambda item: item.position)]
    fallback_image = images[0] if images else ""
    stored_variant_prices = [
        variant.selling_price
        for variant in product.variants
        if variant.active and variant.selling_price is not None
    ]
    public_price = product.price_value or (min(stored_variant_prices) if stored_variant_prices else None)
    if public_price is None:
        raise ValueError(f"Product {product.slug} has no stored customer selling price")
    made_to_order = product.supplier == "printful" and product.verified_warehouse == "POD_ON_DEMAND"
    public_variants = [
        ProductVariantDTO(
            id=f"variant-{variant.position}",
            label=variant.name or variant.attributes or f"Option {variant.position}",
            price=format_inr(variant.selling_price),
            priceValue=variant.selling_price,
            available=bool(
                variant.active
                and (
                    (made_to_order and bool(variant.supplier_variant_id))
                    or (variant.cj_inventory or 0) > 0
                )
            ),
            inventory=max(0, variant.cj_inventory or 0),
        )
        for variant in sorted(product.variants, key=lambda item: item.position)
        if variant.active and variant.selling_price is not None
    ]

    category_slug = product.category.slug if product.category else "uncategorized"
    parent_category = product.category.parent.slug if product.category and product.category.parent else None

    return ProductDTO(
        id=product.slug,
        name=product.name,
        brand=product.brand.name if product.brand else "Unbranded",
        price=format_inr(public_price),
        priceValue=public_price,
        image=fallback_image,
        images=images,
        fallbackImage=fallback_image,
        variants=public_variants,
        madeToOrder=made_to_order,
        category=category_slug,
        parentCategory=parent_category,
        availability=product.availability,
        description=product.description,
        features=[item.value for item in sorted(product.features, key=lambda item: item.position)],
        aiScore=product.ai_score or 0,
        rating=product.rating or Decimal("0"),
        specs=[
            ProductSpecificationDTO(label=item.label, value=item.value)
            for item in sorted(product.specifications, key=lambda item: item.position)
        ],
        pros=[item.value for item in sorted(product.pros, key=lambda item: item.position)],
        cons=[item.value for item in sorted(product.cons, key=lambda item: item.position)],
        aiSummary=product.ai_summary or "",
        bestFor=[item.value for item in sorted(product.best_for, key=lambda item: item.position)],
        notRecommendedFor=[
            item.value
            for item in sorted(product.not_recommended_for, key=lambda item: item.position)
        ],
        tags=[item.value for item in product.tags],
        amazonAsin=product.amazon_asin,
        amazonAffiliateUrl=product.amazon_affiliate_url,
        flipkartAffiliateUrl=product.flipkart_affiliate_url,
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
        reviewSummary=product.review_summary or "",
        buyLinks=[
            ProductBuyLinkDTO(
                id=item.id,
                label=item.label,
                href=build_buy_link_href(product, item.label, item.href),
                retailer_type=item.retailer_type,
                is_affiliate=item.is_affiliate,
                click_count=item.click_count,
            )
            for item in sorted(product.buy_links, key=lambda item: item.label)
            if item.label != "Amazon" or build_amazon_affiliate_url(product)
        ],
        similarProductIds=similar_slugs or [],
        series=product.series,
        modelName=product.model_name,
        variant=product.variant,
        storage=product.storage,
        ram=product.ram,
        color=product.color,
    )
