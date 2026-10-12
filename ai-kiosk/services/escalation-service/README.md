# escalation-service (S16)

> **Skeleton service** — built in Phase 10.. Full spec: `docs/02-modules.md` §S16
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

humans with complete handoff; the farmer never experiences a dead end.

## Responsibilities

escalation engine L0–L4 (roadmap §4.4) with evidence- and policy-driven triggers (repeated contradictory information; image cannot distinguish alternatives; treatment failed; severity increasing; suspected regulatory issue; novel symptom; possible harmful recommendation; scientist disagreement; missing critical information); assignment; status workflow OPEN → ASSIGNED → INVESTIGATING → RESOLVED → LEARNING_CAPTURED; compact human-handoff packet (summary, media, interpretation, contradictions, hypotheses, evidence, previous treatments, weather, AI recommendation, reason); farmer-facing transparency (case ID, status, next steps); SLA tracking and alerts.

## Tech

Python/FastAPI; packet builder (read-only aggregation); MQTT `alerts/safety` for L4 (QoS 2).

## Interfaces

S7, S13, channel adapters, S22, observability (alerts).

## Dependencies

`canonical-schema`, S7, EMQX.

## Scaling

stateless; low volume, high criticality.

## Built in

Phase 10.

## Key invariants

SLAs — L2 ≤ 24 h (trial: same day), L3 ≤ 48 h, L4 immediate + incident process; every escalation has an ID + status; farmer receives next-steps message on every escalation.

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/escalation-service/
├── pyproject.toml
├── README.md
├── src/escalation_service/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_escalation_service.py
```
