from __future__ import annotations

import time
from decimal import Decimal
from types import SimpleNamespace

import httpx

from app.schemas.supplier_discovery import (
    DiscoveryCommercialReview,
    DiscoveryFailure,
    DiscoveryPhase2Economics,
    DiscoveryProduct,
    DiscoveryRankingFactors,
    DiscoveryScoreBreakdown,
    DiscoveryShippingOption,
    DiscoveryVariant,
    DiscoveryVariantPricing,
    DiscoveryVerdictCounts,
    SupplierDiscoveryResponse,
)
from app.services.commercial_review_service import evaluate_commercial_product
from app.services.launch_pricing_policy import LaunchPricingPolicy, load_launch_pricing_policy
from app.services.pricing_engine import calculate_launch_variant_price
from app.suppliers.base import RawSupplierProduct, SupplierAdapter
from app.suppliers.economics import EconomicsConfig, calculate_economics
from app.suppliers.normalizer import normalize_product
from app.suppliers.scoring import score_product


class SupplierAuthenticationError(RuntimeError):
    pass


class SupplierDiscoveryService:
    def __init__(
        self,
        adapter: SupplierAdapter,
        launch_pricing_policy: LaunchPricingPolicy | None = None,
    ) -> None:
        self.adapter = adapter
        self.launch_pricing_policy = launch_pricing_policy or load_launch_pricing_policy()

    async def discover(
        self, keyword: str, destination: str = "IN", page_size: int = 20
    ) -> SupplierDiscoveryResponse:
        started_at = time.monotonic()
        if not await self.adapter.authenticate():
            raise SupplierAuthenticationError("Supplier authentication failed")

        search_results = await self.adapter.search_products(keyword, page_size=page_size)
        products: list[DiscoveryProduct] = []
        failures: list[DiscoveryFailure] = []
        for search_item in search_results:
            try:
                products.append(await self._process_product(search_item, destination))
            except Exception as exc:
                if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code in {401, 403}:
                    raise SupplierAuthenticationError("Supplier authentication failed during discovery") from exc
                failures.append(
                    DiscoveryFailure(
                        requested_product_id=search_item.supplier_product_id,
                        supplier_sku=search_item.supplier_sku,
                        title=search_item.title,
                        stage=getattr(exc, "discovery_stage", "DETAIL_OR_SHIPPING"),
                        error=str(exc) or type(exc).__name__,
                    )
                )

        products.sort(key=self._sort_key)
        for rank, product in enumerate(products, start=1):
            product.rank = rank

        counts = DiscoveryVerdictCounts(
            approved_candidate=sum(p.recommendation == "APPROVED_CANDIDATE" for p in products),
            review=sum(p.recommendation == "REVIEW" for p in products) + len(failures),
            rejected=sum(p.recommendation == "REJECTED" for p in products),
        )
        return SupplierDiscoveryResponse(
            query=keyword,
            destination=destination,
            elapsed_seconds=round(time.monotonic() - started_at, 3),
            requested_count=page_size,
            returned_count=len(search_results),
            success_count=len(products),
            failed_count=len(failures),
            verdict_counts=counts,
            top_recommendations=products[:3],
            products=products,
            failures=failures,
        )

    async def _process_product(
        self, search_item: RawSupplierProduct, destination: str
    ) -> DiscoveryProduct:
        detail = await self.adapter.get_product(search_item.supplier_product_id, strict=True)
        if detail is None:
            raise _DiscoveryStageError("DETAIL", "Supplier product detail was not found")

        phase2_config = EconomicsConfig()
        normalized = normalize_product(detail, usd_to_inr=phase2_config.usd_to_inr)
        shipping_variant_id = (
            normalized.variants[0].supplier_variant_id
            if normalized.variants
            else normalized.supplier_product_id
        )
        try:
            shipping = await self.adapter.calculate_shipping(
                shipping_variant_id,
                destination,
                origin_country=normalized.warehouse_country or "CN",
                quantity=1,
            )
        except Exception as exc:
            raise _DiscoveryStageError("SHIPPING", str(exc) or type(exc).__name__) from exc

        shipping_usd = shipping.options[0].cost_usd if shipping.options else None
        phase2_economics = calculate_economics(
            normalized,
            shipping_cost_usd=shipping_usd,
            config=phase2_config,
        )
        phase2_score = score_product(
            normalized,
            economics=phase2_economics,
            shipping=shipping,
        )
        launch_shipping_inr = (
            Decimal(str(shipping_usd)) * self.launch_pricing_policy.pricing_fx_rate
            if shipping_usd is not None
            else None
        )

        variant_models: list[DiscoveryVariant] = []
        commercial_variants: list[SimpleNamespace] = []
        calculations = []
        for variant in normalized.variants:
            calculation = None
            if variant.cost_usd is not None and launch_shipping_inr is not None:
                calculation = calculate_launch_variant_price(
                    supplier_cost_usd=Decimal(str(variant.cost_usd)),
                    shipping_cost_inr=launch_shipping_inr,
                    policy=self.launch_pricing_policy,
                )
                calculations.append(calculation)
            variant_models.append(
                DiscoveryVariant(
                    supplier_variant_id=variant.supplier_variant_id,
                    supplier_variant_sku=variant.supplier_variant_sku,
                    name=variant.name,
                    option_key=variant.option_key,
                    image=variant.image,
                    cost_usd=variant.cost_usd,
                    phase2_cost_inr=variant.cost_inr,
                    launch_cost_inr=(
                        Decimal(str(variant.cost_usd)) * self.launch_pricing_policy.pricing_fx_rate
                        if variant.cost_usd is not None
                        else None
                    ),
                    weight_grams=variant.weight_grams,
                    total_inventory=variant.total_inventory,
                    cj_inventory=variant.cj_inventory,
                    factory_inventory=variant.factory_inventory,
                    inventory_verification=variant.inventory_verification,
                    pricing=DiscoveryVariantPricing(
                        selling_price_inr=calculation.selling_price_inr,
                        landed_cost_inr=calculation.landed_cost_inr,
                        contribution_before_cac_inr=calculation.contribution_before_cac_inr,
                        contribution_after_target_cac_inr=calculation.contribution_after_target_cac_inr,
                        max_cac_for_target_margin_inr=calculation.max_cac_for_target_margin_inr,
                        target_margin_met=calculation.target_margin_met,
                        cac_target_supported=calculation.cac_target_supported,
                    ) if calculation else None,
                )
            )
            commercial_variants.append(SimpleNamespace(
                active=True,
                supplier_variant_id=variant.supplier_variant_id,
                supplier_variant_sku=variant.supplier_variant_sku,
                supplier_cost_usd=Decimal(str(variant.cost_usd)) if variant.cost_usd is not None else None,
                selling_price=calculation.selling_price_inr if calculation else None,
            ))

        commercial_product = SimpleNamespace(
            name=normalized.title,
            description=normalized.description,
            supplier=normalized.supplier_id,
            supplier_product_id=normalized.supplier_product_id,
            images=[SimpleNamespace(url=url) for url in normalized.images],
            variants=commercial_variants,
            shipping_cost=launch_shipping_inr,
            cj_inventory=normalized.cj_inventory,
            supplier_validation_status=phase2_score.verdict.value,
            supplier_validation_score=phase2_score.score,
            supplier_validation_notes=phase2_score.notes,
        )
        commercial = evaluate_commercial_product(commercial_product, self.launch_pricing_policy)
        recommendation, recommendation_reasons = self._recommendation(phase2_score.verdict.value, commercial)
        contributions_before = [item.contribution_before_cac_inr for item in calculations]
        contributions_after = [item.contribution_after_target_cac_inr for item in calculations]
        cac_supported_count = sum(item.cac_target_supported for item in calculations)
        ranking = DiscoveryRankingFactors(
            all_priced_variants_positive_before_cac=bool(calculations) and all(value > 0 for value in contributions_before),
            all_priced_variants_support_cac=bool(calculations) and cac_supported_count == len(calculations),
            cac_supported_variant_count=cac_supported_count,
            priced_variant_count=len(calculations),
            min_contribution_before_cac_inr=min(contributions_before) if contributions_before else None,
            max_contribution_before_cac_inr=max(contributions_before) if contributions_before else None,
            min_contribution_after_cac_inr=min(contributions_after) if contributions_after else None,
            max_contribution_after_cac_inr=max(contributions_after) if contributions_after else None,
            supplier_score=phase2_score.score,
            cj_inventory=normalized.cj_inventory,
            data_completeness_score=phase2_score.breakdown.data_completeness,
        )

        return DiscoveryProduct(
            recommendation=recommendation,
            recommendation_reasons=recommendation_reasons,
            canonical_product_id=normalized.supplier_product_id,
            supplier=normalized.supplier_id,
            supplier_sku=normalized.supplier_sku,
            title=normalized.title,
            description=normalized.description,
            category=normalized.category,
            images=normalized.images,
            weight_grams=normalized.weight_grams,
            total_inventory=normalized.source_total_inventory,
            cj_inventory=normalized.cj_inventory,
            factory_inventory=normalized.factory_inventory,
            inventory_verification=normalized.inventory_verification,
            missing_fields=normalized.missing_fields,
            variants=variant_models,
            shipping_based_on_variant_id=shipping_variant_id,
            shipping_can_ship=shipping.can_ship,
            shipping_validation=shipping.validation.value,
            shipping_options=[DiscoveryShippingOption(
                carrier=option.carrier,
                method=option.method,
                cost_usd=option.cost_usd,
                cost_inr=Decimal(str(option.cost_usd)) * self.launch_pricing_policy.pricing_fx_rate,
                estimated_days=option.estimated_days,
                trackable=option.trackable,
            ) for option in shipping.options],
            phase2_score=phase2_score.score,
            phase2_verdict=phase2_score.verdict.value,
            phase2_score_breakdown=DiscoveryScoreBreakdown(**phase2_score.breakdown.__dict__),
            phase2_score_notes=phase2_score.notes,
            phase2_economics=DiscoveryPhase2Economics(
                selling_price_inr=phase2_economics.selling_price_inr,
                contribution_inr=phase2_economics.contribution_inr,
                contribution_pct=phase2_economics.contribution_pct,
                margin_status=phase2_economics.margin_status.value,
                unknown_costs=phase2_economics.unknown_costs,
            ),
            commercial_review=DiscoveryCommercialReview(
                decision=commercial.decision,
                reasons=commercial.reasons,
                blocking_reasons=commercial.blocking_reasons,
                cac_target_supported=commercial.cac_target_supported,
                target_margin_met_count=commercial.target_margin_met_count,
                target_margin_not_met_count=commercial.target_margin_not_met_count,
                valid_variant_count=commercial.valid_variant_count,
                missing_variant_count=commercial.missing_variant_count,
            ),
            ranking_factors=ranking,
        )

    @staticmethod
    def _recommendation(phase2_verdict: str, commercial) -> tuple[str, list[str]]:
        critical = {
            "SHIPPING_COST_INVALID",
            "SUPPLIER_COST_MISSING",
            "NO_SELLABLE_INVENTORY",
            "SUPPLIER_VALIDATION_REJECTED",
        }
        if phase2_verdict == "REJECT" or commercial.decision == "REJECTED" or critical.intersection(commercial.blocking_reasons):
            return "REJECTED", commercial.reasons or ["PHASE2_REJECTED"]
        if commercial.decision == "APPROVED":
            return "APPROVED_CANDIDATE", commercial.reasons
        return "REVIEW", commercial.reasons

    @staticmethod
    def _sort_key(product: DiscoveryProduct) -> tuple:
        factors = product.ranking_factors
        return (
            -int(factors.all_priced_variants_positive_before_cac),
            -int(factors.all_priced_variants_support_cac),
            -factors.cac_supported_variant_count,
            -factors.supplier_score,
            -(factors.cj_inventory if factors.cj_inventory is not None else -1),
            -factors.data_completeness_score,
            -factors.market_evidence_score,
            product.canonical_product_id,
        )


class _DiscoveryStageError(RuntimeError):
    def __init__(self, stage: str, message: str) -> None:
        super().__init__(message)
        self.discovery_stage = stage