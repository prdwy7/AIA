"""Hybrid retrieval: structured filters → keyword + vector → fusion → rank.

Pipeline (docs/02 S8):
1. Structured filters (crop / stage / region / validity) — always first.
2. Keyword search (token overlap, BM25-ish in production Postgres FTS).
3. Vector search (cosine over BGE-M3 dense embeddings).
4. Reciprocal Rank Fusion of the keyword and vector rankings.
5. Composite ranking (authority + freshness + relevance) — see rank.py.

The in-memory store mirrors the `kb_passages` table (migration 0003); the
production store is Postgres + pgvector with the same query shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from retrieval_service.embed import Embedder, cosine
from retrieval_service.rank import Passage, ScoredPassage, rank_passages

RRF_K = 60  # standard reciprocal-rank-fusion constant


@dataclass(frozen=True)
class Filters:
    """Structured filters — applied before any ranking."""

    crop: str | None = None
    stage: str | None = None
    region: str | None = None
    only_valid: bool = True  # exclude retired/superseded (effective_to < now)


class PassageStore:
    """In-memory passage store (dev/test). Production: Postgres + pgvector."""

    def __init__(self, passages: list[Passage] | None = None) -> None:
        self._passages: list[Passage] = list(passages or [])

    def add(self, passage: Passage) -> None:
        self._passages.append(passage)

    def all(self) -> list[Passage]:
        return list(self._passages)


@dataclass
class HybridRetriever:
    """Filter → keyword + vector → RRF fusion → composite rank."""

    store: PassageStore
    embedder: Embedder
    rrf_k: int = RRF_K
    candidate_pool: int = 50  # per-method pool before fusion
    _extra: dict = field(default_factory=dict)

    # -- stage 1: filters --------------------------------------------------

    def _filtered(self, filters: Filters, now: date) -> list[Passage]:
        out = []
        for p in self.store.all():
            if filters.crop and p.crop != filters.crop:
                continue
            if filters.stage and p.stage != filters.stage:
                continue
            if filters.region and p.region != filters.region:
                continue
            if filters.only_valid and p.effective_to is not None and p.effective_to < now:
                continue
            out.append(p)
        return out

    # -- stage 2a: keyword -------------------------------------------------

    def _keyword_rank(self, query: str, candidates: list[Passage]) -> list[tuple[Passage, float]]:
        q_tokens = {t for t in query.lower().split() if t}
        scored: list[tuple[Passage, float]] = []
        for p in candidates:
            text = f"{p.text_te} {p.text_en or ''}".lower()
            p_tokens = {t for t in text.split() if t}
            if not p_tokens:
                continue
            overlap = len(q_tokens & p_tokens)
            if overlap == 0:
                continue
            # BM25-ish: overlap / sqrt(|passage|) — deterministic and simple.
            score = overlap / (len(p_tokens) ** 0.5)
            scored.append((p, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[: self.candidate_pool]

    # -- stage 2b: vector --------------------------------------------------

    def _vector_rank(self, query: str, candidates: list[Passage]) -> list[tuple[Passage, float]]:
        with_emb = [p for p in candidates if p.embedding]
        if not with_emb:
            return []
        q_vec = self.embedder.embed([query])[0]
        scored = [(p, cosine(q_vec, p.embedding or [])) for p in with_emb]
        scored = [(p, s) for p, s in scored if s > 0.0]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[: self.candidate_pool]

    # -- stage 3: fusion ---------------------------------------------------

    @staticmethod
    def _rrf_fuse(
        keyword: list[tuple[Passage, float]],
        vector: list[tuple[Passage, float]],
        k: int,
    ) -> list[tuple[Passage, str, float]]:
        """Reciprocal Rank Fusion. Returns (passage, method, fused_relevance).

        `method` records which signal(s) surfaced the passage:
        "keyword" | "vector" | "hybrid" (both).
        """
        fused: dict[str, tuple[Passage, float, set[str]]] = {}
        for rank, (p, _score) in enumerate(keyword, start=1):
            contrib = 1.0 / (k + rank)
            if p.passage_id in fused:
                passage, score, methods = fused[p.passage_id]
                fused[p.passage_id] = (passage, score + contrib, methods | {"keyword"})
            else:
                fused[p.passage_id] = (p, contrib, {"keyword"})
        for rank, (p, _score) in enumerate(vector, start=1):
            contrib = 1.0 / (k + rank)
            if p.passage_id in fused:
                passage, score, methods = fused[p.passage_id]
                fused[p.passage_id] = (passage, score + contrib, methods | {"vector"})
            else:
                fused[p.passage_id] = (p, contrib, {"vector"})
        results: list[tuple[Passage, str, float]] = []
        for passage, score, methods in fused.values():
            method = "hybrid" if len(methods) > 1 else next(iter(methods))
            results.append((passage, method, score))
        results.sort(key=lambda x: x[2], reverse=True)
        return results

    # -- full pipeline -----------------------------------------------------

    def search(
        self,
        query: str,
        filters: Filters | None = None,
        top_k: int = 10,
        now: date | None = None,
    ) -> list[ScoredPassage]:
        today = now or date.today()
        f = filters or Filters()
        candidates = self._filtered(f, today)
        keyword = self._keyword_rank(query, candidates)
        vector = self._vector_rank(query, candidates)
        fused = self._rrf_fuse(keyword, vector, self.rrf_k)
        # Normalize fused scores to 0..1 for the composite blend.
        max_score = fused[0][2] if fused else 1.0
        normalized = [
            (p, m, (s / max_score if max_score > 0 else 0.0)) for p, m, s in fused
        ]
        return rank_passages(normalized, today, top_k=top_k)
