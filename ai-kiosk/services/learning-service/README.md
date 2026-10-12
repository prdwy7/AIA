# learning-service (S14)

> **Skeleton service** — built in Phase 11.. Full spec: `docs/02-modules.md` §S14
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

governed learning.

## Responsibilities

correction classifier (10 delta types, roadmap §4.3.2); candidate generation per channel (knowledge/rule/training/language/case memory); provenance ledger (all 11 fields, §4.3.3); learning sandbox orchestration (data quality → regression → safety → counterexample → holdout); pattern discovery (group validated corrections by crop/stage/problem/region/season; min support N≥5, consistency ≥80%); candidate review workflow.

## Tech

Python; batch + event-driven (workers on Redis); MLflow/DVC integration for training candidates.

## Interfaces

S13, S15, S26, S18, S9, S22 (candidate queues).

## Dependencies

`canonical-schema`, S13 (deltas), S15 (outcomes), MLflow/DVC.

## Scaling

batch workers; pattern discovery is a scheduled job (weekly).

## Built in

Phase 11.

## Key invariants

no automatic production change — candidate promotion requires explicit approval + validation report; case memory, knowledge, rules and training data remain separate; EXPERT_PREFERENCE corrections never auto-promote; all 11 provenance fields non-null or explicitly N/A.

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/learning-service/
├── pyproject.toml
├── README.md
├── src/learning_service/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_learning_service.py
```
