# input-orchestrator (S4)

> **Skeleton service** — built in Phase 1.. Full spec: `docs/02-modules.md` §S4
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

single entry point for all inputs across all modalities and channels.

## Responsibilities

routes audio → speech-service, images → image-service, text → text normalizer, touch events → case-service directly. Owns session state. Enforces input quality gates. Creates immutable `Input` nodes and triggers interpretation. Enforces do-not-repeat memory at input time (e.g., already-received image views).

## Tech

Python/FastAPI; session state in Redis (central) / local Redis (edge); Pydantic v2 schemas.

## Interfaces

S5, S6, S7, channel adapters (inbound), lexicon (shared library).

## Dependencies

S5, S6, S7, Redis, `canonical-schema`, `agri-rules` (lexicon).

## Scaling

stateless compute; horizontal replicas behind the API gateway; session state externalized.

## Built in

Phase 1.

## Key invariants

every input becomes an immutable `Input` node with modality metadata; mixed input within one case is always allowed; modality failure never dead-ends the case.

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/input-orchestrator/
├── pyproject.toml
├── README.md
├── src/input_orchestrator/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_input_orchestrator.py
```
