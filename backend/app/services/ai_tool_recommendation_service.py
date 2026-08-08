from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from app.models.entities import AITool, AIToolFactProvenance
from app.repositories.ai_tool_repository import AIToolRepository
from app.schemas.ai_tool import (
    AIToolRecommendationConfidence,
    AIToolRecommendationDiagnostic,
    AIToolRecommendationExplanation,
    AIToolRecommendationFactor,
    AIToolRecommendationFactors,
    AIToolRecommendationIntent,
    AIToolRecommendationPenalty,
    AIToolRecommendationProvenance,
    AIToolRecommendationRequest,
    AIToolRecommendationResponse,
    AIToolRecommendationResult,
)
from app.services.ai_tool_mapper import to_ai_tool_dto
from app.services.ai_tool_provenance_catalog import is_strict_supported_row


FACTOR_WEIGHTS: dict[str, Decimal] = {
    "category": Decimal("0.20"),
    "use_case": Decimal("0.20"),
    "feature": Decimal("0.20"),
    "platform": Decimal("0.10"),
    "integration": Decimal("0.10"),
    "budget": Decimal("0.15"),
    "experience": Decimal("0.05"),
}


@dataclass(slots=True)
class ScoredTool:
    tool: AITool
    score: Decimal
    factors: AIToolRecommendationFactors
    explanation: AIToolRecommendationExplanation
    confidence: AIToolRecommendationConfidence
    provenance: list[AIToolRecommendationProvenance]


class AIToolRecommendationService:
    def __init__(self, repository: AIToolRepository) -> None:
        self.repository = repository

    def recommend(self, request: AIToolRecommendationRequest) -> AIToolRecommendationResponse:
        recommendation_id = str(uuid4())
        intent = request.intent or AIToolRecommendationIntent()

        diagnostics: list[AIToolRecommendationDiagnostic] = []
        if intent.budget and intent.budget.min is not None and intent.budget.max is not None:
            if intent.budget.min > intent.budget.max:
                return self._empty_response(
                    recommendation_id=recommendation_id,
                    status="conflicting_requirements",
                    query=request.query,
                    intent=intent,
                    diagnostics=[
                        AIToolRecommendationDiagnostic(
                            code="budget_range_invalid",
                            message="Budget min is greater than budget max.",
                        )
                    ],
                    message="Your budget constraints conflict. Please adjust your range.",
                )

        active_requirement_count = self._active_requirement_count(intent)
        if active_requirement_count == 0:
            return self._empty_response(
                recommendation_id=recommendation_id,
                status="insufficient_data",
                query=request.query,
                intent=intent,
                diagnostics=[
                    AIToolRecommendationDiagnostic(
                        code="insufficient_data",
                        message="Provide at least one requirement to receive a deterministic recommendation.",
                    )
                ],
                message="Please provide at least one requirement such as category, use case, features, or budget.",
            )

        candidates = self.repository.list_published()
        if intent.category:
            candidates = [tool for tool in candidates if tool.category.slug == intent.category]

        if not candidates:
            return self._empty_response(
                recommendation_id=recommendation_id,
                status="no_match",
                query=request.query,
                intent=intent,
                diagnostics=[
                    AIToolRecommendationDiagnostic(
                        code="no_candidates",
                        message="No published tools available for the requested category.",
                    )
                ],
                message="No published tools matched your requested category.",
            )

        if intent.requiredFeatures and not self._any_feature_supported(candidates, intent.requiredFeatures):
            return self._empty_response(
                recommendation_id=recommendation_id,
                status="unsupported_feature",
                query=request.query,
                intent=intent,
                diagnostics=[
                    AIToolRecommendationDiagnostic(
                        code="unsupported_feature",
                        message="No published tool currently supports the required feature set.",
                    )
                ],
                message="No published tools currently match those required features.",
            )

        provenance_by_tool = self.repository.get_fact_provenance([tool.id for tool in candidates])

        scored: list[ScoredTool] = []
        for tool in candidates:
            persisted_rows = provenance_by_tool.get(str(tool.id), [])
            strict_rows = [
                row
                for row in persisted_rows
                if is_strict_supported_row(
                    slug=tool.slug,
                    fact_type=row.fact_type,
                    fact_key=row.fact_key,
                    source_kind=row.source_kind,
                    source_url=row.source_url,
                )
            ]
            scored.append(self._score_tool(tool, intent, strict_rows))
        scored.sort(key=lambda row: (-row.score, row.tool.name.lower()))

        pricing_model = intent.pricingPreference.model if intent.pricingPreference else None
        if (intent.budget and intent.budget.max is not None) or pricing_model == "free_only":
            within_budget = [row for row in scored if self._is_within_budget(row.tool, intent)]
            comparable_budget_candidates = [
                row for row in scored if self._is_budget_comparable(row.tool, intent)
            ]

            should_enforce_hard_budget = pricing_model == "free_only" or bool(comparable_budget_candidates)
            if should_enforce_hard_budget and not within_budget:
                return self._empty_response(
                    recommendation_id=recommendation_id,
                    status="overconstrained_budget",
                    query=request.query,
                    intent=intent,
                    diagnostics=[
                        AIToolRecommendationDiagnostic(
                            code="budget_no_match",
                            message="No published tool satisfies the specified budget constraint.",
                        )
                    ],
                    message="No published tools fit the specified budget. Try increasing your budget or relaxing pricing constraints.",
                )
            if within_budget:
                scored = within_budget

        matching = [row for row in scored if row.score > Decimal("0")]
        if not matching:
            return self._empty_response(
                recommendation_id=recommendation_id,
                status="no_match",
                query=request.query,
                intent=intent,
                diagnostics=[
                    AIToolRecommendationDiagnostic(
                        code="match_score_zero",
                        message="Published tools were found, but none matched the provided requirements.",
                    )
                ],
                message="No tools matched your requirements strongly enough. Try relaxing one or more constraints.",
            )

        limited = matching[: request.limit]
        labels = self._derive_result_labels(limited)

        results = [
            AIToolRecommendationResult(
                rank=index + 1,
                resultLabel=labels[index],
                aiTool=to_ai_tool_dto(row.tool),
                overallMatchScore=row.score,
                factors=row.factors,
                explanation=row.explanation,
                confidence=row.confidence,
                provenance=row.provenance,
            )
            for index, row in enumerate(limited)
        ]

        return AIToolRecommendationResponse(
            recommendationId=recommendation_id,
            status="ok",
            query=request.query,
            intent=intent,
            results=results,
            diagnostics=diagnostics,
            followUpQuestions=self._build_follow_up_questions(intent),
            message="Recommendations are ranked by deterministic requirement matching over published AI tool metadata.",
            generatedAt=datetime.now(timezone.utc).isoformat(),
        )

    def _score_tool(
        self,
        tool: AITool,
        intent: AIToolRecommendationIntent,
        provenance_rows: list[AIToolFactProvenance],
    ) -> ScoredTool:
        penalties: list[AIToolRecommendationPenalty] = []

        category_factor = self._score_exact_field(
            user_values=[intent.category] if intent.category else [],
            tool_values=[tool.category.slug],
            weight=FACTOR_WEIGHTS["category"],
        )
        use_case_factor = self._score_overlap_field(intent.useCases, tool.use_cases or [], FACTOR_WEIGHTS["use_case"])
        feature_factor = self._score_overlap_field(intent.requiredFeatures, tool.features or [], FACTOR_WEIGHTS["feature"])
        platform_factor = self._score_overlap_field(intent.platforms, tool.platforms or [], FACTOR_WEIGHTS["platform"])
        integration_factor = self._score_overlap_field(intent.integrations, tool.integrations or [], FACTOR_WEIGHTS["integration"])
        budget_factor, budget_penalties = self._score_budget(intent, tool)
        penalties.extend(budget_penalties)
        experience_factor = self._score_experience(intent.experienceLevel, tool)

        raw_score = (
            category_factor.score * category_factor.weight
            + use_case_factor.score * use_case_factor.weight
            + feature_factor.score * feature_factor.weight
            + platform_factor.score * platform_factor.weight
            + integration_factor.score * integration_factor.weight
            + budget_factor.score * budget_factor.weight
            + experience_factor.score * experience_factor.weight
        )
        penalty_sum = sum((penalty.delta for penalty in penalties), Decimal("0"))
        score = self._clamp(raw_score + penalty_sum, Decimal("0"), Decimal("100"))

        factors = AIToolRecommendationFactors(
            categoryMatch=category_factor,
            useCaseMatch=use_case_factor,
            featureMatch=feature_factor,
            platformMatch=platform_factor,
            integrationMatch=integration_factor,
            budgetMatch=budget_factor,
            experienceMatch=experience_factor,
            penalties=penalties,
            overallMatchScore=score,
        )

        explanation = self._build_explanation(intent, tool, factors)
        provenance = self._build_provenance(tool, factors, provenance_rows)
        confidence = self._build_confidence(intent, tool, factors, provenance_rows)

        return ScoredTool(
            tool=tool,
            score=score,
            factors=factors,
            explanation=explanation,
            confidence=confidence,
            provenance=provenance,
        )

    def _score_exact_field(
        self,
        user_values: list[str | None],
        tool_values: list[str],
        weight: Decimal,
    ) -> AIToolRecommendationFactor:
        cleaned_user = [self._normalize_token(value) for value in user_values if value]
        cleaned_tool = [self._normalize_token(value) for value in tool_values if value]

        if not cleaned_user:
            return AIToolRecommendationFactor(score=Decimal("0"), weight=Decimal("0"))

        match = [value for value in cleaned_user if value in cleaned_tool]
        score = Decimal("100") if match else Decimal("0")

        return AIToolRecommendationFactor(
            score=score,
            weight=weight,
            matchedInputs=match,
            matchedToolValues=match,
            missingRequiredInputs=[value for value in cleaned_user if value not in match],
            missingToolData=[] if cleaned_tool else ["missing_tool_data"],
        )

    def _score_overlap_field(self, user_values: list[str], tool_values: list[str], weight: Decimal) -> AIToolRecommendationFactor:
        cleaned_user = [self._normalize_token(value) for value in user_values if value]
        cleaned_tool = [self._normalize_token(value) for value in tool_values if value]

        if not cleaned_user:
            return AIToolRecommendationFactor(score=Decimal("0"), weight=Decimal("0"))

        if not cleaned_tool:
            return AIToolRecommendationFactor(
                score=Decimal("0"),
                weight=weight,
                missingRequiredInputs=cleaned_user,
                missingToolData=["missing_tool_data"],
            )

        matches = [value for value in cleaned_user if any(value in tool_item for tool_item in cleaned_tool)]
        ratio = Decimal(str(len(matches))) / Decimal(str(len(cleaned_user)))
        score = (ratio * Decimal("100")).quantize(Decimal("0.01"))

        return AIToolRecommendationFactor(
            score=score,
            weight=weight,
            matchedInputs=matches,
            matchedToolValues=[item for item in cleaned_tool if any(match in item for match in matches)],
            missingRequiredInputs=[value for value in cleaned_user if value not in matches],
            missingToolData=[],
        )

    def _score_budget(
        self,
        intent: AIToolRecommendationIntent,
        tool: AITool,
    ) -> tuple[AIToolRecommendationFactor, list[AIToolRecommendationPenalty]]:
        penalties: list[AIToolRecommendationPenalty] = []
        pricing_model = intent.pricingPreference.model if intent.pricingPreference else None
        free_constraint = pricing_model in {"free_only", "prefer_free"} or bool(
            intent.pricingPreference and intent.pricingPreference.preferFreePlan
        )
        weight = FACTOR_WEIGHTS["budget"] if intent.budget or free_constraint else Decimal("0")

        if weight == Decimal("0"):
            return AIToolRecommendationFactor(score=Decimal("0"), weight=Decimal("0")), penalties

        if pricing_model == "free_only":
            if tool.has_free_plan:
                return (
                    AIToolRecommendationFactor(
                        score=Decimal("100"),
                        weight=weight,
                        matchedInputs=["free_plan"],
                        matchedToolValues=["free_plan"],
                    ),
                    penalties,
                )
            penalties.append(
                AIToolRecommendationPenalty(
                    code="budget_exceeded",
                    delta=Decimal("-15"),
                    reason="Tool does not provide a free plan while free-only is required.",
                )
            )
            return (
                AIToolRecommendationFactor(
                    score=Decimal("0"),
                    weight=weight,
                    missingRequiredInputs=["free_only"],
                    missingToolData=[] if tool.has_free_plan is not None else ["free_plan_availability"],
                ),
                penalties,
            )

        if intent.pricingPreference and intent.pricingPreference.preferFreePlan:
            if tool.has_free_plan:
                return (
                    AIToolRecommendationFactor(
                        score=Decimal("100"),
                        weight=weight,
                        matchedInputs=["prefer_free"],
                        matchedToolValues=["free_plan"],
                    ),
                    penalties,
                )

            penalties.append(
                AIToolRecommendationPenalty(
                    code="insufficient_verified_data" if tool.has_free_plan is None else "budget_exceeded",
                    delta=Decimal("-6"),
                    reason=(
                        "Free-plan availability is unknown for this tool."
                        if tool.has_free_plan is None
                        else "Tool does not include a free plan; paid tiers may be required."
                    ),
                )
            )


        if intent.budget is None or intent.budget.max is None:
            return AIToolRecommendationFactor(score=Decimal("0"), weight=weight), penalties

        if tool.pricing_amount is None:
            penalties.append(
                AIToolRecommendationPenalty(
                    code="insufficient_verified_data",
                    delta=Decimal("-4"),
                    reason="Pricing amount is missing for this tool.",
                )
            )
            return (
                AIToolRecommendationFactor(
                    score=Decimal("0"),
                    weight=weight,
                    missingRequiredInputs=["budget_max"],
                    missingToolData=["pricing_amount"],
                ),
                penalties,
            )

        if (
            intent.budget.currency
            and tool.pricing_currency
            and intent.budget.currency.upper() != tool.pricing_currency.upper()
        ):
            penalties.append(
                AIToolRecommendationPenalty(
                    code="insufficient_verified_data",
                    delta=Decimal("-2"),
                    reason="Budget currency cannot be directly compared to tool pricing currency.",
                )
            )
            return (
                AIToolRecommendationFactor(
                    score=Decimal("0"),
                    weight=weight,
                    missingRequiredInputs=["budget_currency_match"],
                    matchedToolValues=[f"pricing_currency_{tool.pricing_currency.lower()}"],
                ),
                penalties,
            )

        if tool.pricing_amount <= intent.budget.max:
            return (
                AIToolRecommendationFactor(
                    score=Decimal("100"),
                    weight=weight,
                    matchedInputs=[f"max_{intent.budget.max}"],
                    matchedToolValues=[f"price_{tool.pricing_amount}"],
                ),
                penalties,
            )

        over_ratio = (tool.pricing_amount - intent.budget.max) / max(intent.budget.max, Decimal("1"))
        penalty = min(Decimal("20"), (over_ratio * Decimal("20")).quantize(Decimal("0.01")))
        penalties.append(
            AIToolRecommendationPenalty(
                code="budget_exceeded",
                delta=-penalty,
                reason="Tool pricing exceeds the requested budget.",
            )
        )
        return (
            AIToolRecommendationFactor(
                score=Decimal("0"),
                weight=weight,
                missingRequiredInputs=["budget_fit"],
                matchedToolValues=[f"price_{tool.pricing_amount}"],
            ),
            penalties,
        )

    def _score_experience(self, experience: str | None, tool: AITool) -> AIToolRecommendationFactor:
        if not experience:
            return AIToolRecommendationFactor(score=Decimal("0"), weight=Decimal("0"))

        searchable = [self._normalize_token(value) for value in (tool.best_for or []) + (tool.not_ideal_for or []) + (tool.tags or [])]
        if not searchable:
            return AIToolRecommendationFactor(
                score=Decimal("0"),
                weight=FACTOR_WEIGHTS["experience"],
                missingToolData=["best_for", "not_ideal_for", "tags"],
            )

        token = self._normalize_token(experience)
        match = any(token in value for value in searchable)

        return AIToolRecommendationFactor(
            score=Decimal("100") if match else Decimal("0"),
            weight=FACTOR_WEIGHTS["experience"],
            matchedInputs=[token] if match else [],
            matchedToolValues=[value for value in searchable if token in value],
            missingRequiredInputs=[] if match else [token],
        )

    def _build_explanation(
        self,
        intent: AIToolRecommendationIntent,
        tool: AITool,
        factors: AIToolRecommendationFactors,
    ) -> AIToolRecommendationExplanation:
        reasons: list[str] = []
        trade_offs: list[str] = []
        covered: list[str] = []
        missing: list[str] = []

        if factors.categoryMatch.score > 0:
            reasons.append(f"Matches requested category {tool.category.name}.")
            covered.append("category")

        if factors.useCaseMatch.score > 0:
            reasons.append("Supports requested use cases based on verified use case metadata.")
            covered.append("use_cases")
        elif intent.useCases:
            missing.append("use_cases")

        if factors.featureMatch.score > 0:
            reasons.append("Contains required features in the published feature list.")
            covered.append("required_features")
        elif intent.requiredFeatures:
            missing.append("required_features")
            trade_offs.append("Some required features are missing in published metadata.")

        if factors.platformMatch.score > 0:
            covered.append("platforms")
        elif intent.platforms:
            missing.append("platforms")
            trade_offs.append("Requested platforms are not fully covered.")

        if factors.integrationMatch.score > 0:
            covered.append("integrations")
        elif intent.integrations:
            missing.append("integrations")
            trade_offs.append("Requested integrations are not fully covered.")

        if factors.budgetMatch.score > 0:
            covered.append("budget")
        elif intent.budget:
            missing.append("budget")

        for penalty in factors.penalties:
            trade_offs.append(penalty.reason)

        if not reasons:
            reasons.append("This tool ranks highest among published options for your current constraints.")

        return AIToolRecommendationExplanation(
            whyRecommended=self._dedupe(reasons),
            tradeOffs=self._dedupe(trade_offs),
            coveredRequirements=self._dedupe(covered),
            missingRequirements=self._dedupe(missing),
            disclaimer="Match score reflects fit to your requirements, not universal quality." if factors.overallMatchScore > 0 else None,
        )

    def _build_confidence(
        self,
        intent: AIToolRecommendationIntent,
        tool: AITool,
        factors: AIToolRecommendationFactors,
        provenance_rows: list[AIToolFactProvenance],
    ) -> AIToolRecommendationConfidence:
        total_fields = Decimal("8")
        present_fields = Decimal("0")

        if tool.use_cases:
            present_fields += Decimal("1")
        if tool.features:
            present_fields += Decimal("1")
        if tool.platforms:
            present_fields += Decimal("1")
        if tool.integrations:
            present_fields += Decimal("1")
        if tool.pricing_model:
            present_fields += Decimal("1")
        if tool.pricing_amount is not None or tool.has_free_plan is not None:
            present_fields += Decimal("1")
        if tool.last_verified_at is not None:
            present_fields += Decimal("1")
        if tool.best_for or tool.not_ideal_for:
            present_fields += Decimal("1")

        metadata_completeness = (present_fields / total_fields * Decimal("100")).quantize(Decimal("0.01"))
        if provenance_rows:
            fact_types = {row.fact_type for row in provenance_rows}
            coverage_bonus = min(Decimal("12"), Decimal(str(len(fact_types))) * Decimal("3"))
            provenance_strength = Decimal("78") + coverage_bonus
        elif tool.pricing_url or tool.website_url:
            provenance_strength = Decimal("58")
        else:
            provenance_strength = Decimal("30")

        freshness = Decimal("40")
        if tool.last_verified_at is not None:
            verified_at = tool.last_verified_at
            if verified_at.tzinfo is None:
                verified_at = verified_at.replace(tzinfo=timezone.utc)
            days_old = (datetime.now(timezone.utc) - verified_at).days
            if days_old <= 30:
                freshness = Decimal("95")
            elif days_old <= 90:
                freshness = Decimal("75")
            else:
                freshness = Decimal("55")

        active_count = max(1, self._active_requirement_count(intent))
        covered_count = 0
        if intent.category and factors.categoryMatch.score > 0:
            covered_count += 1
        if intent.useCases and factors.useCaseMatch.score > 0:
            covered_count += 1
        if intent.requiredFeatures and factors.featureMatch.score > 0:
            covered_count += 1
        if intent.platforms and factors.platformMatch.score > 0:
            covered_count += 1
        if intent.integrations and factors.integrationMatch.score > 0:
            covered_count += 1
        pricing_model = intent.pricingPreference.model if intent.pricingPreference else None
        pricing_is_constraining = pricing_model in {"free_only", "prefer_free"} or bool(
            intent.pricingPreference
            and (intent.pricingPreference.preferFreePlan or intent.pricingPreference.preferFreeTrial)
        )
        if (intent.budget or pricing_is_constraining) and factors.budgetMatch.score > 0:
            covered_count += 1
        if intent.experienceLevel and factors.experienceMatch.score > 0:
            covered_count += 1
        requirement_coverage = (Decimal(str(covered_count)) / Decimal(str(active_count)) * Decimal("100")).quantize(Decimal("0.01"))

        score = (
            metadata_completeness * Decimal("0.35")
            + provenance_strength * Decimal("0.30")
            + freshness * Decimal("0.20")
            + requirement_coverage * Decimal("0.15")
        ).quantize(Decimal("0.01"))

        missing_data_flags: list[str] = []
        if tool.pricing_amount is None and intent.budget and intent.budget.max is not None:
            missing_data_flags.append("missing_pricing_for_budget_match")
            score = min(score, Decimal("55"))

        if not provenance_rows and (tool.pricing_url or tool.website_url):
            missing_data_flags.append("using_fallback_source_metadata")
        if not provenance_rows and not (tool.pricing_url or tool.website_url):
            missing_data_flags.append("missing_source_provenance")

        if factors.featureMatch.missingToolData and intent.requiredFeatures:
            missing_data_flags.append("missing_feature_metadata")
            score = min(score, Decimal("60"))

        level = "low"
        if score >= Decimal("75"):
            level = "high"
        elif score >= Decimal("50"):
            level = "medium"

        return AIToolRecommendationConfidence(
            score=score,
            level=level,
            metadataCompleteness=metadata_completeness,
            provenanceStrength=provenance_strength,
            freshness=freshness,
            requirementCoverage=requirement_coverage,
            missingDataFlags=missing_data_flags,
        )

    def _build_provenance(
        self,
        tool: AITool,
        factors: AIToolRecommendationFactors,
        provenance_rows: list[AIToolFactProvenance],
    ) -> list[AIToolRecommendationProvenance]:
        if provenance_rows:
            return [
                AIToolRecommendationProvenance(
                    aiToolId=str(row.ai_tool_id),
                    factType=row.fact_type,
                    factKey=row.fact_key,
                    sourceUrl=row.source_url,
                    sourceKind=row.source_kind,
                    verifiedAt=row.verified_at.isoformat() if row.verified_at else None,
                )
                for row in provenance_rows
            ]

        items: list[AIToolRecommendationProvenance] = []

        if tool.pricing_url:
            items.append(
                AIToolRecommendationProvenance(
                    aiToolId=str(tool.id),
                    factType="pricing",
                    factKey=tool.pricing_model or "pricing",
                    sourceUrl=tool.pricing_url,
                    sourceKind="official_provider",
                    verifiedAt=tool.last_verified_at.isoformat() if tool.last_verified_at else None,
                )
            )

        for feature in factors.featureMatch.matchedInputs[:2]:
            items.append(
                AIToolRecommendationProvenance(
                    aiToolId=str(tool.id),
                    factType="feature",
                    factKey=feature,
                    sourceUrl=tool.website_url,
                    sourceKind="official_provider",
                    verifiedAt=tool.last_verified_at.isoformat() if tool.last_verified_at else None,
                )
            )

        for platform in factors.platformMatch.matchedInputs[:2]:
            items.append(
                AIToolRecommendationProvenance(
                    aiToolId=str(tool.id),
                    factType="platform",
                    factKey=platform,
                    sourceUrl=tool.website_url,
                    sourceKind="official_provider",
                    verifiedAt=tool.last_verified_at.isoformat() if tool.last_verified_at else None,
                )
            )

        for integration in factors.integrationMatch.matchedInputs[:2]:
            items.append(
                AIToolRecommendationProvenance(
                    aiToolId=str(tool.id),
                    factType="integration",
                    factKey=integration,
                    sourceUrl=tool.website_url,
                    sourceKind="official_provider",
                    verifiedAt=tool.last_verified_at.isoformat() if tool.last_verified_at else None,
                )
            )

        for use_case in factors.useCaseMatch.matchedInputs[:2]:
            items.append(
                AIToolRecommendationProvenance(
                    aiToolId=str(tool.id),
                    factType="use_case",
                    factKey=use_case,
                    sourceUrl=tool.website_url,
                    sourceKind="official_provider",
                    verifiedAt=tool.last_verified_at.isoformat() if tool.last_verified_at else None,
                )
            )

        return items

    def _derive_result_labels(self, results: list[ScoredTool]) -> list[str]:
        if not results:
            return []

        labels = ["strong_alternative" for _ in results]
        labels[0] = "best_match"

        if len(results) > 1:
            budget_index = self._find_budget_option_index(results)
            if budget_index is not None and budget_index != 0:
                labels[budget_index] = "budget_option"

        return labels

    def _find_budget_option_index(self, results: list[ScoredTool]) -> int | None:
        priced: list[tuple[int, Decimal]] = []
        for index, row in enumerate(results):
            if row.tool.has_free_plan:
                return index
            if row.tool.pricing_amount is not None:
                priced.append((index, row.tool.pricing_amount))

        if not priced:
            return None

        priced.sort(key=lambda pair: pair[1])
        return priced[0][0]

    def _build_follow_up_questions(self, intent: AIToolRecommendationIntent) -> list[str]:
        questions: list[str] = []
        if not intent.category:
            questions.append("Which AI tool category should I focus on?")
        if not intent.useCases:
            questions.append("What is your main use case?")
        if not intent.requiredFeatures:
            questions.append("Which features are must-have for you?")
        if intent.budget is None:
            questions.append("Do you have a monthly or yearly budget range?")
        return questions[:4]

    def _empty_response(
        self,
        recommendation_id: str,
        status: str,
        query: str | None,
        intent: AIToolRecommendationIntent,
        diagnostics: list[AIToolRecommendationDiagnostic],
        message: str,
    ) -> AIToolRecommendationResponse:
        return AIToolRecommendationResponse(
            recommendationId=recommendation_id,
            status=status,
            query=query,
            intent=intent,
            results=[],
            diagnostics=diagnostics,
            followUpQuestions=self._build_follow_up_questions(intent),
            message=message,
            generatedAt=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def _normalize_token(value: str) -> str:
        return " ".join(value.strip().lower().replace("_", " ").split())

    @staticmethod
    def _dedupe(items: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in items:
            normalized = item.strip()
            if not normalized:
                continue
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(normalized)
        return out

    @staticmethod
    def _clamp(value: Decimal, low: Decimal, high: Decimal) -> Decimal:
        return max(low, min(high, value.quantize(Decimal("0.01"))))

    @staticmethod
    def _active_requirement_count(intent: AIToolRecommendationIntent) -> int:
        count = 0
        if intent.category:
            count += 1
        if intent.useCases:
            count += 1
        if intent.requiredFeatures:
            count += 1
        if intent.platforms:
            count += 1
        if intent.integrations:
            count += 1
        pricing_model = intent.pricingPreference.model if intent.pricingPreference else None
        pricing_is_constraining = pricing_model in {"free_only", "prefer_free"} or bool(
            intent.pricingPreference
            and (intent.pricingPreference.preferFreePlan or intent.pricingPreference.preferFreeTrial)
        )
        if intent.budget or pricing_is_constraining:
            count += 1
        if intent.experienceLevel:
            count += 1
        return count

    @staticmethod
    def _any_feature_supported(candidates: list[AITool], required_features: list[str]) -> bool:
        normalized_required = [item.strip().lower() for item in required_features if item.strip()]
        for tool in candidates:
            normalized_features = [item.strip().lower() for item in tool.features or []]
            if any(any(req in feature for feature in normalized_features) for req in normalized_required):
                return True
        return False

    @staticmethod
    def _is_within_budget(tool: AITool, intent: AIToolRecommendationIntent) -> bool:
        if intent.pricingPreference and intent.pricingPreference.model == "free_only":
            return bool(tool.has_free_plan)

        if intent.budget is None or intent.budget.max is None:
            return True

        if tool.pricing_amount is None:
            return False

        if (
            intent.budget.currency
            and tool.pricing_currency
            and intent.budget.currency.upper() != tool.pricing_currency.upper()
        ):
            return True

        return tool.pricing_amount <= intent.budget.max

    @staticmethod
    def _is_budget_comparable(tool: AITool, intent: AIToolRecommendationIntent) -> bool:
        if intent.budget is None or intent.budget.max is None or tool.pricing_amount is None:
            return False

        if (
            intent.budget.currency
            and tool.pricing_currency
            and intent.budget.currency.upper() != tool.pricing_currency.upper()
        ):
            return False

        return True
