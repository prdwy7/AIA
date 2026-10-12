# outcome-service (S15)

> **Skeleton service** — built in Phase 9.. Full spec: `docs/02-modules.md` §S15
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

closed loop — advice delivered ≠ problem solved.

## Responsibilities

follow-up scheduling from approved advisory protocols (not fixed intervals); outcome capture (worked/partial/failed/worsened/unknown) across channels (kiosk return visit, WhatsApp, extension worker, scientist portal); expected-observation tracking; failed-solution protocol (stop automatic repetition → reassess → request new evidence → compare original vs current case → check alternative hypotheses → escalate if triggers met); failure learning records.

## Tech

Python/FastAPI; scheduler (Redis-backed cron); channel adapter webhooks for delivery.

## Interfaces

S7, S16, channel adapters (S1/S2/S3), S14.

## Dependencies

`canonical-schema`, S7, S16.

## Scaling

stateless + scheduler; follow-up volume is small at pilot (dozens/day).

## Built in

Phase 9.

## Key invariants

failed interventions do NOT automatically trigger another intervention (test: failed case produces reassessment + evidence request, never an auto-re-prescription); "cannot determine" is a first-class outcome (unknown); every applicable intervention has a follow-up.

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/outcome-service/
├── pyproject.toml
├── README.md
├── src/outcome_service/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_outcome_service.py
```
