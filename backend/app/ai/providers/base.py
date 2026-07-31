from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class GenerationRequest:
    systemPrompt: str
    userPrompt: str
    variables: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class GenerationResult:
    text: str
    provider: str


class LLMProvider(Protocol):
    name: str

    def generate(self, request: GenerationRequest) -> GenerationResult:
        ...
