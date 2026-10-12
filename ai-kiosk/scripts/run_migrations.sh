#!/usr/bin/env bash
# Apply SQL migrations (db/migrations/*.sql) to central + edge Postgres.
# Usage: ./scripts/run_migrations.sh   (== make migrate)
#
# Migrations are schema DDL (CREATE TABLE/INDEX/TRIGGER) run once per fresh DB;
# the dev compose stack auto-applies them at init (dev-central.yml / edge.yml
# mount db/migrations into docker-entrypoint-initdb.d).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MIGRATIONS_DIR="$ROOT/db/migrations"

# Prefer .env if present.
if [[ -f "$ROOT/.env" ]]; then
  set -a; source "$ROOT/.env"; set +a
fi

DB_URL="${DATABASE_URL:-postgresql+psycopg://kiosk:kiosk@localhost:5432/ai_kiosk}"
EDGE_DB_URL="${EDGE_DATABASE_URL:-postgresql+psycopg://kiosk:kiosk@localhost:5433/ai_kiosk_edge}"

# psycopg async URL → psql-compatible URL
to_psql() { printf '%s' "$1" | sed -E 's#^postgresql\+psycopg://#postgresql://#'; }

apply() {
  local url="$1"
  local name="$2"
  local psql_url
  psql_url="$(to_psql "$url")"
  echo "==> ${name}: ${psql_url}"
  for f in "$MIGRATIONS_DIR"/*.sql; do
    echo "    - $(basename "$f")"
    psql "$psql_url" -v ON_ERROR_STOP=1 -q -f "$f"
  done
}

command -v psql >/dev/null 2>&1 || { echo "psql not found — install postgresql-client"; exit 1; }

apply "$DB_URL" "central"
apply "$EDGE_DB_URL" "edge"

echo "Migrations complete."
