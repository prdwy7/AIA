# K3s — central cluster (light skeleton)

Production central runs the **stateless** services on K3s; the stateful tier
(Postgres 17 + pgvector, MinIO/S3, Redis, EMQX, Keycloak) is externalized to
managed services (see `infra/terraform/main.tf`). For local/staging the same
topology is reproduced with Docker Compose (`infra/compose/dev-central.yml`).

## What runs on the cluster

- Core services: core-api, input-orchestrator, case-service, retrieval-service,
  rules-service, llm-service (GPU node), advisory-service, prescription-service,
  review-service, learning-service, outcome-service, escalation-service,
  weather-service, knowledge-service, mlops-service.
- Channel adapters: whatsapp-adapter, web-adapter.
- UIs: admin-console (S22), scientist-portal (S21), web-adapter PWA (S3).
- Observability agents (OpenTelemetry collector, Prometheus, Grafana, Loki).

## Device/edge tier

Edge kiosks run outside the cluster — one device per instance, offline-capable,
synced via `sync-agent` (mTLS, signed manifests). See `infra/compose/edge.yml`.

## Layout

- `central.yaml` — namespace + placeholder Deployment (reference pattern).
- Full Helm/Kustomize charts ship in W3–W5 (production hardening); this is the
  Phase-1 skeleton referenced by docs/01-architecture.md.
