from __future__ import annotations

from app.ai.providers.base import LLMProvider
from app.ai.providers.heuristic import HeuristicLLMProvider


def build_llm_provider(provider_name: str) -> LLMProvider:
    normalized = provider_name.strip().lower()
    if normalized in {"heuristic", "mock", "local"}:
        return HeuristicLLMProvider()

    # Keep non-configured providers safe while preserving plug-in architecture.
    return HeuristicLLMProvider()
