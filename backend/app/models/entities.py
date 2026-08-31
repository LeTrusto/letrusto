import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, JSON, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    icon: Mapped[str | None] = mapped_column(String(80), nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    products: Mapped[list["Product"]] = relationship(back_populates="category")
    parent: Mapped["Category | None"] = relationship("Category", remote_side="Category.id", foreign_keys="Category.parent_id")
    children: Mapped[list["Category"]] = relationship("Category", foreign_keys="Category.parent_id", back_populates="parent")


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)

    products: Mapped[list["Product"]] = relationship(back_populates="brand")


class AIToolCategory(Base):
    __tablename__ = "ai_tool_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    tools: Mapped[list["AITool"]] = relationship(back_populates="category")


class AITool(Base):
    __tablename__ = "ai_tools"
    __table_args__ = (
        Index("ix_ai_tools_category_status", "category_id", "lifecycle_status"),
        Index("ix_ai_tools_last_verified", "last_verified_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(160), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    website_url: Mapped[str] = mapped_column(Text, nullable=False)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("ai_tool_categories.id", ondelete="RESTRICT"), nullable=False)
    lifecycle_status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)

    pricing_model: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pricing_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    pricing_currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    pricing_period: Mapped[str | None] = mapped_column(String(20), nullable=True)
    has_free_plan: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_free_trial: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    trial_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pricing_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    pricing_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    affiliate_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    affiliate_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    letrusto_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    why_letrusto_recommends: Mapped[str | None] = mapped_column(Text, nullable=True)

    use_cases: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    features: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    pros: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    cons: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    best_for: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    not_ideal_for: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    platforms: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    integrations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    category: Mapped[AIToolCategory] = relationship(back_populates="tools")
    fact_provenance: Mapped[list["AIToolFactProvenance"]] = relationship(
        back_populates="ai_tool", cascade="all, delete-orphan"
    )


class AIToolFactProvenance(Base):
    __tablename__ = "ai_tool_fact_provenance"
    __table_args__ = (
        Index("ix_ai_tool_fact_provenance_tool_fact", "ai_tool_id", "fact_type", "fact_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ai_tool_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_tools.id", ondelete="CASCADE"), nullable=False, index=True)
    fact_type: Mapped[str] = mapped_column(String(40), nullable=False)
    fact_key: Mapped[str] = mapped_column(String(160), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_kind: Mapped[str] = mapped_column(String(40), nullable=False, default="official_provider")
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    ai_tool: Mapped[AITool] = relationship(back_populates="fact_provenance")


class SupplierCandidate(Base):
    __tablename__ = "supplier_candidates"
    __table_args__ = (
        UniqueConstraint(
            "supplier",
            "supplier_product_id",
            name="uq_supplier_candidates_supplier_product_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier: Mapped[str] = mapped_column(String(40), nullable=False, index=True, default="cj")
    supplier_product_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    supplier_sku: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    approval_status: Mapped[str] = mapped_column(String(20), nullable=False, default="REVIEW", index=True)
    readiness_status: Mapped[str] = mapped_column(String(20), nullable=False, default="DISCOVERED", index=True)
    supplier_validation_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    supplier_validation_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    commercial_status: Mapped[str] = mapped_column(String(20), nullable=False, default="REVIEW")
    market_status: Mapped[str] = mapped_column(String(30), nullable=False, default="NOT_EVALUATED")
    discovery_min_selling_price_inr: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    discovery_max_selling_price_inr: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    data_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    snapshot_status: Mapped[str] = mapped_column(
        String(40), nullable=False, default="LEGACY_SNAPSHOT_UNAVAILABLE", server_default="LEGACY_SNAPSHOT_UNAVAILABLE"
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    decision_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    rejection_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    imported_product_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True
    )
    imported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    import_result: Mapped[str | None] = mapped_column(String(40), nullable=True)
    import_failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    market_evidence: Mapped[list["ProductMarketEvidence"]] = relationship(
        back_populates="supplier_candidate", cascade="all, delete-orphan"
    )


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
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE", index=True)
    supplier: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    supplier_product_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    supplier_source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    supplier_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    shipping_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    selling_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    total_inventory: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cj_inventory: Mapped[int | None] = mapped_column(Integer, nullable=True)
    factory_inventory: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verified_warehouse: Mapped[str | None] = mapped_column(String(20), nullable=True)
    last_supplier_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    commercial_status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT", index=True)
    commercial_reasons: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    commercial_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    supplier_validation_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    supplier_validation_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    supplier_validation_notes: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    supplier_validation_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    supplier_validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_decided_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    approval_rejection_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    approval_evidence: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=True)
    brand_id: Mapped[int | None] = mapped_column(ForeignKey("brands.id", ondelete="RESTRICT"), nullable=True)

    # Phase 6.1 catalog enrichment fields (all nullable for backward compatibility)
    series: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    model_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    variant: Mapped[str | None] = mapped_column(String(120), nullable=True)
    storage: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ram: Mapped[str | None] = mapped_column(String(20), nullable=True)
    color: Mapped[str | None] = mapped_column(String(60), nullable=True)
    amazon_asin: Mapped[str | None] = mapped_column(String(20), nullable=True)
    amazon_affiliate_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    flipkart_affiliate_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    price_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="INR")
    rating: Mapped[Decimal | None] = mapped_column(Numeric(3, 1), nullable=True)
    ai_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    category: Mapped[Category] = relationship(back_populates="products")
    brand: Mapped[Brand] = relationship(back_populates="products")

    images: Mapped[list["ProductImage"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    variants: Mapped[list["ProductVariant"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    market_evidence: Mapped[list["ProductMarketEvidence"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
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
    trust_claims: Mapped[list["TrustClaim"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    printful_shipping_rates: Mapped[list["PrintfulShippingRate"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class PrintfulShippingRate(Base):
    __tablename__ = "printful_shipping_rates"
    __table_args__ = (
        UniqueConstraint("product_id", "category_key", "destination_region", name="uq_printful_shipping_rate_scope"),
        Index("ix_printful_shipping_rates_destination", "destination_region", "country_codes"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=True, index=True
    )
    source: Mapped[str] = mapped_column(String(40), nullable=False, default="printful")
    rate_source: Mapped[str] = mapped_column(String(40), nullable=False, default="PRINTFUL_PUBLISHED")
    category_key: Mapped[str] = mapped_column(String(80), nullable=False, default="hoodies-sweatshirts")
    destination_region: Mapped[str] = mapped_column(String(40), nullable=False)
    country_codes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    shipping_method: Mapped[str] = mapped_column(String(120), nullable=False, default="Standard")
    single_product_rate: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    additional_product_rate: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="USD")
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    requires_verification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    product: Mapped[Product | None] = relationship(back_populates="printful_shipping_rates")


class ProductVariant(Base):
    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint("product_id", "supplier_variant_id", name="uq_product_variants_product_supplier_id"),
        Index("ix_product_variants_supplier_variant_id", "supplier_variant_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    supplier_variant_id: Mapped[str] = mapped_column(String(120), nullable=False)
    supplier_variant_sku: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(String(240), nullable=False, default="")
    attributes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    supplier_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    supplier_cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    selling_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    total_inventory: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cj_inventory: Mapped[int | None] = mapped_column(Integer, nullable=True)
    factory_inventory: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verified_warehouse: Mapped[str | None] = mapped_column(String(20), nullable=True)
    weight_grams: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    product: Mapped[Product] = relationship(back_populates="variants")
    warehouse_inventory: Mapped[list["SupplierVariantInventory"]] = relationship(
        back_populates="variant", cascade="all, delete-orphan", passive_deletes=True
    )


class SupplierVariantInventory(Base):
    __tablename__ = "supplier_variant_inventory"
    __table_args__ = (
        UniqueConstraint(
            "supplier",
            "supplier_variant_id",
            "warehouse_identity",
            name="uq_supplier_variant_inventory_identity",
        ),
        Index("ix_supplier_variant_inventory_variant_country", "variant_id", "warehouse_country"),
        Index("ix_supplier_variant_inventory_product_variant", "product_id", "supplier_variant_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False
    )
    supplier: Mapped[str] = mapped_column(String(40), nullable=False, default="cj")
    supplier_product_id: Mapped[str] = mapped_column(String(120), nullable=False)
    supplier_variant_id: Mapped[str] = mapped_column(String(120), nullable=False)
    warehouse_identity: Mapped[str] = mapped_column(String(180), nullable=False)
    warehouse_country: Mapped[str] = mapped_column(String(20), nullable=False)
    storage_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    warehouse_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    total_inventory: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cj_sellable_inventory: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    factory_inventory: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    verification_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    variant: Mapped[ProductVariant] = relationship(back_populates="warehouse_inventory")


class ProductMarketEvidence(Base):
    __tablename__ = "product_market_evidence"
    __table_args__ = (
        CheckConstraint("observed_price_inr > 0", name="ck_product_market_evidence_positive_price"),
        CheckConstraint("currency = 'INR'", name="ck_product_market_evidence_currency_inr"),
        CheckConstraint(
            "(product_id IS NOT NULL) <> (supplier_candidate_id IS NOT NULL)",
            name="ck_product_market_evidence_exactly_one_owner",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=True, index=True
    )
    supplier_candidate_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("supplier_candidates.id", ondelete="CASCADE"), nullable=True, index=True
    )
    competitor_name: Mapped[str] = mapped_column(String(160), nullable=False)
    product_name: Mapped[str] = mapped_column(String(240), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    observed_price_inr: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="INR", server_default="INR")
    variant_description: Mapped[str | None] = mapped_column(String(240), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    product: Mapped[Product | None] = relationship(back_populates="market_evidence")
    supplier_candidate: Mapped[SupplierCandidate | None] = relationship(back_populates="market_evidence")


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
    retailer_type: Mapped[str] = mapped_column(String(40), nullable=False, default="marketplace")
    is_affiliate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    click_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    product: Mapped[Product] = relationship(back_populates="buy_links")


# ── Phase 3: Content Engine ───────────────────────────────────────────────────


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (Index("ix_articles_slug", "slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False, default="guide")
    meta_title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


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


# ── Phase 5: User Platform Entities ──────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    mobile_number: Mapped[str | None] = mapped_column(String(15), unique=True, index=True, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(15), nullable=True)
    shipping_address: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    google_id: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    saved_comparisons: Mapped[list["SavedComparison"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    price_alerts: Mapped[list["PriceAlert"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    ai_conversations: Mapped[list["AiConversation"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    analytics_events: Mapped[list["AnalyticsEvent"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    support_tickets: Mapped[list["SupportTicket"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    cart: Mapped["Cart | None"] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)
    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class OtpChallenge(Base):
    __tablename__ = "otp_challenges"
    __table_args__ = (Index("ix_otp_challenges_mobile_created", "mobile_number", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mobile_number: Mapped[str] = mapped_column(String(15), nullable=False, index=True)
    code_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    request_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="cart")
    items: Mapped[list["CartItem"]] = relationship(back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("cart_id", "product_id", "variant_id", name="uq_cart_items_variant"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("carts.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), index=True)
    variant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product_variants.id", ondelete="RESTRICT"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_snapshot: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    cart: Mapped[Cart] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()
    variant: Mapped[ProductVariant] = relationship()


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("order_number", name="uq_orders_order_number"),
        UniqueConstraint("user_id", "idempotency_key", name="uq_orders_user_idempotency"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING_PAYMENT", index=True)
    payment_status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    fulfillment_status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    shipping_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="INR")
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    shipping_address: Mapped[dict] = mapped_column(JSON, nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payment_provider: Mapped[str | None] = mapped_column(String(30), nullable=True)
    provider_order_id: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True, index=True)
    payment_session_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    payment_attempted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payment_failure_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    provider_reference: Mapped[str | None] = mapped_column(String(160), nullable=True)
    supplier_order_id: Mapped[str | None] = mapped_column(String(160), nullable=True, unique=True, index=True)
    fulfillment_submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fulfillment_failure_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tracking_number: Mapped[str | None] = mapped_column(String(160), nullable=True)
    tracking_carrier: Mapped[str | None] = mapped_column(String(120), nullable=True)
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    supplier_status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    last_supplier_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    supplier_pay_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    supplier_payment_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    supplier_shipment_order_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    supplier_origin: Mapped[str | None] = mapped_column(String(40), nullable=True)
    supplier_logistic_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    supplier_status_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    supplier_payment_state: Mapped[str | None] = mapped_column(String(20), nullable=True)
    supplier_payment_attempted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    supplier_payment_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    supplier_payment_error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    supplier_payment_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cancelled_by: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    payment_attempts: Mapped[list["PaymentAttempt"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    refund_requests: Mapped[list["RefundRequest"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    inventory_reservations: Mapped[list["InventoryReservation"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    variant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    product_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    variant_name: Mapped[str] = mapped_column(String(240), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    supplier_cost_inr_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    supplier_cost_usd_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    supplier_cost_currency_snapshot: Mapped[str | None] = mapped_column(String(8), nullable=True)
    shipping_cost_inr_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    landed_cost_inr_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    pricing_fx_rate_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    payment_gateway_policy_pct_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    rto_reserve_policy_pct_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    target_contribution_margin_pct_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    target_cac_inr_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    economics_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    economics_missing: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    order: Mapped[Order] = relationship(back_populates="items")
    product: Mapped[Product | None] = relationship()
    variant: Mapped[ProductVariant | None] = relationship()
    inventory_reservation: Mapped["InventoryReservation | None"] = relationship(back_populates="order_item", uselist=False)


class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"
    __table_args__ = (UniqueConstraint("provider", "provider_payment_id", name="uq_payment_attempt_provider_payment"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    provider_order_id: Mapped[str] = mapped_column(String(120), nullable=False)
    provider_payment_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING")
    failure_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    order: Mapped[Order] = relationship(back_populates="payment_attempts")


class RefundRequest(Base):
    __tablename__ = "refund_requests"
    __table_args__ = (UniqueConstraint("idempotency_key", name="uq_refund_requests_idempotency_key"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    payment_attempt_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("payment_attempts.id", ondelete="SET NULL"), nullable=True)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    provider_refund_id: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    provider_order_id: Mapped[str] = mapped_column(String(120), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="INR")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING")
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    requested_by: Mapped[str] = mapped_column(String(80), nullable=False, default="customer")
    admin_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    order: Mapped[Order] = relationship(back_populates="refund_requests")
    payment_attempt: Mapped[PaymentAttempt | None] = relationship()


class InventoryReservation(Base):
    __tablename__ = "inventory_reservations"
    __table_args__ = (
        UniqueConstraint("order_item_id", name="uq_inventory_reservations_order_item"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    order_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product_variants.id", ondelete="RESTRICT"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE", index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    order: Mapped[Order] = relationship(back_populates="inventory_reservations")
    order_item: Mapped[OrderItem] = relationship(back_populates="inventory_reservation")
    variant: Mapped[ProductVariant] = relationship()


class MarketingSpend(Base):
    __tablename__ = "marketing_spend"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spend_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    campaign: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    spend_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="INR")
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class OrderMarketingAttribution(Base):
    __tablename__ = "order_marketing_attribution"
    __table_args__ = (UniqueConstraint("order_id", name="uq_order_marketing_attribution_order"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(40), nullable=False)
    campaign: Mapped[str | None] = mapped_column(String(200), nullable=True)
    attribution_method: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ATTRIBUTED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    order: Mapped[Order] = relationship()


class TrustClaim(Base):
    __tablename__ = "trust_claims"
    __table_args__ = (
        CheckConstraint("verification_status IN ('UNVERIFIED', 'PENDING', 'VERIFIED', 'REJECTED', 'EXPIRED')", name="ck_trust_claim_status"),
        CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 100)", name="ck_trust_claim_confidence"),
        Index("ix_trust_claims_product_status", "product_id", "verification_status"),
        Index("ix_trust_claims_type", "claim_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_type: Mapped[str] = mapped_column(String(80), nullable=False)
    claim_value: Mapped[str] = mapped_column(Text, nullable=False)
    claim_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(80), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(20), nullable=False, default="UNVERIFIED", index=True)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    assessment_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    product: Mapped[Product] = relationship(back_populates="trust_claims")
    evidence_links: Mapped[list["TrustClaimEvidence"]] = relationship(back_populates="claim", cascade="all, delete-orphan")
    verifications: Mapped[list["TrustVerification"]] = relationship(back_populates="claim", cascade="all, delete-orphan")
    audit_events: Mapped[list["TrustAuditEvent"]] = relationship(back_populates="claim", cascade="all, delete-orphan")


class TrustEvidence(Base):
    __tablename__ = "trust_evidence"
    __table_args__ = (
        CheckConstraint("(reference_url IS NOT NULL) OR (storage_reference IS NOT NULL)", name="ck_trust_evidence_reference"),
        Index("ix_trust_evidence_type_active", "evidence_type", "is_active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_type: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(80), nullable=True)
    reference_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    evidence_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    claim_links: Mapped[list["TrustClaimEvidence"]] = relationship(back_populates="evidence")


class TrustClaimEvidence(Base):
    __tablename__ = "trust_claim_evidence"
    __table_args__ = (UniqueConstraint("claim_id", "evidence_id", name="uq_trust_claim_evidence"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trust_claims.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trust_evidence.id", ondelete="RESTRICT"), nullable=False, index=True)
    assessment_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    attached_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    claim: Mapped[TrustClaim] = relationship(back_populates="evidence_links")
    evidence: Mapped[TrustEvidence] = relationship(back_populates="claim_links")


class TrustVerification(Base):
    __tablename__ = "trust_verifications"
    __table_args__ = (
        CheckConstraint("verification_status IN ('UNVERIFIED', 'PENDING', 'VERIFIED', 'REJECTED', 'EXPIRED')", name="ck_trust_verification_status"),
        Index("ix_trust_verifications_claim_verified", "claim_id", "verified_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trust_claims.id", ondelete="CASCADE"), nullable=False, index=True)
    verification_status: Mapped[str] = mapped_column(String(20), nullable=False)
    verification_method: Mapped[str] = mapped_column(String(80), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_snapshot: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    verification_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    verified_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    claim: Mapped[TrustClaim] = relationship(back_populates="verifications")


class TrustAuditEvent(Base):
    __tablename__ = "trust_audit_events"
    __table_args__ = (Index("ix_trust_audit_events_claim_created", "claim_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trust_claims.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("trust_evidence.id", ondelete="SET NULL"), nullable=True, index=True)
    verification_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("trust_verifications.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    previous_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    current_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    claim: Mapped[TrustClaim] = relationship(back_populates="audit_events")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (Index("ix_refresh_tokens_hash", "token_hash"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")


class SavedComparison(Base):
    __tablename__ = "saved_comparisons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_ids: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array
    label: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="saved_comparisons")


class PriceAlert(Base):
    __tablename__ = "price_alerts"
    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uq_price_alert_user_product"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    target_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="price_alerts")
    product: Mapped["Product"] = relationship()


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (Index("ix_notifications_user_read", "user_id", "is_read"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    product_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="notifications")
    product: Mapped["Product | None"] = relationship()


class AiConversation(Base):
    __tablename__ = "ai_conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, default="New Conversation")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="ai_conversations")
    messages: Mapped[list["AiMessage"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class AiMessage(Base):
    __tablename__ = "ai_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_conversations.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    conversation: Mapped["AiConversation"] = relationship(back_populates="messages")


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    __table_args__ = (
        Index("ix_analytics_events_type_created", "event_type", "created_at"),
        Index("ix_analytics_events_recommendation_created", "recommendation_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    product_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    ai_tool_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ai_tools.id", ondelete="SET NULL"), nullable=True, index=True)
    ai_tool_slug: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    recommendation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped["User | None"] = relationship(back_populates="analytics_events")


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User | None"] = relationship(back_populates="support_tickets")


class Deal(Base):
    __tablename__ = "deals"
    __table_args__ = (
        Index("ix_deals_is_active_valid_until", "is_active", "valid_until"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    deal_type: Mapped[str] = mapped_column(String(40), nullable=False)  # today | festival | cashback | coupon | trending
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    coupon_code: Mapped[str | None] = mapped_column(String(40), nullable=True)
    cashback_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    product: Mapped["Product"] = relationship()
