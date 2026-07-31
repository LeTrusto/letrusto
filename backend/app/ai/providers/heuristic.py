from __future__ import annotations

from app.ai.providers.base import GenerationRequest, GenerationResult


class HeuristicLLMProvider:
    name = "heuristic"

    def generate(self, request: GenerationRequest) -> GenerationResult:
        draft = request.variables.get("draft")
        if isinstance(draft, str) and draft.strip():
            return GenerationResult(text=draft.strip(), provider=self.name)

        return GenerationResult(text=request.userPrompt.strip(), provider=self.name)
