# observability (S25)

Full reproducibility of any production answer: OpenTelemetry traces/span + metrics
+ structured logs, Prometheus + Grafana + Loki on central, edge telemetry shipped
via MQTT with local buffering.

Files:
- `prometheus.yml` — scrape config for central services + (empty) edge devices.
- `loki-config.yaml` — Loki dev config (logs; audit records live in Postgres).
- `grafana/` — provisioned dashboards (populated in W2+).

Invariants (docs/02 §S25): every decision-bearing response includes
`version_tuple` + `trace_id`; security logs separated from farmer analytics.
See `infra/k3s/` for the OpenTelemetry collector placement and `docs/08` §6 for
the KPI/metric catalog.
