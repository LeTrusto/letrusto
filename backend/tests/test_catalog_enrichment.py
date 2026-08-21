import asyncio
from copy import deepcopy
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.ai.providers.catalog_enrichment import (
    CatalogEnrichmentRequest,
    CatalogEnrichmentResult,
    MockCatalogEnrichmentProvider,
)
from app.core.exceptions import BadRequestError
from app.db.session import SessionLocal
from app.models.entities import SupplierCandidate
from app.services.catalog_enrichment_service import CatalogEnrichmentService


class RecordingProvider(MockCatalogEnrichmentProvider):
    def __init__(self, content=None, error=None):
        self.calls = 0
        self.content = content
        self.error = error

    def generate(self, request):
        self.calls += 1
        if self.error:
            raise self.error
        result = super().generate(request)
        return CatalogEnrichmentResult(
            content=self.content if self.content is not None else result.content,
            provider=self.name,
        )


class MalformedProvider:
    name = "malformed"

    def generate(self, request):
        return CatalogEnrichmentResult(
            content={"category": "home-kitchen", "title": "Only a title"},
            provider=self.name,
        )


class MutatingProvider(MockCatalogEnrichmentProvider):
    def generate(self, request):
        request.variants[0]["cj_inventory"] = 0
        request.variants[0]["supplier_variant_id"] = "MUTATED"
        request.variants.clear()
        return super().generate(request)


@pytest.fixture
def enrichment_context():
    db = SessionLocal()
    product_id = f"ENRICH-{uuid4()}"
    candidate = SupplierCandidate(
        supplier="cj",
        supplier_product_id=product_id,
        supplier_sku=f"SKU-{product_id}",
        name="Creative Swordfish Handle Metal Beer Bottle Openers",
        approval_status="REVIEW",
        readiness_status="VALIDATED",
        supplier_validation_status="PASS",
        supplier_validation_score=88,
        commercial_status="REVIEW",
        snapshot_status="AVAILABLE",
        data_snapshot={
            "reference_data": {
                "productNameEn": "Creative Swordfish Handle Metal Beer Bottle Openers",
                "description": "Metal bottle opener for kitchen and bar use.",
                "categoryNameEn": "Kitchen Accessories",
            },
            "warehouses": [{
                "storage_id": "1",
                "warehouse_name": "China Warehouse",
                "warehouse_country": "CN",
            }],
            "logistics": {
                "selected": {"carrier": "CJPacket Eub", "method": "CJPacket Eub"},
            },
            "freight": {"cost_usd": 2.65, "cost_inr": "221.275"},
            "commercial_result": {
                "minimum_price_inr": "641.17",
                "maximum_price_inr": "641.17",
                "target_margin_percent": "20.00",
                "cac_viable": False,
                "failure_reasons": [],
            },
            "variants": [{
                "supplier_variant_id": "1899737610076839937",
                "supplier_variant_sku": "SKU-1",
                "name": "Swordfish opener",
                "attributes": "Metal",
                "supplier_cost_usd": 1.0,
                "supplier_cost_inr": 83.5,
                "weight_grams": 120,
                "cj_inventory": 177,
                "factory_inventory": 12527,
                "total_inventory": 12704,
                "selling_price_inr": "641.17",
                "target_margin_status": "PASS",
                "cac_target_status": "REVIEW",
            }],
        },
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    yield db, candidate
    db.rollback()
    stored = db.scalar(select(SupplierCandidate).where(SupplierCandidate.id == candidate.id))
    if stored:
        db.delete(stored)
        db.commit()
    db.close()


def enrich(context, provider=None):
    db, candidate = context
    return asyncio.run(CatalogEnrichmentService(db, provider=provider).enrich(candidate.id))


def test_validated_candidate_generates_complete_enrichment_and_review_state(enrichment_context):
    db, candidate = enrichment_context
    before = deepcopy(candidate.data_snapshot)

    result = enrich(enrichment_context, MockCatalogEnrichmentProvider())

    assert result.readiness_status == "REVIEW"
    assert result.enrichment["status"] == "ENRICHED"
    assert result.enrichment["category"] == "home-kitchen"
    assert result.enrichment["subcategory"] == "bar-accessories"
    assert result.enrichment["title"]
    assert result.enrichment["description"]
    assert result.enrichment["key_features"]
    assert result.enrichment["attributes"]
    assert result.enrichment["seo_title"]
    assert result.enrichment["seo_meta_description"]
    assert result.enrichment["search_keywords"]
    assert result.enrichment["suggested_selling_price_inr"] == "641.17"
    assert result.enrichment["commercial_summary"]["target_margin_percent"] == "20.00"
    assert result.supplier_product_id == candidate.supplier_product_id
    assert result.variants[0].supplier_variant_id == before["variants"][0]["supplier_variant_id"]
    assert result.variants[0].cj_inventory == before["variants"][0]["cj_inventory"]
    assert result.variants[0].factory_inventory == before["variants"][0]["factory_inventory"]
    assert result.warehouses == before["warehouses"]
    assert result.freight == before["freight"]
    assert result.logistics == before["logistics"]


def test_enrichment_is_idempotent(enrichment_context):
    provider = RecordingProvider()

    first = enrich(enrichment_context, provider)
    second = enrich(enrichment_context, provider)

    assert first.enrichment == second.enrichment
    assert provider.calls == 1


def test_provider_cannot_mutate_authoritative_snapshot(enrichment_context):
    db, candidate = enrichment_context
    before = deepcopy(candidate.data_snapshot)

    result = enrich(enrichment_context, MutatingProvider())

    db.refresh(candidate)
    assert result.readiness_status == "REVIEW"
    assert candidate.data_snapshot["variants"] == before["variants"]
    assert candidate.data_snapshot["warehouses"] == before["warehouses"]
    assert candidate.data_snapshot["freight"] == before["freight"]
    assert candidate.data_snapshot["logistics"] == before["logistics"]
    assert candidate.data_snapshot["commercial_result"] == before["commercial_result"]


@pytest.mark.parametrize("field", ["key_features", "search_keywords"])
@pytest.mark.parametrize("values", [[""], ["   "], ["", ""]])
def test_empty_generated_values_are_rejected(enrichment_context, field, values):
    provider = RecordingProvider()
    content = provider.generate(CatalogEnrichmentRequest(
        product_id="test",
        title="Bottle opener",
        description="A bottle opener.",
        supplier_category="Kitchen",
        variants=[],
    )).content
    content[field] = values

    result = enrich(enrichment_context, RecordingProvider(content=content))

    assert result.enrichment["status"] == "FAILED"
    assert result.enrichment["failure_reasons"] == ["INSUFFICIENT_CONTENT"]


@pytest.mark.parametrize(
    ("provider", "reason"),
    [
        (RecordingProvider(error=RuntimeError("provider unavailable")), "provider unavailable"),
        (MalformedProvider(), "INSUFFICIENT_CONTENT"),
        (RecordingProvider(content={"category": "invalid"}), "INVALID_CATEGORY"),
    ],
)
def test_enrichment_failures_are_review_safe(enrichment_context, provider, reason):
    result = enrich(enrichment_context, provider)

    assert result.readiness_status == "REVIEW"
    assert result.enrichment["status"] == "FAILED"
    assert reason in result.enrichment["failure_reasons"]
    assert result.approval_status == "REVIEW"


def test_missing_product_data_is_recorded_without_changing_deterministic_snapshot(enrichment_context):
    db, candidate = enrichment_context
    original = deepcopy(candidate.data_snapshot)
    candidate.data_snapshot = {"commercial_result": original["commercial_result"]}
    db.commit()

    result = enrich(enrichment_context)

    assert result.readiness_status == "REVIEW"
    assert result.enrichment["failure_reasons"] == ["MISSING_PRODUCT_INFORMATION"]
    assert result.enrichment["status"] == "FAILED"


def test_pricing_failure_is_recorded_and_provider_content_is_not_published(enrichment_context):
    db, candidate = enrichment_context
    snapshot = deepcopy(candidate.data_snapshot)
    snapshot["commercial_result"]["minimum_price_inr"] = None
    candidate.data_snapshot = snapshot
    db.commit()

    result = enrich(enrichment_context)

    assert result.readiness_status == "REVIEW"
    assert result.enrichment["failure_reasons"] == ["PRICING_FAILURE"]


def test_rejected_candidate_cannot_be_enriched(enrichment_context):
    db, candidate = enrichment_context
    candidate.readiness_status = "REJECTED"
    db.commit()

    with pytest.raises(BadRequestError, match="Rejected"):
        enrich(enrichment_context)


def test_imported_candidate_cannot_be_enriched(enrichment_context):
    db, candidate = enrichment_context
    candidate.approval_status = "IMPORTED"
    db.commit()

    with pytest.raises(BadRequestError, match="Imported"):
        enrich(enrichment_context)
