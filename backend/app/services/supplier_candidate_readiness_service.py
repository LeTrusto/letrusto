from __future__ import annotations

from typing import Final, Literal

from app.core.exceptions import BadRequestError


CandidateReadinessStatus = Literal[
    "DISCOVERED", "VALIDATED", "ENRICHING", "ENRICHED", "REVIEW", "REJECTED"
]

_ALLOWED_TRANSITIONS: Final[dict[CandidateReadinessStatus, frozenset[CandidateReadinessStatus]]] = {
    "DISCOVERED": frozenset({"VALIDATED", "REVIEW", "REJECTED"}),
    "VALIDATED": frozenset({"ENRICHING"}),
    "ENRICHING": frozenset({"ENRICHED", "REVIEW", "REJECTED"}),
    "ENRICHED": frozenset({"REVIEW"}),
    "REVIEW": frozenset({"VALIDATED", "REJECTED"}),
    "REJECTED": frozenset(),
}


class SupplierCandidateReadinessService:
    @staticmethod
    def transition(
        current: str, target: CandidateReadinessStatus
    ) -> CandidateReadinessStatus:
        if current not in _ALLOWED_TRANSITIONS:
            raise BadRequestError(f"Unknown supplier candidate readiness state: {current}")
        if target not in _ALLOWED_TRANSITIONS[current]:
            raise BadRequestError(
                f"Invalid supplier candidate readiness transition: {current} -> {target}"
            )
        return target

    @staticmethod
    def initial_state(target: CandidateReadinessStatus) -> CandidateReadinessStatus:
        return SupplierCandidateReadinessService.transition("DISCOVERED", target)

    @staticmethod
    def allowed_transitions() -> dict[str, tuple[str, ...]]:
        return {
            state: tuple(targets)
            for state, targets in _ALLOWED_TRANSITIONS.items()
        }
