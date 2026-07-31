import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)

    products: Mapped[list["Product"]] = relationship(back_populates="brand")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_category_price", "category_id", "price_value"),
        Index("ix_products_rating_ai", "rating", "ai_score"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    availability: Mapped[str] = mapped_column(String(30), nullable=False, default="In Stock")

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id", ondelete="RESTRICT"), nullable=False)

    price_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="INR")
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 1), nullable=False)
    ai_score: Mapped[int] = mapped_column(Integer, nullable=False)

    ai_summary: Mapped[str] = mapped_column(Text, nullable=False)
    review_summary: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    category: Mapped[Category] = relationship(back_populates="products")
    brand: Mapped[Brand] = relationship(back_populates="products")

    images: Mapped[list["ProductImage"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    specifications: Mapped[list["ProductSpecification"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    features: Mapped[list["ProductFeature"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    pros: Mapped[list["ProductPro"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    cons: Mapped[list["ProductCon"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    best_for: Mapped[list["ProductBestFor"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    not_recommended_for: Mapped[list["ProductNotRecommendedFor"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    tags: Mapped[list["ProductTag"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    price_history: Mapped[list["PriceHistory"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    buy_links: Mapped[list["ProductBuyLink"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    similarities: Mapped[list["ProductSimilarity"]] = relationship(
        foreign_keys="ProductSimilarity.product_id",
        cascade="all, delete-orphan",
    )


class ProductImage(Base):
    __tablename__ = "product_images"
    __table_args__ = (UniqueConstraint("product_id", "position", name="uq_product_images_product_position"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    product: Mapped[Product] = relationship(back_populates="images")


class ProductSpecification(Base):
    __tablename__ = "product_specifications"
    __table_args__ = (UniqueConstraint("product_id", "label", name="uq_product_specifications_product_label"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    value: Mapped[str] = mapped_column(String(240), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    product: Mapped[Product] = relationship(back_populates="specifications")


class ProductFeature(Base):
    __tablename__ = "product_features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    value: Mapped[str] = mapped_column(String(240), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    product: Mapped[Product] = relationship(back_populates="features")


class ProductPro(Base):
    __tablename__ = "product_pros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    value: Mapped[str] = mapped_column(String(240), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    product: Mapped[Product] = relationship(back_populates="pros")


class ProductCon(Base):
    __tablename__ = "product_cons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    value: Mapped[str] = mapped_column(String(240), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    product: Mapped[Product] = relationship(back_populates="cons")


class ProductBestFor(Base):
    __tablename__ = "product_best_for"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    value: Mapped[str] = mapped_column(String(240), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    product: Mapped[Product] = relationship(back_populates="best_for")


class ProductNotRecommendedFor(Base):
    __tablename__ = "product_not_recommended_for"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    value: Mapped[str] = mapped_column(String(240), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    product: Mapped[Product] = relationship(back_populates="not_recommended_for")


class ProductTag(Base):
    __tablename__ = "product_tags"
    __table_args__ = (Index("ix_product_tags_value", "value"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    value: Mapped[str] = mapped_column(String(80), nullable=False)

    product: Mapped[Product] = relationship(back_populates="tags")


class PriceHistory(Base):
    __tablename__ = "price_history"
    __table_args__ = (UniqueConstraint("product_id", "label", name="uq_price_history_product_label"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(40), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    product: Mapped[Product] = relationship(back_populates="price_history")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (Index("ix_reviews_product_rating", "product_id", "rating"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    rating: Mapped[Decimal] = mapped_column(Numeric(2, 1), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[str] = mapped_column(String(20), nullable=False)

    product: Mapped[Product] = relationship(back_populates="reviews")


class ProductBuyLink(Base):
    __tablename__ = "product_buy_links"
    __table_args__ = (UniqueConstraint("product_id", "label", name="uq_product_buy_links_product_label"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(60), nullable=False)
    href: Mapped[str] = mapped_column(Text, nullable=False)

    product: Mapped[Product] = relationship(back_populates="buy_links")


class ProductSimilarity(Base):
    __tablename__ = "product_similarities"
    __table_args__ = (
        UniqueConstraint("product_id", "similar_product_id", name="uq_product_similarity_pair"),
        Index("ix_product_similarity_product_score", "product_id", "score"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    similar_product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_favorites_user_product"),
        Index("ix_favorites_user_created", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
