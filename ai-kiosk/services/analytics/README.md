# analytics (S24)

> **Skeleton service** — built in W3 (operations + safety) → W4 (trial dashboards) → W5 (surveillance + learning).. Full spec: `docs/02-modules.md` §S24
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

dashboards on the system of record.

## Responsibilities

Metabase dashboards on the central Postgres: service operations (queries/day, response time, print success, escalations); crop intelligence (crop/stage distribution); pest surveillance (incidence by geography/time — review signal only, never autonomous outbreak declaration); AI quality (correction rate/types); safety (blocked interventions, regulatory conflicts); knowledge (unanswered questions, stale records); language (ASR confidence, corrected entities); learning (accepted corrections, candidate rules, model versions); device (uptime, errors, temperature, sync backlog).

## Tech

Metabase (OSS) on PostgreSQL; scheduled aggregate tables (nightly) to keep dashboards fast.

## Interfaces

Postgres (read replica).

## Dependencies

PostgreSQL, Metabase.

## Scaling

read replica; aggregate tables.

## Built in

W3 (operations + safety) → W4 (trial dashboards) → W5 (surveillance + learning).

## Key invariants

surveillance is aggregate only, mandal-level minimum granularity, no individual farmer identification; access: scientist/admin/auditor only, logged.

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/analytics/
├── pyproject.toml
├── README.md
├── src/analytics/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_analytics.py
```
