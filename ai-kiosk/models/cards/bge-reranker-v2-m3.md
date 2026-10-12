# Card — BGE-Reranker-v2-M3 (RERANK-0.1.0)

| Field | Value |
|---|---|
| Registry ID | `RERANK-0.1.0` |
| Model | BGE-Reranker-v2-M3 (`BAAI/bge-reranker-v2-m3`) |
| Class | Reranker |
| License | MIT |
| Deploy | Edge + Central (GPU, time-shared with LLM) |
| Purpose | Evidence reranking (cross-encoder over hybrid candidates) |
| Source | https://huggingface.co/BAAI/bge-reranker-v2-m3 |

## What it is

Cross-encoder reranker applied to the hybrid-retrieval candidate pool
(keyword + vector → RRF fusion → rerank → composite rank). ~1–2 GB VRAM,
batched, time-shared with the LLM via the GPU queue.

## Runtime & usage

- Runtime: sentence-transformers CrossEncoder (GPU) — batched, off the hot
  path when the LLM is drafting.
- Input: (query, passage) pairs from the retrieval candidate pool.
- Output: relevance scores feeding the composite rank
  (W: relevance 0.5, authority 0.3, freshness 0.2).

## Benchmarks / gates

- KB retrieval set: NDCG with vs without reranking (the reranker must earn
  its GPU time).

## Invariants

- Reranking never changes evidence provenance — method + score + authority
  level are still carried on every returned item.
