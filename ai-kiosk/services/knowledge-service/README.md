# knowledge-service (S18)

> **Skeleton service** — built in WS-KB (W1–W2: KB v1 for Kurnool crops); versioning/bundles in Phase 11/14.. Full spec: `docs/02-modules.md` §S18
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

governed knowledge.

## Responsibilities

KB lifecycle: ingestion (PDFs/manuals → structured records + passages via pypdf/unstructured/marker), normalization, expert review workflow, versioning (KB N+1 with effective dates + supersession links), test cases per entry, edge bundle publishing (signed), evidence ledger management, re-index/re-embed worker, retirement/monitoring (age, unanswered questions, retrieval recall).

## Tech

Python; ingestion workers; MinIO (bundles); pgvector re-index; minisign signatures.

## Interfaces

S22 (review UI), S8 (index), S19 (bundles), S14 (candidates), evidence ledger.

## Dependencies

MinIO, pgvector, `kb_entries`/`kb_passages` tables.

## Scaling

batch workers; KB size at pilot ~10⁴–10⁵ passages.

## Built in

WS-KB (W1–W2: KB v1 for Kurnool crops); versioning/bundles in Phase 11/14.

## Key invariants

source authority hierarchy (roadmap §4.6.1) enforced at ingestion; every KB entry ships with test questions; KB entries carry effective dates and supersession links; retired entries archived, not deleted.

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/knowledge-service/
├── pyproject.toml
├── README.md
├── src/knowledge_service/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_knowledge_service.py
```
