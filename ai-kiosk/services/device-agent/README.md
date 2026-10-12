# device-agent (S20)

> **Skeleton service** — built in basic in Phase 1 (W1); full in WS-OFFLINE (W3).. Full spec: `docs/02-modules.md` §S20
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

device health and lifecycle (edge daemon).

## Responsibilities

CPU/GPU/memory/disk/temperature, printer status (paper, errors), network status (Ethernet/Wi-Fi/4G), UPS state, graceful shutdown on power loss, watchdog for kiosk-ui and core-api, signed update verification and staged activation, telemetry batching.

## Tech

Python daemon (systemd), `nvidia-smi`/`tegrastats` for GPU, MQTT telemetry publisher with local buffering.

## Interfaces

MQTT `kiosk/{device_id}/telemetry|ack`, S22 (via central), S19 (update activation).

## Dependencies

EMQX, hardware sensors.

## Scaling

per-device; no scaling concerns. Fleet view in admin console.

## Built in

basic in Phase 1 (W1); full in WS-OFFLINE (W3).

## Key invariants

no inbound ports on the device; no secrets on edge except device cert + sync key (LUKS-protected keystore); power loss → graceful shutdown → clean state.

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/device-agent/
├── pyproject.toml
├── README.md
├── src/device_agent/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_device_agent.py
```
