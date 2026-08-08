from __future__ import annotations

import re
from decimal import Decimal

from app.schemas.ai_tool import (
    AIToolRecommendationBudget,
    AIToolRecommendationIntent,
    AIToolRecommendationPricingPreference,
    AIToolRecommendationRequest,
)


AI_TOOL_HINTS = {
    "ai tool",
    "ai tools",
    "chatgpt",
    "claude",
    "grammarly",
    "midjourney",
    "runway",
    "copilot",
    "youtube",
    "blog",
    "coding",
    "coding tool",
    "writing tool",
    "image generator",
    "video generator",
    "voice generator",
}

CATEGORY_HINTS: dict[str, set[str]] = {
    "ai-assistants": {"assistant", "chatgpt", "claude", "ai chat", "q&a"},
    "ai-writing": {"writing", "blog", "copy", "grammar", "content writing", "blogging"},
    "ai-image-design": {"image", "design", "visual", "image generator", "midjourney", "canva"},
    "ai-video-audio": {"video", "youtube", "audio", "voice", "text-to-video", "video generation", "runway", "elevenlabs"},
    "ai-coding-developer-tools": {"coding", "developer", "programming", "code completion", "github", "copilot", "cursor"},
}

EXPERIENCE_HINTS: dict[str, set[str]] = {
    "beginner": {"beginner", "new", "starter", "easy"},
    "intermediate": {"intermediate"},
    "advanced": {"advanced", "expert", "power user"},
    "team": {"team", "company", "business", "startup"},
}

PRICING_HINTS: dict[str, set[str]] = {
    "free": {"free", "no cost"},
    "free_trial": {"trial", "free trial"},
    "monthly": {"monthly", "per month"},
    "yearly": {"yearly", "annual", "per year"},
}

FREE_ONLY_PATTERNS: tuple[str, ...] = (
    r"\bcompletely free\b",
    r"\bfree only\b",
    r"\bonly free\b",
    r"\bno paid plans?\b",
    r"\bwithout paid plans?\b",
)

PREFER_FREE_PATTERNS: tuple[str, ...] = (
    r"\bprefer(?: a)? free\b",
    r"\bfree is better\b",
    r"\bfree.*paid (?:is )?okay\b",
    r"\bpaid (?:is )?okay.*free\b",
)

PAID_ALLOWED_PATTERNS: tuple[str, ...] = (
    r"\bpaid (?:is )?okay\b",
    r"\bpaid allowed\b",
)

ANY_PRICING_PATTERNS: tuple[str, ...] = (
    r"\bany price\b",
    r"\bany pricing\b",
    r"\bno budget\b",
)


class AIToolIntentRouter:
    def is_ai_tool_request(self, message: str) -> bool:
        lowered = message.lower()
        if any(term in lowered for term in AI_TOOL_HINTS):
            return True

        return bool(re.search(r"\b(ai|tool|software|compare)\b", lowered)) and bool(
            re.search(r"\b(write|video|audio|image|design|coding|blog|youtube|assistant|compare)\b", lowered)
        )

    def build_request(self, query: str, limit: int = 5) -> AIToolRecommendationRequest:
        normalized = query.strip()
        lowered = normalized.lower()

        category = self._extract_category(lowered)
        experience_level = self._extract_experience(lowered)
        pricing_preference = self._extract_pricing_preference(lowered)
        budget = self._extract_budget(normalized)

        use_cases = self._extract_list(lowered, {
            "youtube": "youtube videos",
            "video": "video generation",
            "videos": "video generation",
            "blog": "blogging",
            "content": "content creation",
            "research": "research",
            "coding": "coding",
            "marketing": "marketing",
            "editing": "editing",
            "voice": "voice generation",
            "video generation": "video generation",
            "image generation": "image generation",
            "image generator": "image generation",
            "design": "design",
        })
        required_features = self._extract_list(lowered, {
            "grammar": "grammar",
            "templates": "templates",
            "api": "api",
            "collaboration": "collaboration",
            "long context": "long context",
            "video editing": "video editing",
            "text-to-video": "text-to-video",
            "voice cloning": "voice cloning",
            "code completion": "code completion",
            "ai chat": "ai chat",
            "image generation": "image generation",
        })
        platforms = self._extract_list(lowered, {
            "web": "web",
            "windows": "windows",
            "mac": "mac",
            "macos": "mac",
            "ios": "ios",
            "android": "android",
            "desktop": "desktop",
            "browser": "browser extension",
        })
        integrations = self._extract_list(lowered, {
            "github": "github",
            "slack": "slack",
            "google workspace": "google workspace",
            "adobe": "adobe",
            "google docs": "google docs",
            "office": "microsoft office",
            "api": "api",
            "drive": "google drive",
            "dropbox": "dropbox",
        })

        constraints: list[str] = []
        if "must" in lowered:
            constraints.append("strict_requirements")
        if "only" in lowered:
            constraints.append("strict_filtering")

        intent = AIToolRecommendationIntent(
            category=category,
            useCases=use_cases,
            requiredFeatures=required_features,
            platforms=platforms,
            integrations=integrations,
            budget=budget,
            pricingPreference=pricing_preference,
            experienceLevel=experience_level,
            constraints=constraints,
        )

        return AIToolRecommendationRequest(
            query=normalized,
            intent=intent,
            limit=max(1, min(20, limit)),
        )

    def _extract_category(self, lowered: str) -> str | None:
        best_category: str | None = None
        best_score = 0
        for category, hints in CATEGORY_HINTS.items():
            score = sum(1 for hint in hints if hint in lowered)
            if score > best_score:
                best_score = score
                best_category = category
        return best_category if best_score > 0 else None

    def _extract_experience(self, lowered: str) -> str | None:
        for label, hints in EXPERIENCE_HINTS.items():
            if any(hint in lowered for hint in hints):
                return label
        return None

    def _extract_pricing_preference(self, lowered: str) -> AIToolRecommendationPricingPreference | None:
        if any(re.search(pattern, lowered) for pattern in FREE_ONLY_PATTERNS):
            return AIToolRecommendationPricingPreference(model="free_only", preferFreePlan=True)

        if any(re.search(pattern, lowered) for pattern in PREFER_FREE_PATTERNS):
            return AIToolRecommendationPricingPreference(model="prefer_free", preferFreePlan=True)

        if any(re.search(pattern, lowered) for pattern in PAID_ALLOWED_PATTERNS):
            return AIToolRecommendationPricingPreference(model="paid_allowed")

        if any(re.search(pattern, lowered) for pattern in ANY_PRICING_PATTERNS):
            return AIToolRecommendationPricingPreference(model="any")

        model: str | None = None
        for key, hints in PRICING_HINTS.items():
            if any(hint in lowered for hint in hints):
                model = key
                break

        prefer_free_plan = True if "free" in lowered else None
        prefer_free_trial = True if "trial" in lowered else None

        if model is None and prefer_free_plan is None and prefer_free_trial is None:
            return None

        return AIToolRecommendationPricingPreference(
            model=model,
            preferFreePlan=prefer_free_plan,
            preferFreeTrial=prefer_free_trial,
        )

    def _extract_budget(self, text: str) -> AIToolRecommendationBudget | None:
        normalized = text.lower().replace(",", "")
        normalized = normalized.replace("₹", "inr ")

        currency = "USD" if "$" in text else "INR"

        if re.search(r"\b(?:₹?\s*0\s*budget|budget\s*0|\$\s*0\b)\b", normalized):
            return AIToolRecommendationBudget(currency=currency, max=Decimal("0"), pricingPeriod="monthly")

        budget_max_match = re.search(r"(?:under|below|upto|up to|max)\D*(\d+(?:\.\d+)?)", normalized)
        budget_min_match = re.search(r"(?:above|over|from|min)\D*(\d+(?:\.\d+)?)", normalized)

        inline_amount_match = re.search(r"(?:inr|\$|₹|\?)\s*(\d+(?:\.\d+)?)\s*/?\s*(?:month|mo)\b", normalized)
        if inline_amount_match and not budget_max_match:
            budget_max_match = inline_amount_match

        budget_max: Decimal | None = Decimal(budget_max_match.group(1)) if budget_max_match else None
        budget_min: Decimal | None = Decimal(budget_min_match.group(1)) if budget_min_match else None

        if budget_min is None and budget_max is None:
            return None

        return AIToolRecommendationBudget(
            currency=currency,
            min=budget_min,
            max=budget_max,
            pricingPeriod="monthly" if ("month" in normalized or "mo" in normalized) else None,
        )

    @staticmethod
    def _extract_list(lowered: str, catalog: dict[str, str]) -> list[str]:
        values: list[str] = []
        for hint, canonical in catalog.items():
            if hint in lowered:
                values.append(canonical)
        seen: set[str] = set()
        deduped: list[str] = []
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            deduped.append(value)
        return deduped
