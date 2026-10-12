.PHONY: install dev-up dev-down migrate download-models test lint typecheck eval-gate kiosk-build

install:            ## Install Python workspace (all packages + services)
	uv sync --all-packages

dev-up:             ## Start central dev stack
	docker compose -f infra/compose/dev-central.yml up -d

dev-down:
	docker compose -f infra/compose/dev-central.yml down

edge-up:            ## Start simulated edge stack
	docker compose -f infra/compose/edge.yml up -d

edge-down:
	docker compose -f infra/compose/edge.yml down

migrate:            ## Apply DB migrations
	./scripts/run_migrations.sh

download-models:    ## Download ASR models (Vaani-Whisper + SraVaani) from HuggingFace
	./scripts/download_models.sh

test:               ## Run all tests
	uv run pytest -q

lint:
	uv run ruff check packages services

typecheck:
	uv run mypy packages/canonical-schema/src packages/agri-rules/src

eval-gate:          ## Run AI evaluation gate (RAGAS/DeepEval/promptfoo)
	./scripts/run_eval_gate.sh

kiosk-build:        ## Build Flutter kiosk app
	cd kiosk && flutter build linux --release
