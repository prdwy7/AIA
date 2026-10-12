# weather-service (S17)

> **Skeleton service** — built in WS-RULES (W1–W2, needed for weather-window rules).. Full spec: `docs/02-modules.md` §S17
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

weather context for rules.

## Responsibilities

IMD ingestion (central worker, 15–60 min poll: cityforecast/cityforecastloc, current weather, district/subdivision warnings, rainfall, AWS/ARG, Agromet Advisory); timestamp + location validation; unit normalization; `weather_snapshots` table; staleness marking (STALE after 6 h forecast / 2 h nowcast windows); spray-window evaluation input for S9; edge cache distribution via sync manifests.

## Tech

Python worker; HTTPS (IP-whitelisted, attribution); Postgres; manifest publisher.

## Interfaces

S9, S19 (down), S11 (context), S22 (staleness alerts).

## Dependencies

IMD API (IP whitelist), `weather_snapshots` table.

## Scaling

single idempotent worker; edge keeps last-known snapshot and marks STALE — never silently infers.

## Built in

WS-RULES (W1–W2, needed for weather-window rules).

## Key invariants

stale weather → spray-window rule returns UNKNOWN (never silently infers); attribution displayed per IMD terms.

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/weather-service/
├── pyproject.toml
├── README.md
├── src/weather_service/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_weather_service.py
```
