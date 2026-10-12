# sync-agent (S19)

> **Skeleton service** — built in core sync in WS-OFFLINE (W3); media sync in Phase 12.. Full spec: `docs/02-modules.md` §S19
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

encrypted, idempotent, resumable synchronization (edge + central peer).

## Responsibilities

up — append-only events (inputs, decisions, corrections, outcomes, telemetry, print jobs) batched with sequence numbers; down — signed versioned manifests (knowledge, rules, models, prompt policy, lexicon, weather baseline) → fetch from MinIO → verify signature → activate. Gap detection and repair; media queue (chunked, resumable uploads).

## Tech

Python (edge) + FastAPI endpoints (central); MQTT (EMQX) for manifest/command signaling; HTTPS for bulk transfer; minisign/cosign signature verification; LUKS-encrypted local queue.

## Interfaces

EMQX topics (roadmap §7.5), core-api `/v1/sync/*`, MinIO, S20 (activation hooks).

## Dependencies

EMQX, MinIO, S20.

## Scaling

per-device instance with backpressure; central peer is stateless workers. Idempotency by `event_id` makes retries safe.

## Built in

core sync in WS-OFFLINE (W3); media sync in Phase 12.

## Key invariants

idempotent by event ID (retries safe); append-only (conflicts structurally impossible for case data); media dedup by content hash; unsigned/invalid bundles rejected + alert.

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/sync-agent/
├── pyproject.toml
├── README.md
├── src/sync_agent/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_sync_agent.py
```
