# rules-service (S9)

> **Skeleton service** — built in WS-RULES (W1–W2); counterexample search in Phase 11.. Full spec: `docs/02-modules.md` §S9
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

deterministic policy package (API front for the `agri-rules` package).

## Responsibilities

regulatory checks (banned/refused/restricted → BLOCK/REVIEW/CONDITION), crop/target, formulation, dose range, application method, weather window (GREEN/CAUTION/BLOCKED/UNKNOWN), PHI/PPE/environment, confidence gates, clarification policy. Pure functions over typed context; every rule has `test_cases[]`; counterexample search for rule candidates.

## Tech

Python policy package (`agri-rules`) — no external rule engine (Drools/OPA evaluated and rejected: Java/external-runtime overhead, weaker test ergonomics for agronomic logic); versioned as a signed artifact (RULE version in the version tuple).

## Interfaces

S11, S12, S17 (context input), S14 (counterexample search).

## Dependencies

`agri-rules` package, `regulatory_products` table, weather snapshots.

## Scaling

in-process library (no network hop); zero scaling concerns. Test suite runs in CI on every build.

## Built in

WS-RULES (W1–W2); counterexample search in Phase 11.

## Key invariants

deterministic — the LLM cannot override; 100% of blocking rules covered by tests; property test: no blocked intervention can reach printable state; gaps surface as REVIEW, never silent pass.

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/rules-service/
├── pyproject.toml
├── README.md
├── src/rules_service/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_rules_service.py
```
