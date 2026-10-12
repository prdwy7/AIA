# mlops-service (S26)

> **Skeleton service** — built in Phase 14 (foundation W3, hardening W5).. Full spec: `docs/02-modules.md` §S26
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

the release pipeline (roadmap §4.5).

## Responsibilities

MLflow 3 registry (models, experiments) + DVC 3 dataset versioning; evaluation runners (RAGAS, DeepEval, promptfoo, lm-evaluation-harness) as CI jobs and scheduled production sampling; shadow-mode orchestration (candidate model on live cases, hidden output, comparison vs production + scientist decisions; exit: no safety regression, correction rate not worse, groundedness ≥ baseline); canary orchestration (device/case subsets); signed bundle build (model/KB/rules/prompt/speech); rollback (previous version retained ≥ 12 months, one-command restore, RTO ≤ 15 min/device); drift + correction-rate monitoring.

## Tech

Python; MLflow 3; DVC 3; GPU node (on-demand) for fine-tuning (Unsloth/axolotl + PEFT/LoRA).

## Interfaces

MLflow/DVC stores (MinIO + Postgres), CI/CD, S22, S10 (shadow), version_registry.

## Dependencies

MLflow, DVC, MinIO, GPU node.

## Scaling

batch/async; GPU node is on-demand (owned or rented).

## Built in

Phase 14 (foundation W3, hardening W5).

## Key invariants

no candidate can publish without validation + approval; previous production version restorable (drill, RTO ≤ 15 min); lockfiles are law; model artifacts content-addressed (SHA-256) + signed.

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/mlops-service/
├── pyproject.toml
├── README.md
├── src/mlops_service/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_mlops_service.py
```
