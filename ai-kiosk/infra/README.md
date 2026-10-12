# infrastructure

Deployment topology for the AI Kiosk system (docs/01-architecture.md).

| Path | What | Reference |
|---|---|---|
| `compose/dev-central.yml` | Central dev stack (Postgres+pgvector, SeaweedFS S3, Redis, EMQX, Keycloak, Prometheus, Grafana, Loki, Metabase) | `make dev-up` |
| `compose/edge.yml` | Simulated edge (Postgres+pgvector, Redis, Mosquitto, Ollama) | `make edge-up` |
| `compose/mosquitto.conf` | Edge MQTT dev config | edge.yml |
| `docker/Dockerfile.service` | Build any FastAPI service (`--build-arg SERVICE=…`) | services/*|
| `docker/Dockerfile.edge` | Edge device runtime (core pipeline + Ollama) | kiosk/ |
| `caddy/Caddyfile` | Public gateway (TLS + mTLS for sync) | S19/S23 |
| `k3s/` | Central cluster skeletons (stateless services) | docs/01 |
| `keycloak/` | Realm + roles (S23) | docs/02 §S23 |
| `observability/` | Prometheus + Loki config (S25) | docs/02 §S25 |
| `terraform/` | Central managed infra skeleton | docs/01 |

## Quick start (dev)

```bash
make dev-up          # central stack on localhost (5432/9000/6379/1883/8080/9090/3000/3100/3001)
make edge-up         # edge simulator (5433/6380/1884/11434)
make migrate         # apply db/migrations/*.sql (via scripts/run_migrations.sh)
```

## Environment

All services read configuration from `.env` (see `.env.example` at repo root).
Central and edge share the same service images; the only differences are the
`DEVICE_MODE`/`DATABASE_URL`/`MQTT_*` variables and the model bundle present.
