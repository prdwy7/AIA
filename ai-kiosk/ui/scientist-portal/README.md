# scientist-portal (S21)

> **UI skeleton** — built in WS-PORTAL (W2) → Phase 8 (multimodal). Full spec:
> `docs/02-modules.md` §S21.

## Purpose

The scientist's workbench.

## Responsibilities

- Review queue (prescriptions + uncertain cases).
- Minimal-field correction UX (approve/correct/escalate; only wrong fields editable).
- Multimodal feedback (text, voice → ASR → structured correction, image, annotated image).
- Automatic context display (read-only snapshot).
- Candidate approval (knowledge/rule/training/language).
- Escalation queue with SLA.
- Dashboards (AI quality, safety, learning).

## Tech

React 18 + TypeScript PWA; Keycloak OIDC; WebSocket/SSE for queue updates.

## Interfaces

S13 (review-service), S14 (learning-service), S16 (escalation-service), S7
(case tree view), S5 (voice feedback).

## Dependencies

S13, S14, S16, S23 (Keycloak).

## Scaling

Stateless; small user base (dozens of scientists at district scale).

## Key invariants

- **MFA (TOTP) required.**
- Context snapshot is **read-only**.
- Scientist changes **only the wrong fields**; original AI decision is never
  overwritten.
- UAT with ≥ 3 KVK scientists (Phase 8 exit).

## Run (dev)

```bash
cd ui/scientist-portal
npm install
npm run dev   # http://localhost:5173, proxies /v1 → http://localhost:8000
```
