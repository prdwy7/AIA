# admin-console (S22)

> **UI skeleton** — built in Phase 1 (W1, basic) → W3–W5 (full). Full spec:
> `docs/02-modules.md` §S22.

## Purpose

Platform administration.

## Responsibilities

- Device fleet management (status, health, active version tuple, sync state).
- Release management (shadow → canary → production promotion, rollback).
- Users/roles.
- Audit views.
- KB/rules review workflows.
- Weather staleness alerts.
- Candidate queues.

## Tech

React 18 + TypeScript PWA; Keycloak OIDC (admin/auditor roles).

## Interfaces

version_registry, devices, Keycloak, S26 (mlops-service), S18 (knowledge-service),
S14 (learning-service).

## Dependencies

S23 (Keycloak), S26, S18, S14.

## Scaling

Stateless; small user base.

## Key invariants

- **Admin may not approve agricultural content** (role separation).
- **Two-person rule** for production promotion.
- Fleet shows the **active version tuple** per device.

## Run (dev)

```bash
cd ui/admin-console
npm install
npm run dev   # http://localhost:5174, proxies /v1 → http://localhost:8000
```
