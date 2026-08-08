from app.models.entities import AITool
from app.schemas.ai_tool import AIToolCategoryDTO, AIToolDTO, AIToolPricingDTO


def to_ai_tool_dto(tool: AITool) -> AIToolDTO:
    return AIToolDTO(
        id=tool.slug,
        slug=tool.slug,
        name=tool.name,
        provider=tool.provider,
        description=tool.description,
        websiteUrl=tool.website_url,
        logoUrl=tool.logo_url,
        category=AIToolCategoryDTO(
            id=tool.category.id,
            name=tool.category.name,
            slug=tool.category.slug,
            position=tool.category.position,
        ),
        lifecycleStatus=tool.lifecycle_status,
        pricing=AIToolPricingDTO(
            model=tool.pricing_model,
            amount=tool.pricing_amount,
            currency=tool.pricing_currency,
            period=tool.pricing_period,
            hasFreePlan=tool.has_free_plan,
            hasFreeTrial=tool.has_free_trial,
            trialDays=tool.trial_days,
            notes=tool.pricing_notes,
            pricingUrl=tool.pricing_url,
        ),
        letrustoScore=tool.letrusto_score,
        useCases=tool.use_cases or [],
        features=tool.features or [],
        pros=tool.pros or [],
        cons=tool.cons or [],
        bestFor=tool.best_for or [],
        notIdealFor=tool.not_ideal_for or [],
        whyLetrustoRecommends=tool.why_letrusto_recommends,
        tags=tool.tags or [],
        platforms=tool.platforms or [],
        integrations=tool.integrations or [],
        affiliateAvailable=tool.affiliate_available,
        affiliateUrl=tool.affiliate_url,
        lastVerifiedAt=tool.last_verified_at.isoformat() if tool.last_verified_at else None,
    )
