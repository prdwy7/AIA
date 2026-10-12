# web-adapter (S3)

> **Skeleton service** — built in Phase 2.. Full spec: `docs/02-modules.md` §S3
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

farmer-facing web/mobile PWA backend.

## Responsibilities

chat (text/voice optional), photo upload, case lookup by QR/short code, outcome reporting, follow-up responses. Pseudonymous (case-scoped tokens; no account required).

## Tech

React 18 + TypeScript PWA (Vite, Tailwind) + FastAPI backend.

## Interfaces

case-service (via S4), MinIO (uploads), Keycloak (optional login for returning farmers).

## Dependencies

S4, S23, MinIO.

## Scaling

stateless; static assets on CDN.

## Built in

Phase 2.

## Key invariants

same canonical case schema as kiosk/WhatsApp (Phase 2 exit: automated schema-parity test).

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/web-adapter/
├── pyproject.toml
├── README.md
├── src/web_adapter/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_web_adapter.py
```
