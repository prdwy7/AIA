# whatsapp-adapter (S2)

> **Skeleton service** — built in Phase 2.. Full spec: `docs/02-modules.md` §S2
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

WhatsApp Business Cloud API adapter.

## Responsibilities

webhook verification + inbound (text/voice note/photo/multiple photos) → `case_id` mapping (phone → farmer_ref → active case); media download to MinIO; outbound rendering (text cards, quick replies, list messages, media); template management (India approval ~2–4 weeks; utility templates for follow-ups outside the 24-h window); per-message billing tracking (per-message since Jul 2025; free service tier from Oct 2026); queue + retry with backoff.

## Tech

Python/FastAPI; Meta Graph SDK; webhook signature verification; Redis outbound queue.

## Interfaces

Meta Cloud API, case-service (via S4), MinIO, speech-service (voice notes), image-service (photos).

## Dependencies

S4, S5, S6, S23, MinIO, Redis.

## Scaling

stateless, 2 replicas; webhook is at-least-once → idempotent handlers.

## Built in

Phase 2.

## Key invariants

no business logic in the adapter; billing category tracked per message; case continuity (kiosk → WhatsApp → kiosk).

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/whatsapp-adapter/
├── pyproject.toml
├── README.md
├── src/whatsapp_adapter/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_whatsapp_adapter.py
```
