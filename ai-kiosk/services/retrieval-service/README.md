# retrieval-service (S8)

Hybrid evidence retrieval (roadmap §9.3).

## Purpose

- Structured filters first (crop / stage / geography / validity).
- Hybrid search: SQL/exact + keyword (Postgres FTS/BM25) + vector
  (pgvector, BGE-M3 dense + sparse).
- Reranking (BGE-Reranker-v2-M3, GPU) and evidence ranking by
  **authority + freshness + relevance**.
- Similar-case search (case embeddings) for S7 / Phase 7.

## Responsibilities

- `POST /v1/retrieval/search` — hybrid evidence retrieval with filters;
  returns ranked evidence with `method` + `score` + `authority_level`.
- Embedding generation (batch, KB re-index worker — not on the hot path).
- Similar-case index maintenance.

## Tech

- Python 3.12; PostgreSQL 17 + pgvector 0.8.2 (HNSW); BGE-M3 (edge +
  central); BGE-Reranker-v2-M3 (GPU).
- `sentence-transformers` is an **optional extra**; `HashEmbedder` is the
  deterministic dev/test fallback so the ranking logic is testable without a
  GPU.

## Interfaces

- Inbound: advisory-service (S11), case-service (S7).
- Outbound: knowledge-service (S18, index maintenance), similar-case index.

## Dependencies

- Models EMB-0.1.0 (BGE-M3) / RERANK-0.1.0 (BGE-Reranker-v2-M3), pgvector.
- `kb_entries` / `kb_passages` tables (migration 0003).

## Scaling

Single Postgres with HNSW is sufficient for the pilot (KB ~10⁴–10⁵
passages); read replica + index tuning at district scale. Embedding
generation is batch (KB re-index worker), not on the hot path.

## Built in

WS-AI (W2); consumed by Phases 3, 6, 7.

## Key invariants

- Every returned evidence item carries **method + score + authority level**.
- High-impact recommendations are traceable to evidence-ledger entries.
- Structured filters always run before ranking (no unfiltered vector blasts).

## Run

```bash
uv sync --all-packages
uv run uvicorn retrieval_service.app:app --reload
uv run pytest services/retrieval-service -q
```
