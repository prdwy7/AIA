# advisory-service (S11)

> **Skeleton service** — built in WS-AI (W2) → Phase 6 (verification engine).. Full spec: `docs/02-modules.md` §S11
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

composes the grounded answer.

## Responsibilities

retrieval evidence + rules evaluation + LLM draft → advisory/prescription draft with evidence-ID retention end-to-end; risk-tier assignment (information/diagnosis/advisory/prescription); verification-gate orchestration (Phase 6); confirmation-gate decisions (θ_confirm = 0.80, θ_auto = 0.85).

## Tech

Python/FastAPI; Pydantic v2 decision schemas (roadmap §6.1.1 `decision` payload).

## Interfaces

S8, S9, S10, S7, S12, S13.

## Dependencies

`canonical-schema`, S8/S9/S10.

## Scaling

stateless; CPU-bound orchestration (GPU work delegated to S10/S6).

## Built in

WS-AI (W2) → Phase 6 (verification engine).

## Key invariants

evidence IDs retained end-to-end on every high-risk output; an apparently obvious solution still passes its risk tier's verification gates; gate outcomes recorded on the decision node (`rules_evaluated[]`).

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/advisory-service/
├── pyproject.toml
├── README.md
├── src/advisory_service/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_advisory_service.py
```
