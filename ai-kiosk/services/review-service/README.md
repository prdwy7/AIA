# review-service (S13)

> **Skeleton service** — built in WS-PORTAL (W2, basic approve/correct/escalate) → Phase 8 (multimodal feedback, full snapshot).. Full spec: `docs/02-modules.md` §S13
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

the scientist gate.

## Responsibilities

scientist review queue: approve/correct/escalate; automatic full context snapshot (case, language, input, crop, problem, location, weather, soil, previous management, knowledge, rules, AI, scientist, output, audit); decision-delta creation; correction classification trigger; review SLA tracking (L2 ≤ 24 h; trial: same day).

## Tech

Python/FastAPI; snapshot builder (read-only aggregation over case graph); Pydantic v2 delta schemas.

## Interfaces

S7, S14, S16, S21 (scientist-portal), S2 (review notifications).

## Dependencies

`canonical-schema`, S7.

## Scaling

stateless; queue is Postgres-backed.

## Built in

WS-PORTAL (W2, basic approve/correct/escalate) → Phase 8 (multimodal feedback, full snapshot).

## Key invariants

scientist changes **only the wrong fields**; original AI decision is never overwritten; every correction carries an evidence status (EVIDENCE_BACKED / LOCALLY_VALIDATED / EXPERT_PREFERENCE).

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/review-service/
├── pyproject.toml
├── README.md
├── src/review_service/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_review_service.py
```
