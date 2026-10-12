# kiosk-adapter (S1)

> **Skeleton service** — built in Phase 1 (MVP: touch+text+print, basic voice) → extended in Phases 2, 4, 5 (camera, cross-correction UX, media sets).. Full spec: `docs/02-modules.md` §S1
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

local bridge for the farmer-facing kiosk application (Flutter app lives in `kiosk/`).

## Responsibilities

voice capture (mic array → 16 kHz WAV), touch guided flow (pickers, quick replies, confirmation gates), text input (Telugu script + Latin keyboard), camera capture with framing guidance, TTS playback, print UI, session lifecycle (start/timeout/reset), offline queue visibility. All intelligence calls go to the local core-api over localhost.

## Tech

Flutter 3.x (Linux target), kiosk mode (auto-start, no desktop escape); plugins: `camera`, `record`/`audio`, `esc_pos_printer`, `usb_serial`, `local_auth` (operator PIN). This service is the local HTTP bridge the Flutter app talks to.

## Interfaces

core-api (localhost HTTP), thermal printer (USB/serial ESC/POS), device-agent (health queries), hardware sensors (temperature, UPS).

## Dependencies

S4, S5 (TTS playback), S12 (print), S20.

## Scaling

one instance per device; no horizontal scaling — reliability engineering instead (watchdog auto-restart, session resume, print idempotency).

## Built in

Phase 1 (MVP: touch+text+print, basic voice) → extended in Phases 2, 4, 5 (camera, cross-correction UX, media sets).

## Key invariants

every touch action is a typed `Input` node with `modality=touch`, confidence 1.0; no dead ends — every screen offers "talk to an expert", "print what I have", "start over"; do-not-repeat memory enforced in UI.

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/kiosk-adapter/
├── pyproject.toml
├── README.md
├── src/kiosk_adapter/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_kiosk_adapter.py
```
