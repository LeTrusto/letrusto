from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.providers.catalog_enrichment import (
    CatalogEnrichmentProvider,
    CatalogEnrichmentRequest,
    build_catalog_enrichment_provider,
)
from app.core.catalog_readiness import LETRUSTO_TAXONOMY
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.entities import SupplierCandidate
from app.schemas.admin_products import SupplierCandidateDTO
from app.services.admin_product_service import AdminProductService
from app.services.supplier_candidate_readiness_service import SupplierCandidateReadinessService


class CatalogEnrichmentService:
    def __init__(
        self,
        db: Session,
        provider: CatalogEnrichmentProvider | None = None,
    ) -> None:
        self.db = db
        self.provider = provider or build_catalog_enrichment_provider()
        self.candidate_service = AdminProductService(db)

    async def enrich(self, candidate_id: UUID) -> SupplierCandidateDTO:
        candidate = self.db.scalar(
            select(SupplierCandidate).where(SupplierCandidate.id == candidate_id)
        )
        if candidate is None:
            raise NotFoundError("Supplier candidate not found")
        if candidate.imported_product_id or candidate.approval_status == "IMPORTED":
            raise BadRequestError("Imported supplier candidate cannot be enriched")
        if candidate.approval_status == "REJECTED":
            raise BadRequestError("Rejected supplier candidate cannot be enriched")
        if candidate.readiness_status == "REJECTED":
            raise BadRequestError("Rejected supplier candidate cannot be enriched")
        if candidate.readiness_status not in {"VALIDATED", "REVIEW"}:
            raise BadRequestError(
                "Only VALIDATED supplier candidates can start enrichment"
            )

        snapshot = deepcopy(candidate.data_snapshot or {})
        existing = snapshot.get("enrichment") or {}
        if existing.get("status") == "ENRICHED":
            return self.candidate_service._candidate_dto(candidate)
        if candidate.readiness_status == "REVIEW":
            raise BadRequestError("Only VALIDATED supplier candidates can start enrichment")

        candidate.readiness_status = SupplierCandidateReadinessService.transition(
            candidate.readiness_status, "ENRICHING"
        )
        self.db.commit()

        try:
            request = self._build_request(candidate, snapshot)
            result = self.provider.generate(request)
            content = self._validate_content(result.content)
            commercial = self._deterministic_commercial_result(snapshot)
            snapshot["enrichment"] = {
                "status": "ENRICHED",
                "provider": result.provider,
                **content,
                "suggested_selling_price_inr": commercial["suggested_selling_price_inr"],
                "commercial_summary": commercial["summary"],
                "failure_reasons": [],
                "enriched_at": datetime.now(timezone.utc).isoformat(),
            }
            candidate.data_snapshot = snapshot
            candidate.readiness_status = SupplierCandidateReadinessService.transition(
                candidate.readiness_status, "ENRICHED"
            )
            candidate.readiness_status = SupplierCandidateReadinessService.transition(
                candidate.readiness_status, "REVIEW"
            )
        except Exception as exc:
            reason = getattr(exc, "detail", None) or str(exc) or "ENRICHMENT_FAILURE"
            self._record_failure(candidate, snapshot, str(reason))

        self.db.commit()
        self.db.refresh(candidate)
        return self.candidate_service._candidate_dto(candidate)

    def _build_request(
        self, candidate: SupplierCandidate, snapshot: dict[str, Any]
    ) -> CatalogEnrichmentRequest:
        reference = snapshot.get("reference_data")
        variants = snapshot.get("variants")
        if not isinstance(reference, dict) or not isinstance(variants, list) or not variants:
            raise BadRequestError("MISSING_PRODUCT_INFORMATION")
        description = self._first_text(
            reference.get("description"), reference.get("productProEn"), reference.get("productNameEn")
        )
        if not description:
            raise BadRequestError("MISSING_PRODUCT_INFORMATION")
        return CatalogEnrichmentRequest(
            product_id=candidate.supplier_product_id,
            title=candidate.name,
            description=description,
            supplier_category=self._first_text(
                reference.get("categoryNameEn"), reference.get("categoryName")
            ),
            variants=deepcopy(variants),
        )

    @staticmethod
    def _first_text(*values: Any) -> str:
        for value in values:
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    @staticmethod
    def _validate_content(content: Any) -> dict[str, Any]:
        if not isinstance(content, dict):
            raise BadRequestError("MALFORMED_AI_RESPONSE")
        category = content.get("category")
        if not isinstance(category, str) or category not in LETRUSTO_TAXONOMY:
            raise BadRequestError("INVALID_CATEGORY")
        required_text = (
            "subcategory", "title", "description", "seo_title", "seo_meta_description"
        )
        for field in required_text:
            if not isinstance(content.get(field), str) or not content[field].strip():
                raise BadRequestError("INSUFFICIENT_CONTENT")
        if not isinstance(content.get("key_features"), list):
            raise BadRequestError("INSUFFICIENT_CONTENT")
        if not isinstance(content.get("attributes"), dict) or not content["attributes"]:
            raise BadRequestError("INSUFFICIENT_CONTENT")
        if not isinstance(content.get("search_keywords"), list):
            raise BadRequestError("INSUFFICIENT_CONTENT")
        key_features = [item.strip() for item in content["key_features"] if isinstance(item, str)]
        search_keywords = [item.strip() for item in content["search_keywords"] if isinstance(item, str)]
        if len(key_features) != len(content["key_features"]) or len(search_keywords) != len(content["search_keywords"]):
            raise BadRequestError("INSUFFICIENT_CONTENT")
        if not key_features or not search_keywords or not all(key_features) or not all(search_keywords):
            raise BadRequestError("INSUFFICIENT_CONTENT")
        return {
            "category": category,
            "subcategory": content["subcategory"].strip(),
            "title": content["title"].strip(),
            "description": content["description"].strip(),
            "key_features": key_features,
            "attributes": content["attributes"],
            "seo_title": content["seo_title"].strip(),
            "seo_meta_description": content["seo_meta_description"].strip(),
            "search_keywords": search_keywords,
        }

    @staticmethod
    def _deterministic_commercial_result(snapshot: dict[str, Any]) -> dict[str, Any]:
        commercial = snapshot.get("commercial_result")
        if not isinstance(commercial, dict):
            raise BadRequestError("PRICING_FAILURE")
        suggested = commercial.get("minimum_price_inr")
        if suggested is None:
            raise BadRequestError("PRICING_FAILURE")
        return {
            "suggested_selling_price_inr": suggested,
            "summary": {
                "minimum_price_inr": commercial.get("minimum_price_inr"),
                "maximum_price_inr": commercial.get("maximum_price_inr"),
                "target_margin_percent": commercial.get("target_margin_percent"),
                "cac_viable": commercial.get("cac_viable"),
                "failure_reasons": commercial.get("failure_reasons", []),
            },
        }

    @staticmethod
    def _record_failure(
        candidate: SupplierCandidate, snapshot: dict[str, Any], reason: str
    ) -> None:
        candidate.data_snapshot = {
            **snapshot,
            "enrichment": {
                "status": "FAILED",
                "provider": None,
                "failure_reasons": [reason],
            },
        }
        candidate.readiness_status = SupplierCandidateReadinessService.transition(
            candidate.readiness_status, "REVIEW"
        )
