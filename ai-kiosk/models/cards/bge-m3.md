# Card — BGE-M3 (EMB-0.1.0)

| Field | Value |
|---|---|
| Registry ID | `EMB-0.1.0` |
| Model | BGE-M3 (`BAAI/bge-m3`) |
| Class | Embedding |
| License | MIT |
| Deploy | Edge + Central |
| Purpose | KB + case embeddings (dense 1024-d + sparse lexical) |
| Source | https://huggingface.co/BAAI/bge-m3 |

## What it is

Multilingual dense+sparse embedding model — one model for the knowledge-base
passage index (pgvector HNSW, `kb_passages.embedding vector(1024)`) and for
similar-case search (case embeddings, `similar_case_index`).

## Runtime & usage

- Runtime: sentence-transformers (central) / ONNX int8 (edge, ~1.2 GB VRAM).
- Normalized embeddings (cosine = dot product).
- Dev/test fallback: `HashEmbedder` (deterministic bag-of-words hash, 1024-d)
  in retrieval-service so ranking logic is testable without the model.

## Benchmarks / gates

- KB retrieval set (≥ 200 questions with gold evidence, per crop): recall,
  NDCG.
- Similar-case golden pairs (≥ 100 curated pairs): NDCG@10, difference
  visibility.

## Invariants

- Embedding generation is batch (KB re-index worker), never on the hot path.
- Every retrieval result carries method + score + authority level
  (retrieval-service invariant).
