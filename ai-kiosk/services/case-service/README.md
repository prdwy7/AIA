# case-service (S7)

> **Skeleton service** — built in Phase 1 (schema + skeleton) → Phase 3 (full tree semantics).. Full spec: `docs/02-modules.md` §S7
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

owns the Case-to-Solution Tree — the canonical case service.

## Responsibilities

append-only `case_node` writes; lifecycle state machine (roadmap §4.2) with transition guards; contradiction detection (across modalities); do-not-repeat memory; case continuity (short code, QR payload, cross-channel mapping); tree retrieval.

## Tech

Python/FastAPI; PostgreSQL (system of record); ULID IDs; DB-level append-only enforcement (triggers reject UPDATE/DELETE except status transitions).

## Interfaces

all core services; channel adapters (via S4); S8 (case embeddings); S15/S16.

## Dependencies

`canonical-schema`, PostgreSQL, MinIO (media refs).

## Scaling

stateless API; Postgres partitioned by `case_id` range; read replicas at district scale. Hot path is small (node append + state transition).

## Built in

Phase 1 (schema + skeleton) → Phase 3 (full tree semantics).

## Key invariants

the ONLY service that mutates case state (append-only; status transitions only); original farmer input and original system interpretation are immutable; every question has a recorded decision purpose; a case never silently changes crop/stage/problem — contradictions force a clarification branch; max 3 questions per branch by default.

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/case-service/
├── pyproject.toml
├── README.md
├── src/case_service/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_case_service.py
```
