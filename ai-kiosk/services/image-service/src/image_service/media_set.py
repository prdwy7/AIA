"""Media-set management: views per case + missing-view requests.

A complete diagnostic media set has these views:

    whole_plant | leaf | stem | fruit | pest_closeup | field_context

Invariant: **already-received views are never re-requested** (do-not-repeat
memory). Missing-view requests are concrete and bounded.
"""

from __future__ import annotations

from dataclasses import dataclass, field

ALL_VIEWS = ("whole_plant", "leaf", "stem", "fruit", "pest_closeup", "field_context")

# Views that are always useful for a first photo set (subset of ALL_VIEWS).
DEFAULT_REQUESTED_VIEWS = ("whole_plant", "leaf", "pest_closeup")

_VIEW_INSTRUCTIONS: dict[str, str] = {
    "whole_plant": "మొక్క పూర్తీ ఫోటో (whole plant, from 1–2 m)",
    "leaf": "ప్రభావితమైన పత్రం క్లారీ ఫోటో (close-up of the affected leaf)",
    "stem": "కాండం ఫోటో (stem close-up)",
    "fruit": "పండు/పొట్టు ఫోటో (fruit/boll close-up)",
    "pest_closeup": "పురుగు క్లారీ ఫోటో (insect close-up, if visible)",
    "field_context": "పొలం పరిసరాల ఫోటో (field context)",
}


@dataclass
class MediaSet:
    """The media set for one case (which views are already received)."""

    case_id: str
    received: dict[str, str] = field(default_factory=dict)  # view -> media_id

    def record(self, view: str, media_id: str) -> None:
        if view not in ALL_VIEWS:
            raise ValueError(f"unknown view: {view}")
        self.received[view] = media_id

    def has(self, view: str) -> bool:
        return view in self.received

    def missing(self, requested: tuple[str, ...] = DEFAULT_REQUESTED_VIEWS) -> list[str]:
        """Views that are requested but not yet received.

        Never returns a view that is already received (do-not-repeat).
        """
        return [v for v in requested if v not in self.received]

    def complete(self, requested: tuple[str, ...] = DEFAULT_REQUESTED_VIEWS) -> bool:
        return not self.missing(requested)

    def instructions(self, requested: tuple[str, ...] = DEFAULT_REQUESTED_VIEWS) -> list[str]:
        """Concrete, bilingual instructions for the missing views only."""
        return [_VIEW_INSTRUCTIONS[v] for v in self.missing(requested) if v in _VIEW_INSTRUCTIONS]


class MediaSetManager:
    """Tracks media sets across cases."""

    def __init__(self) -> None:
        self._sets: dict[str, MediaSet] = {}

    def get(self, case_id: str) -> MediaSet:
        if case_id not in self._sets:
            self._sets[case_id] = MediaSet(case_id=case_id)
        return self._sets[case_id]

    def record(self, case_id: str, view: str, media_id: str) -> MediaSet:
        media_set = self.get(case_id)
        media_set.record(view, media_id)
        return media_set
