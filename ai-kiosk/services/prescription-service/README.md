# prescription-service (S12)

> **Skeleton service** — built in Phase 1 (print MVP in kiosk MVP) → full lock/verify in WS-AI (W2).. Full spec: `docs/02-modules.md` §S12
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

controlled output.

## Responsibilities

locked prescription objects — created only from approved decisions; records full version tuple; print job management (idempotent `print_id`, no duplicates on printer failure); QR generation (prescription_id + verification URL); public verification endpoint (QR scan → status, content, versions, scientist, expiry).

## Tech

Python/FastAPI; `qrcode`; ESC/POS print job format; MinIO (printed artifact archive).

## Interfaces

S11/S13 (input), print hardware (edge), MinIO, public verification API.

## Dependencies

`canonical-schema`, MinIO, printer (edge).

## Scaling

stateless; print queue on edge with retry + idempotency.

## Built in

Phase 1 (print MVP in kiosk MVP) → full lock/verify in WS-AI (W2).

## Key invariants

zero unapproved prescriptions (hard); printer failure never duplicates (idempotent `print_id`); blocked interventions cannot reach printable state.

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/prescription-service/
├── pyproject.toml
├── README.md
├── src/prescription_service/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_prescription_service.py
```
