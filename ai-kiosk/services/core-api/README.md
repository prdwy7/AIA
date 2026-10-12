# core-api (S4 entry point)

Central API for the AI Kiosk. Owns the public HTTP surface for sessions, cases
and inputs (docs/04-api-contracts.md §1). All other services expose their own
endpoints; this service is the single entry point for channel adapters and the
kiosk.

## Purpose

- Create kiosk sessions and cases (pseudonymous, consent-gated).
- Accept inputs across all four modalities (voice, touch, text, picture) and
  store them as immutable `Input` nodes on the Case-to-Solution Tree.
- Serve the case tree (append-only) for downstream services and the UI.

## Responsibilities

- `POST /v1/session` — create a kiosk session (consent required).
- `POST /v1/cases` — create a case (channel, location, language, farmer_ref?).
- `POST /v1/cases/{id}/inputs` — add a typed input (modality + payload/media + asr?).
- `GET /v1/cases/{id}/tree` — retrieve the full CST.
- `GET /health`, `GET /ready` — liveness/readiness (docs/04 §8).

## Tech

- Python 3.12, FastAPI, Pydantic v2.
- `canonical-schema` for all request/response and domain models.
- In-memory append-only store for dev/test; PostgreSQL (migration 0002) in
  production — same invariants, DB-trigger enforced.

## Interfaces

- Inbound: kiosk (localhost), WhatsApp/web adapters (via gateway).
- Outbound: speech-service, image-service, case-service (via S4 routing in
  production; this service holds the case graph in the pilot).

## Dependencies

- `canonical-schema`, `agri-rules` (workspace packages).
- PostgreSQL 17 + pgvector (production), Redis (session state, production).

## Scaling

Stateless API; horizontal replicas behind the API gateway. Session state is
externalized (Redis). The case graph is the hot path: node append + state
transition only.

## Built in

Phase 1 (MVP: sessions, cases, inputs, tree). Full tree semantics (questions,
answers, corrections, contradictions) land in Phase 3 with case-service.

## Key invariants

- Every input becomes an immutable `Input` node with modality metadata.
- Voice inputs **require** an `asr` result (enforced by the schema).
- Touch inputs carry `confidence = 1.0`.
- The tree is append-only: no UPDATE except status transitions
  (`active -> superseded | rejected`).
- Mixed modalities within one case are always allowed.
- Errors are RFC 7807 `problem+json` with domain error codes.

## Run

```bash
uv sync
uv run uvicorn core_api.app:app --reload
uv run pytest services/core-api -q
```
