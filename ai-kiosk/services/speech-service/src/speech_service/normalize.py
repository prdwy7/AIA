"""Agricultural vocabulary normalization (lexicon pass, docs/05 §2).

Maps local/dialectal terms to canonical forms using the `lexicon` table
(migration 0003). The lexicon is part of `SPEECH_VERSION` and is released
through the same pipeline as models and KB.

This pass runs on ASR transcripts and text inputs before entity extraction,
so a farmer's local word ("పసపు" for cotton) resolves to the canonical crop
term regardless of modality.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class LexiconEntry:
    """A local term → canonical mapping."""

    term: str
    normalized: str
    category: str = "general"  # crop | pest | disease | product | dose | location | stage | general
    crop: str | None = None
    region: str | None = None


@dataclass(frozen=True)
class AppliedMapping:
    term: str
    normalized: str
    category: str
    count: int


@dataclass(frozen=True)
class NormalizedText:
    """Result of the lexicon pass."""

    original: str
    normalized: str
    applied: list[AppliedMapping] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.applied)


class LexiconNormalizer:
    """Deterministic term → canonical replacement (case-insensitive)."""

    def __init__(self, entries: list[LexiconEntry]) -> None:
        # Longest terms first so multi-word terms win over their substrings.
        self._entries = sorted(entries, key=lambda e: len(e.term), reverse=True)
        self._patterns: list[tuple[re.Pattern[str], LexiconEntry]] = []
        for entry in self._entries:
            pattern = re.compile(
                r"(?<![0-9A-Za-z\u0C00-\u0C7F])"
                + re.escape(entry.term)
                + r"(?![0-9A-Za-z\u0C00-\u0C7F])",
                re.IGNORECASE,
            )
            self._patterns.append((pattern, entry))

    def normalize(self, text: str) -> NormalizedText:
        result = text
        applied: dict[str, AppliedMapping] = {}
        for pattern, entry in self._patterns:
            matches = pattern.findall(result)
            if matches:
                result = pattern.sub(entry.normalized, result)
                applied[entry.term] = AppliedMapping(
                    term=entry.term,
                    normalized=entry.normalized,
                    category=entry.category,
                    count=len(matches),
                )
        return NormalizedText(
            original=text,
            normalized=result,
            applied=list(applied.values()),
        )
