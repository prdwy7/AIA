#!/usr/bin/env bash
# One-shot developer bootstrap for the AI Kiosk repo (Phase 0–1 foundations).
# Usage: ./scripts/bootstrap.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> [1/5] Verifying uv..."
command -v uv >/dev/null 2>&1 || {
  echo "uv not found — install from https://docs.astral.sh/uv"; exit 1; }

echo "==> [2/5] Syncing Python workspace (all packages + services)..."
uv sync --all-packages

echo "==> [3/5] Applying DB migrations (central + edge)..."
./scripts/run_migrations.sh

echo "==> [4/5] Lint..."
uv run ruff check packages services

echo "==> [5/5] Tests..."
uv run pytest -q

cat <<EOF

Bootstrap complete.
Next:
  make dev-up     # central stack (Postgres+pgvector, MinIO, Redis, EMQX, Keycloak, ...)
  make edge-up    # edge simulator (Postgres, Redis, Mosquitto, Ollama)
  uv run uvicorn core_api.app:app --reload   # start a service (see services/*/README.md)
EOF
