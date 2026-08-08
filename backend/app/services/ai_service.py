from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from statistics import median
from uuid import uuid4

from app.ai.prompts import (
    ASSISTANT_SYSTEM_PROMPT,
    BUYING_GUIDE_PROMPT,
    COMPARE_SUMMARY_PROMPT,
    RECOMMENDATION_EXPLAINER_PROMPT,
    REVIEW_SUMMARY_PROMPT,
)
from app.ai.providers.base import GenerationRequest, LLMProvider
from app.core.exceptions import NotFoundError
from app.models.entities import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.ai_tool import AIToolRecommendationResponse
from app.schemas.ai import (
    AssistantMessageResponse,
    BuyingGuideResponse,
    ComparisonSummaryResponse,
    RecommendationWorkflowResponse,
    RankedRecommendationDTO,
    ReviewSummaryResponse,
    ShoppingIntentDTO,
)
from app.services.ai_tool_intent_router import AIToolIntentRouter
from app.services.ai_tool_recommendation_service import AIToolRecommendationService
from app.schemas.product import ProductDTO
from app.services.product_mapper import to_product_dto


CATEGORY_HINTS: dict[str, set[str]] = {
    "phone": {"phone", "smartphone", "android", "iphone", "camera phone"},
    "laptop": {"laptop", "notebook", "ultrabook", "macbook"},
    "headphones": {"headphone", "headphones", "earbuds", "anc"},
    "smartwatch": {"smartwatch", "watch", "fitness watch"},
    "television": {"tv", "television", "oled", "qled"},
    "refrigerator": {"fridge", "refrigerator"},
    "washing-machine": {"washing machine", "washer"},
    "gaming": {"gaming", "console", "ps5", "xbox", "handheld"},
    "tablet": {"tablet", "ipad"},
    "camera": {"camera", "dslr", "mirrorless"},
}

USAGE_HINTS: dict[str, set[str]] = {
    "gaming": {"gaming", "fps", "performance", "graphics"},
    "photography": {"camera", "photo", "portrait", "video", "vlog"},
    "office": {"office", "meetings", "calls", "work"},
    "travel": {"travel", "portable", "flight", "trip"},
    "fitness": {"fitness", "health", "workout", "running"},
    "study": {"student", "study", "college", "classes"},
    "coding": {"coding", "developer", "programming", "python"},
}

PRIORITY_HINTS: dict[str, set[str]] = {
    "battery": {"battery", "backup", "all-day"},
    "camera": {"camera", "photo", "video", "zoom"},
    "performance": {"fast", "performance", "processor", "chip"},
    "display": {"display", "screen", "oled", "brightness"},
    "value": {"value", "money", "budget", "worth"},
}

GREETING_WORDS = {
    "hello",
    "hi",
    "hey",
    "namaste",
    "good morning",
    "good evening",
}


@dataclass(slots=True)
class SessionContext:
    session_id: str
    created_at: datetime
    updated_at: datetime
    history: list[dict[str, str]] = field(default_factory=list)
    last_intent: ShoppingIntentDTO | None = None


class InMemorySessionStore:
    def __init__(self, ttl_minutes: int = 120) -> None:
        self.ttl = timedelta(minutes=max(5, ttl_minutes))
        self._sessions: dict[str, SessionContext] = {}

    def get_or_create(self, session_id: str | None = None) -> SessionContext:
        self._cleanup_expired()

        if session_id and session_id in self._sessions:
            return self._sessions[session_id]

        sid = session_id or str(uuid4())
        now = datetime.now(timezone.utc)
        context = SessionContext(session_id=sid, created_at=now, updated_at=now)
        self._sessions[sid] = context
        return context

    def update(self, context: SessionContext) -> None:
        context.updated_at = datetime.now(timezone.utc)
        self._sessions[context.session_id] = context

    def _cleanup_expired(self) -> None:
        now = datetime.now(timezone.utc)
        expired = [sid for sid, ctx in self._sessions.items() if now - ctx.updated_at > self.ttl]
        for sid in expired:
            self._sessions.pop(sid, None)


class AIService:
    def __init__(
        self,
        repository: ProductRepository,
        provider: LLMProvider,
        session_store: InMemorySessionStore,
        ai_tool_intent_router: AIToolIntentRouter | None = None,
        ai_tool_recommendation_service: AIToolRecommendationService | None = None,
    ) -> None:
        self.repository = repository
        self.provider = provider
        self.session_store = session_store
        self.ai_tool_intent_router = ai_tool_intent_router
        self.ai_tool_recommendation_service = ai_tool_recommendation_service

    def chat_assistant(self, message: str, session_id: str | None = None, limit: int = 4) -> AssistantMessageResponse:
        context = self.session_store.get_or_create(session_id)

        parsed_intent = self._parse_intent(message)
        merged_intent = self._merge_intent(parsed_intent, context.last_intent)
        workflow = self._build_recommendation_workflow(merged_intent, limit=max(1, limit))

        ai_tool_reply = self._build_ai_tool_reply(message, limit=max(1, limit))
        if ai_tool_reply:
            draft_reply = ai_tool_reply
        elif self._is_general_knowledge_query(message):
            draft_reply = self._build_general_knowledge_reply(message)
        else:
            draft_reply = self._build_assistant_reply(message, workflow)
        llm_text = self.provider.generate(
            GenerationRequest(
                systemPrompt=ASSISTANT_SYSTEM_PROMPT,
                userPrompt=RECOMMENDATION_EXPLAINER_PROMPT,
                variables={"draft": draft_reply},
            )
        ).text

        context.history.append({"role": "user", "content": message})
        context.history.append({"role": "assistant", "content": llm_text})
        context.last_intent = merged_intent
        self.session_store.update(context)

        return AssistantMessageResponse(
            sessionId=context.session_id,
            reply=llm_text,
            workflow=workflow,
        )

    def _build_ai_tool_reply(self, message: str, limit: int) -> str | None:
        if not self.ai_tool_intent_router or not self.ai_tool_recommendation_service:
            return None

        if not self.ai_tool_intent_router.is_ai_tool_request(message):
            return None

        try:
            request = self.ai_tool_intent_router.build_request(message, limit=limit)
            recommendation = self.ai_tool_recommendation_service.recommend(request)
        except Exception:
            return None

        return self._format_ai_tool_recommendation_reply(recommendation)

    @staticmethod
    def _format_ai_tool_recommendation_reply(recommendation: AIToolRecommendationResponse) -> str:
        if recommendation.status != "ok" or not recommendation.results:
            return recommendation.message

        lines = ["I routed this request through the AI tool recommendation engine."]
        for result in recommendation.results[:3]:
            reasons = "; ".join(result.explanation.whyRecommended[:2])
            lines.append(
                f"- {result.aiTool.name} ({result.overallMatchScore}% match, {result.resultLabel.replace('_', ' ')})"
                + (f": {reasons}" if reasons else "")
            )

        if recommendation.results[0].explanation.tradeOffs:
            lines.append("Trade-offs: " + "; ".join(recommendation.results[0].explanation.tradeOffs[:2]))

        return "\n".join(lines)

    def recommendation_workflow(self, query: str, limit: int = 4) -> RecommendationWorkflowResponse:
        intent = self._parse_intent(query)
        return self._build_recommendation_workflow(intent, limit=max(1, limit))

    def compare_summary(self, first_product_id: str, second_product_id: str) -> ComparisonSummaryResponse:
        first = self.repository.get_by_slug(first_product_id)
        second = self.repository.get_by_slug(second_product_id)

        if not first:
            raise NotFoundError(f"Product '{first_product_id}' not found")
        if not second:
            raise NotFoundError(f"Product '{second_product_id}' not found")

        first_score = self._compare_score(first)
        second_score = self._compare_score(second)
        winner = first if first_score >= second_score else second
        loser = second if winner.id == first.id else first

        key_advantages = self._comparison_advantages(winner, loser)
        trade_offs = self._comparison_tradeoffs(first, second)

        draft = (
            f"{winner.name} is the better overall pick for most buyers based on rating, AI score, and practical"
            f" value. {loser.name} remains attractive for buyers prioritizing specific strengths listed below."
        )
        summary = self.provider.generate(
            GenerationRequest(
                systemPrompt=ASSISTANT_SYSTEM_PROMPT,
                userPrompt=COMPARE_SUMMARY_PROMPT,
                variables={"draft": draft},
            )
        ).text

        return ComparisonSummaryResponse(
            winnerProductId=winner.slug,
            summary=summary,
            keyAdvantages=key_advantages,
            tradeOffs=trade_offs,
        )

    def review_summary(self, product_id: str) -> ReviewSummaryResponse:
        product = self.repository.get_by_slug(product_id)
        if not product:
            raise NotFoundError(f"Product '{product_id}' not found")

        positive_candidates = [item.value for item in sorted(product.pros, key=lambda x: x.position)][:3]
        negative_candidates = [item.value for item in sorted(product.cons, key=lambda x: x.position)][:3]

        for review in sorted(product.reviews, key=lambda x: x.rating, reverse=True):
            if len(positive_candidates) >= 4:
                break
            if review.rating >= Decimal("4.0"):
                positive_candidates.append(review.title)

        for review in sorted(product.reviews, key=lambda x: x.rating):
            if len(negative_candidates) >= 4:
                break
            if review.rating <= Decimal("3.5"):
                negative_candidates.append(review.title)

        positives = self._unique_preserve_order(positive_candidates)[:4]
        negatives = self._unique_preserve_order(negative_candidates)[:4]

        buying_advice = self._review_advice(product)
        verdict_draft = (
            f"{product.name} is a {'strong' if product.ai_score >= 85 else 'situational'} buy. "
            f"Prioritize it if the positives match your daily usage and the trade-offs are acceptable."
        )
        final_verdict = self.provider.generate(
            GenerationRequest(
                systemPrompt=ASSISTANT_SYSTEM_PROMPT,
                userPrompt=REVIEW_SUMMARY_PROMPT,
                variables={"draft": verdict_draft},
            )
        ).text

        return ReviewSummaryResponse(
            positives=positives,
            negatives=negatives,
            buyingAdvice=buying_advice,
            finalVerdict=final_verdict,
        )

    def buying_guide(self, product_id: str, alternatives_limit: int = 3) -> BuyingGuideResponse:
        product = self.repository.get_by_slug(product_id)
        if not product:
            raise NotFoundError(f"Product '{product_id}' not found")

        category_products = [
            item for item in self.repository.list_products() if item.category_id == product.category_id and item.id != product.id
        ]
        category_prices = [float(item.price_value) for item in category_products]
        category_median = median(category_prices) if category_prices else float(product.price_value)

        worth_buying = product.ai_score >= 84 and float(product.rating) >= 4.1
        value_signal = float(product.price_value) / max(1.0, category_median)

        if value_signal <= 0.9:
            value_msg = "priced below the category median while keeping strong quality signals"
        elif value_signal <= 1.1:
            value_msg = "priced near the category median with balanced value"
        else:
            value_msg = "priced above the category median, so it should be chosen for its strengths rather than budget"

        alternatives = sorted(
            category_products,
            key=lambda item: (self._compare_score(item), -abs(float(item.price_value) - float(product.price_value))),
            reverse=True,
        )[: max(1, alternatives_limit)]

        verdict_draft = (
            f"{'Worth buying' if worth_buying else 'Worth considering carefully'}: {product.name} is {value_msg}."
        )
        verdict = self.provider.generate(
            GenerationRequest(
                systemPrompt=ASSISTANT_SYSTEM_PROMPT,
                userPrompt=BUYING_GUIDE_PROMPT,
                variables={"draft": verdict_draft},
            )
        ).text

        return BuyingGuideResponse(
            worthBuying=worth_buying,
            verdict=verdict,
            bestFor=[item.value for item in sorted(product.best_for, key=lambda x: x.position)][:4],
            alternatives=[self._to_dto(item) for item in alternatives],
            priceValueAnalysis=(
                f"{product.name} is {value_msg}. Category median is about ₹{int(category_median):,} while this product is"
                f" ₹{int(product.price_value):,}."
            ),
        )

    def _build_recommendation_workflow(self, intent: ShoppingIntentDTO, limit: int) -> RecommendationWorkflowResponse:
        all_products = self.repository.list_products()

        filtered = [product for product in all_products if self._matches_intent(product, intent)]
        if not filtered:
            filtered = all_products

        ranked = sorted(
            filtered,
            key=lambda item: self._recommendation_score(item, intent),
            reverse=True,
        )[: max(1, limit)]

        ranked_dtos = [
            RankedRecommendationDTO(
                product=self._to_dto(product),
                score=round(self._recommendation_score(product, intent), 2),
                reasons=self._recommendation_reasons(product, intent),
            )
            for product in ranked
        ]

        explanation_draft = self._recommendation_explanation(intent, ranked)
        explanation = self.provider.generate(
            GenerationRequest(
                systemPrompt=ASSISTANT_SYSTEM_PROMPT,
                userPrompt=RECOMMENDATION_EXPLAINER_PROMPT,
                variables={"draft": explanation_draft},
            )
        ).text

        return RecommendationWorkflowResponse(
            intent=intent,
            explanation=explanation,
            rankedRecommendations=ranked_dtos,
            followUpQuestions=self._follow_up_questions(intent),
        )

    def _to_dto(self, product: Product) -> ProductDTO:
        similar = self.repository.get_similar_slugs(product.id)
        return to_product_dto(product, similar_slugs=similar)

    def _matches_intent(self, product: Product, intent: ShoppingIntentDTO) -> bool:
        if intent.category and product.category.slug != intent.category:
            return False

        price_value = float(product.price_value)
        if intent.budgetMin is not None and price_value < intent.budgetMin * 0.8:
            return False
        if intent.budgetMax is not None and price_value > intent.budgetMax * 1.15:
            return False

        return True

    def _recommendation_score(self, product: Product, intent: ShoppingIntentDTO) -> float:
        score = float(product.ai_score) * 0.65 + float(product.rating) * 8.0

        product_blob = " ".join(
            [
                product.name.lower(),
                product.description.lower(),
                product.brand.name.lower(),
                product.category.slug.lower(),
                " ".join(feature.value.lower() for feature in product.features),
                " ".join(tag.value.lower() for tag in product.tags),
            ]
        )

        if intent.usage and intent.usage in product_blob:
            score += 11
        if intent.category and intent.category == product.category.slug:
            score += 8

        if intent.budgetMax is not None:
            budget_gap = max(0.0, float(intent.budgetMax) - float(product.price_value))
            score += min(8.0, budget_gap / 5000.0)

        for priority in intent.priorities:
            if priority in product_blob:
                score += 4

        return score

    def _recommendation_reasons(self, product: Product, intent: ShoppingIntentDTO) -> list[str]:
        reasons = [f"AI score {product.ai_score}/100 and rating {float(product.rating):.1f}/5"]

        if intent.budgetMax is not None and float(product.price_value) <= intent.budgetMax:
            reasons.append(f"Within your budget at about ₹{int(product.price_value):,}")

        if intent.usage:
            usage_text = intent.usage.replace("-", " ")
            reasons.append(f"Good fit for {usage_text} based on features and tags")

        if intent.category:
            reasons.append(f"Direct match for requested category: {intent.category}")

        if product.features:
            reasons.append(f"Notable feature: {product.features[0].value}")

        return reasons[:4]

    def _recommendation_explanation(self, intent: ShoppingIntentDTO, ranked: list[Product]) -> str:
        if not ranked:
            return "I could not find a strong product match. Share a budget, category, or use-case for better picks."

        top = ranked[0]
        intent_bits: list[str] = []
        if intent.category:
            intent_bits.append(intent.category)
        if intent.usage:
            intent_bits.append(intent.usage)
        if intent.budgetMax is not None:
            intent_bits.append(f"budget up to ₹{intent.budgetMax:,}")

        focus = ", ".join(intent_bits) if intent_bits else "overall value"
        return (
            f"I prioritized {focus} and ranked products by AI score, user rating, and price fit. "
            f"{top.name} leads due to stronger overall quality and practical value for your request."
        )

    def _follow_up_questions(self, intent: ShoppingIntentDTO) -> list[str]:
        questions: list[str] = []

        if intent.budgetMax is None:
            questions.append("What is your max budget?")
        if intent.category is None:
            questions.append("Which product category should I focus on?")
        if intent.usage is None:
            questions.append("What is your primary use-case?")

        questions.extend(
            [
                "Do you care more about performance or battery life?",
                "Should I prioritize value for money or premium features?",
            ]
        )

        return self._unique_preserve_order(questions)[:4]

    def _comparison_advantages(self, winner: Product, loser: Product) -> list[str]:
        advantages: list[str] = []

        if winner.ai_score > loser.ai_score:
            advantages.append(f"Higher AI score ({winner.ai_score} vs {loser.ai_score})")
        if winner.rating > loser.rating:
            advantages.append(f"Better user rating ({float(winner.rating):.1f} vs {float(loser.rating):.1f})")
        if winner.price_value < loser.price_value:
            advantages.append("Lower price for a better overall quality-to-cost balance")
        if winner.features:
            advantages.append(f"Practical strength: {winner.features[0].value}")

        return self._unique_preserve_order(advantages)[:4]

    def _comparison_tradeoffs(self, first: Product, second: Product) -> list[str]:
        tradeoffs: list[str] = []

        if first.price_value != second.price_value:
            cheaper = first if first.price_value < second.price_value else second
            pricier = second if cheaper.id == first.id else first
            tradeoffs.append(
                f"{cheaper.name} is cheaper, while {pricier.name} asks a premium for additional strengths"
            )

        if first.rating != second.rating:
            higher = first if first.rating >= second.rating else second
            tradeoffs.append(f"{higher.name} has stronger customer sentiment")

        if first.ai_score != second.ai_score:
            higher_ai = first if first.ai_score >= second.ai_score else second
            tradeoffs.append(f"{higher_ai.name} ranks higher in AI fit scoring")

        return self._unique_preserve_order(tradeoffs)[:4]

    def _review_advice(self, product: Product) -> str:
        if product.rating >= Decimal("4.5") and product.ai_score >= 90:
            return "Strong buy for most users in this category, especially if it matches your feature priorities."
        if product.rating >= Decimal("4.0") and product.ai_score >= 82:
            return "Good buy if the listed strengths match your primary use-case and the price fits your budget."
        return "Consider only if the product's niche strengths matter to you more than broad value-for-money options."

    def _parse_intent(self, message: str) -> ShoppingIntentDTO:
        text = message.lower().strip()

        budget_min, budget_max = self._extract_budget(text)
        category = self._extract_label(text, CATEGORY_HINTS)
        usage = self._extract_label(text, USAGE_HINTS)
        priorities = self._extract_priorities(text)

        return ShoppingIntentDTO(
            budgetMin=budget_min,
            budgetMax=budget_max,
            category=category,
            usage=usage,
            priorities=priorities,
        )

    def _merge_intent(self, latest: ShoppingIntentDTO, previous: ShoppingIntentDTO | None) -> ShoppingIntentDTO:
        if previous is None:
            return latest

        return ShoppingIntentDTO(
            budgetMin=latest.budgetMin if latest.budgetMin is not None else previous.budgetMin,
            budgetMax=latest.budgetMax if latest.budgetMax is not None else previous.budgetMax,
            usage=latest.usage or previous.usage,
            category=latest.category or previous.category,
            priorities=self._unique_preserve_order(previous.priorities + latest.priorities),
        )

    def _build_assistant_reply(self, user_message: str, workflow: RecommendationWorkflowResponse) -> str:
        if self._is_greeting(user_message):
            return (
                "Hi! I can help you discover the best products based on budget, use-case, and category. "
                "Tell me what you are shopping for, and I will shortlist the top options."
            )

        top = workflow.rankedRecommendations[0] if workflow.rankedRecommendations else None
        if not top:
            return "I need a little more detail to make a useful recommendation."

        if self._is_compare_query(user_message) and len(workflow.rankedRecommendations) >= 2:
            first = workflow.rankedRecommendations[0].product
            second = workflow.rankedRecommendations[1].product
            winner_name = first.name if first.aiScore >= second.aiScore else second.name
            return (
                f"For this comparison, {winner_name} is currently the stronger overall pick based on fit score, "
                "rating, and value. Share your budget to get a tighter recommendation."
            )

        lowered = user_message.lower()
        if "iphone" in lowered and "samsung" in lowered:
            return (
                "iPhone usually leads in long-term software consistency, while Samsung often offers stronger "
                "display value and model variety at similar prices. Tell me your budget and priorities, and I will "
                "pick the better fit."
            )

        follow_up = workflow.followUpQuestions[0] if workflow.followUpQuestions else "Would you like a side-by-side comparison?"

        return (
            f"For '{user_message}', my top pick is {top.product.name}. "
            f"It ranks high on quality and value based on your intent. {follow_up}"
        )

    @staticmethod
    def _build_general_knowledge_reply(user_message: str) -> str:
        lowered = user_message.lower().strip()
        if "generative ai" in lowered:
            return (
                "Generative AI is a class of AI systems that learn patterns from data and generate new content, "
                "such as text, images, audio, video, or code. It is useful for drafting and ideation, but outputs "
                "should still be reviewed for accuracy and bias."
            )

        return (
            "I can explain AI concepts and best practices directly. If you also want recommendations, share your "
            "use case, budget, and preferred platforms."
        )

    @staticmethod
    def _is_greeting(message: str) -> bool:
        cleaned = message.lower().strip()
        return cleaned in GREETING_WORDS

    @staticmethod
    def _is_compare_query(message: str) -> bool:
        cleaned = message.lower()
        return "compare" in cleaned or " vs " in cleaned or " versus " in cleaned

    @staticmethod
    def _is_general_knowledge_query(message: str) -> bool:
        lowered = message.lower().strip()
        if not lowered:
            return False

        question_like = lowered.endswith("?") or lowered.startswith(("what is", "what are", "explain", "define", "how does"))
        if not question_like:
            return False

        recommendation_signals = (
            "recommend",
            "best",
            "budget",
            "under",
            "buy",
            "compare",
            "vs",
            "tool",
            "software",
            "phone",
            "laptop",
            "headphone",
            "smartwatch",
            "television",
            "camera",
        )
        return not any(signal in lowered for signal in recommendation_signals)

    @staticmethod
    def _extract_budget(text: str) -> tuple[int | None, int | None]:
        normalized = text.replace(",", "")

        between_match = re.search(r"between\s*₹?\s*(\d+)\s*(?:and|to)\s*₹?\s*(\d+)", normalized)
        if between_match:
            low = int(between_match.group(1))
            high = int(between_match.group(2))
            return (min(low, high), max(low, high))

        under_match = re.search(r"(?:under|below|upto|up to|max)\s*₹?\s*(\d+)", normalized)
        if under_match:
            high = int(under_match.group(1))
            return (None, high)

        above_match = re.search(r"(?:above|over|from)\s*₹?\s*(\d+)", normalized)
        if above_match:
            low = int(above_match.group(1))
            return (low, None)

        bare_numbers = [int(match) for match in re.findall(r"₹\s*(\d{4,6})", normalized)]
        if len(bare_numbers) == 1:
            return (None, bare_numbers[0])
        if len(bare_numbers) >= 2:
            low, high = sorted(bare_numbers[:2])
            return (low, high)

        return (None, None)

    @staticmethod
    def _extract_label(text: str, hints: dict[str, set[str]]) -> str | None:
        for label, words in hints.items():
            if any(word in text for word in words):
                return label
        return None

    def _extract_priorities(self, text: str) -> list[str]:
        priorities = [label for label, words in PRIORITY_HINTS.items() if any(word in text for word in words)]
        return self._unique_preserve_order(priorities)

    @staticmethod
    def _unique_preserve_order(values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            normalized = value.strip()
            if not normalized:
                continue
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            result.append(normalized)
        return result

    @staticmethod
    def _compare_score(product: Product) -> float:
        return float(product.ai_score) * 0.7 + float(product.rating) * 8.0 - float(product.price_value) / 120000.0
