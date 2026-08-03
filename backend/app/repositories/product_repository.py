from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.entities import Brand, Category, Product, ProductSimilarity
from app.schemas.product import ProductSearchQuery


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _category_load_options():
        return selectinload(Product.category).selectinload(Category.parent)

    @staticmethod
    def _product_load_options() -> tuple:
        return (
            selectinload(Product.brand),
            selectinload(Product.category).selectinload(Category.parent),
            selectinload(Product.images),
            selectinload(Product.specifications),
            selectinload(Product.features),
            selectinload(Product.pros),
            selectinload(Product.cons),
            selectinload(Product.best_for),
            selectinload(Product.not_recommended_for),
            selectinload(Product.tags),
            selectinload(Product.price_history),
            selectinload(Product.reviews),
            selectinload(Product.buy_links),
            selectinload(Product.similarities),
        )

    def list_products(self, ids: list[str] | None = None) -> list[Product]:
        stmt = select(Product).options(*self._product_load_options())
        if ids is not None:
            if len(ids) == 0:
                return []
            stmt = stmt.where(Product.slug.in_(ids))

        return list(self.db.scalars(stmt).unique().all())

    def get_by_slug(self, slug: str) -> Product | None:
        stmt = (
            select(Product)
            .options(*self._product_load_options())
            .where(Product.slug == slug)
        )
        return self.db.scalars(stmt).unique().first()

    def search_candidates(self, query: ProductSearchQuery) -> list[Product]:
        stmt: Select = select(Product).join(Product.brand).join(Product.category).options(*self._product_load_options())

        if query.category != "all":
            # Match by category slug OR its parent slug (so "electronics" returns all electronics children)
            parent_sub = select(Category.id).where(Category.slug == query.category)
            stmt = stmt.where(
                (Category.slug == query.category) | (Category.parent_id.in_(parent_sub))
            )

        if query.subcategory:
            stmt = stmt.where(Category.slug == query.subcategory)

        if query.series:
            stmt = stmt.where(func.lower(Product.series).contains(query.series.lower()))

        if query.brand:
            # Partial case-insensitive brand match so "apple" finds "Apple"
            stmt = stmt.where(func.lower(Brand.name).contains(query.brand.lower()))

        if query.price == "under-30000":
            stmt = stmt.where(Product.price_value < 30000)
        elif query.price == "30000-80000":
            stmt = stmt.where(Product.price_value >= 30000, Product.price_value <= 80000)
        elif query.price == "above-80000":
            stmt = stmt.where(Product.price_value > 80000)

        if query.rating == "4-plus":
            stmt = stmt.where(Product.rating >= 4)
        elif query.rating == "4.5-plus":
            stmt = stmt.where(Product.rating >= 4.5)

        if query.aiScore == "above-90":
            stmt = stmt.where(Product.ai_score > 90)

        if query.minPrice is not None:
            stmt = stmt.where(Product.price_value >= query.minPrice)
        if query.maxPrice is not None:
            stmt = stmt.where(Product.price_value <= query.maxPrice)
        if query.minRating is not None:
            stmt = stmt.where(Product.rating >= query.minRating)
        if query.minAiScore is not None:
            stmt = stmt.where(Product.ai_score >= query.minAiScore)

        return list(self.db.scalars(stmt).unique().all())

    def get_similar_slugs(self, product_id) -> list[str]:
        stmt = (
            select(Product.slug)
            .join(ProductSimilarity, ProductSimilarity.similar_product_id == Product.id)
            .where(ProductSimilarity.product_id == product_id)
            .order_by(ProductSimilarity.score.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_categories(self) -> list[Category]:
        return list(self.db.scalars(select(Category).order_by(Category.position.asc(), Category.name.asc())).all())

    def get_top_level_categories(self) -> list[Category]:
        return list(
            self.db.scalars(
                select(Category)
                .where(Category.parent_id.is_(None))
                .options(selectinload(Category.children))
                .order_by(Category.position.asc())
            ).all()
        )

    def get_brands(self) -> list[str]:
        return list(self.db.scalars(select(Brand.name).order_by(Brand.name.asc())).all())

    def get_by_id(self, product_id) -> Product | None:
        stmt = select(Product).options(*self._product_load_options()).where(Product.id == product_id)
        return self.db.scalars(stmt).unique().first()
