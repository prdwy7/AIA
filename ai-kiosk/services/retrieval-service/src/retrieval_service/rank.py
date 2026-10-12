"""Evidence ranking: authority + freshness + relevance (docs/02 S8).

Every returned evidence item carries method + score + authority level.
The composite score blends:
- relevance (fused retrieval score, 0..1),
- authority (source authority level 1..7, normalized),
- freshness (effective-date decay; retired/superseded passages are excluded
  upstream by the validity filter).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

# Default weights (tunable per risk tier in production).
W_RELEVANCE = 0.5
W_AUTHORITY = 0.3
W_FRESHNESS = 0.2

# Freshness: full credit within this many days of `now`, linear decay to 0
# at this many days. Freshness is a *soft* signal — hard expiry (retired /
# superseded knowledge) is enforced by the validity filter (effective_to),
# so the decay horizon spans the long tail of still-relevant agronomy.
FRESH_FULL_DAYS = 365
FRESH_ZERO_DAYS = 5475  # 15 years (retention horizon)


@dataclass(frozen=True)
class Passage:
    """A retrieval unit (kb_passages row)."""

    passage_id: str
    entry_id: str
    text_te: str
    text_en: str | None = None
    crop: str | None = None
    stage: str | None = None
    region: str | None = None
    authority_level: int = 3  # 1..7
    effective_from: date | None = None
    effective_to: date | None = None
    embedding: list[float] | None = None
    kb_version: str = "1.0.0"


@dataclass(frozen=True)
class ScoredPassage:
    """A ranked result — always carries method + score + authority."""

    passage: Passage
    method: str  # "sql" | "keyword" | "vector" | "hybrid"
    score: float  # composite 0..1
    rank: int  # 1-based
    relevance: float
    authority: float
    freshness: float


def authority_score(level: int) -> float:
    """Normalize authority level 1..7 to 0..1."""
    return max(0.0, min(1.0, (level - 1) / 6.0))


def freshness_score(effective_from: date | None, now: date) -> float:
    """Full credit for recent knowledge, linear decay over the retention horizon."""
    if effective_from is None:
        return 0.5  # unknown age → neutral
    age_days = (now - effective_from).days
    if age_days <= 0:
        return 1.0
    if age_days >= FRESH_ZERO_DAYS:
        return 0.0
    if age_days <= FRESH_FULL_DAYS:
        return 1.0
    span = FRESH_ZERO_DAYS - FRESH_FULL_DAYS
    return 1.0 - (age_days - FRESH_FULL_DAYS) / span


def composite_score(relevance: float, authority: float, freshness: float) -> float:
    return W_RELEVANCE * relevance + W_AUTHORITY * authority + W_FRESHNESS * freshness


def rank_passages(
    candidates: list[tuple[Passage, str, float]],
    now: date,
    top_k: int = 10,
) -> list[ScoredPassage]:
    """Apply the composite score and return the top-k, 1-based ranked.

    `candidates` is a list of (passage, method, fused_relevance).
    """
    scored: list[ScoredPassage] = []
    for passage, method, relevance in candidates:
        auth = authority_score(passage.authority_level)
        fresh = freshness_score(passage.effective_from, now)
        scored.append(
            ScoredPassage(
                passage=passage,
                method=method,
                score=composite_score(relevance, auth, fresh),
                rank=0,
                relevance=relevance,
                authority=auth,
                freshness=fresh,
            )
        )
    scored.sort(key=lambda s: s.score, reverse=True)
    for i, item in enumerate(scored[:top_k], start=1):
        scored[i - 1] = ScoredPassage(
            passage=item.passage,
            method=item.method,
            score=item.score,
            rank=i,
            relevance=item.relevance,
            authority=item.authority,
            freshness=item.freshness,
        )
    return scored[:top_k]
