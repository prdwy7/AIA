# AI-Enabled Agricultural Advisory Kiosk — Implementation Monorepo

A **governed, offline-first, multimodal agricultural decision-support platform** for KVK Banavasi (ICAR / ANGRAU), Kurnool district, Andhra Pradesh.

Farmers interact through **four first-class input modalities — voice, touch, text, and picture** — on a kiosk (and later WhatsApp/web). The system builds a persistent **Case-to-Solution Tree (CST)**, cross-checks understanding with the farmer, retrieves authoritative evidence, applies deterministic regulatory/agronomic/weather rules, drafts grounded answers with a local LLM, and routes high-risk outputs through a **scientist gate** before any prescription is printed or delivered.

> **Design documents (source of truth):**
> - `../AI_Kiosk_v2_Multimodal_Case_to_Solution.md` — v2.0 design (case-to-solution tree)
> - `../AI_Kiosk_v2_Project_Roadmap.md` — complete project roadmap (architecture, frameworks, 18-month plan)

## Repository layout

```
ai-kiosk/
├── docs/                  # Project context, architecture, modules, models, tools, ops
│   ├── 00-project-context.md
│   ├── 01-architecture.md
│   ├── 02-modules.md          # Context for every module (S1–S26)
│   ├── 03-data-model.md
│   ├── 04-api-contracts.md
│   ├── 05-models.md           # List of models (ML + data)
│   ├── 06-tools.md            # Tool dependency registry
│   ├── 07-security-privacy.md
│   ├── 08-operations.md
│   └── 09-roadmap.md
├── packages/
│   ├── canonical-schema/    # Pydantic v2 models for the entire case graph (Phase 1 core)
│   └── agri-rules/          # Deterministic rules engine (regulatory/PHI/PPE/weather gates)
├── services/                # 26 services (S1–S26) — see docs/02-modules.md
├── ui/
│   ├── scientist-portal/    # React 18 + TypeScript PWA (S21)
│   └── admin-console/       # React 18 + TypeScript PWA (S22)
├── kiosk/                   # Flutter kiosk app (S1) — voice/touch/text/picture/print
├── db/migrations/           # PostgreSQL 17 + pgvector DDL
├── models/                  # ML model registry: pins, licenses, cards, gates
├── evals/                   # Golden cases, agri-vocab ASR set spec, RAGAS/DeepEval/promptfoo
├── infra/                   # Docker, compose (dev central + edge), Caddy, K3s, Terraform
├── ci/workflows/            # GitHub Actions: CI, eval gate, release
└── scripts/                 # bootstrap, migrations, service-skeleton generator
```

## Quickstart (development)

Prerequisites: Python 3.12, [uv](https://docs.astral.sh/uv/), Docker, Node 20 (UIs), Flutter 3.x (kiosk).

```bash
# 1. Install Python workspace
uv sync

# 2. Start the central dev stack (Postgres 17 + pgvector, SeaweedFS S3, Redis, EMQX,
#    Keycloak, Prometheus, Grafana, Loki, Metabase)
docker compose -f infra/compose/dev-central.yml up -d

# 3. Apply migrations
make migrate            # or: scripts/run_migrations.sh

# 4. Run tests (schema + rules + services)
make test

# 5. Run a service (example: core API)
uv run uvicorn core_api.app:app --reload --port 8001   # 8000 is often taken by other local apps

# 6. Kiosk edge stack (simulated edge on this machine)
docker compose -f infra/compose/edge.yml up -d
```

## The 26 modules (S1–S26)

| # | Module | Layer | One-line context |
|---|--------|-------|------------------|
| S1 | channel-adapter-kiosk | Edge | Flutter kiosk: voice/touch/text/picture capture, TTS, print |
| S2 | channel-adapter-whatsapp | Central | WhatsApp Cloud API in/out; media; phone→case mapping |
| S3 | channel-adapter-web | Central | PWA chat, photo upload, QR/short-code case lookup |
| S4 | input-orchestrator | Core | Routes all modalities to processors; owns session state |
| S5 | speech-service | Core | ASR chain (Vaani-Whisper → SraVaani → BHASHINI) + Piper TTS |
| S6 | image-service | Core | Quality checks, VLM observations, ViT classifier, media sets |
| S7 | case-service | Core | Canonical case graph (CST), contradiction detection |
| S8 | retrieval-service | Core | Hybrid retrieval: SQL + BM25 + pgvector (BGE-M3) + reranker |
| S9 | rules-service | Core | Deterministic policy: regulatory, dose, PHI/PPE, weather window |
| S10 | llm-service | Core | Ollama inference, structured output, prompt-policy versioning |
| S11 | advisory-service | Core | Composes evidence + rules + LLM draft into grounded advisory |
| S12 | prescription-service | Core | Locked prescription, print job, QR, verification endpoint |
| S13 | review-service | Core | Scientist queue; approve/correct/escalate; context snapshot |
| S14 | learning-service | Core | Delta classifier; candidates; provenance; sandbox |
| S15 | outcome-service | Core | Follow-ups, outcome capture, failure protocol |
| S16 | escalation-service | Core | L0–L4 engine, assignment, handoff packets |
| S17 | weather-service | Core | IMD ingestion, cache, staleness, spray-window input |
| S18 | knowledge-service | Core | KB ingestion, review workflow, versioning, edge bundles |
| S19 | sync-agent | Edge/central | Encrypted, idempotent, resumable sync + media queue |
| S20 | device-agent | Edge | Health, printer, disk, graceful shutdown, signed updates |
| S21 | scientist-portal | Central UI | React PWA: review, multimodal feedback, dashboards |
| S22 | admin-console | Central UI | React PWA: devices, releases, users, audit |
| S23 | identity (Keycloak) | Central | OIDC; farmer/operator/scientist/admin/auditor roles |
| S24 | analytics | Central | Metabase dashboards (ops, surveillance, AI quality, safety) |
| S25 | observability | Cross-cutting | OpenTelemetry + Prometheus + Grafana + Loki |
| S26 | mlops-service | Central | MLflow + DVC, eval runners, shadow/canary, rollback |

Full per-module context (responsibilities, interfaces, dependencies, invariants, build phase): [docs/02-modules.md](docs/02-modules.md).

## List of models (ML)

| Role | Model | License | Where |
|------|-------|---------|-------|
| ASR primary (offline) | ARTPARK-IISc/whisper-large-v3-vaani-telugu (2B) | Apache-2.0 | Edge (faster-whisper int8) |
| ASR fast fallback (offline) | ARTPARK-IISc/SraVaani-1.0 (~430M, ONNX) | MIT | Edge (CPU path) |
| ASR online / cross-check | BHASHINI ASR API | Govt. platform | Central |
| TTS (offline) | Piper — Telugu voice | MIT | Edge (CPU) |
| TTS (online) | BHASHINI TTS API | Govt. platform | Central |
| Edge LLM + vision | Gemma 3 12B (Q4/Q5 GGUF) | Gemma ToU | Edge (Ollama) |
| Edge LLM (light) | Llama 3.1 8B Instruct | Llama 3.1 Community License | Edge (Ollama) |
| Central LLM (online) | Sarvam-M 24B | Apache-2.0 | Central / GPU node |
| Vision classification | Fine-tuned ViT/ConvNeXt (KVK dataset) | Internal | Edge (ONNX) |
| Embeddings | BGE-M3 (569M) | MIT | Edge + central |
| Reranker | BGE-Reranker-v2-M3 | MIT | Edge + central |

Registry with version pins, gates, and model cards: [models/](models/). Full detail: [docs/05-models.md](docs/05-models.md).

## Tool stack (baseline pins, Sep 2026)

Python 3.12 · FastAPI · Pydantic v2 · PostgreSQL 17 + pgvector 0.8.2 · Ollama 0.34.x · Redis 7 · SeaweedFS S3 (dev) / MinIO (prod) · EMQX 5 / Mosquitto 2 · Keycloak 26 · Caddy · Docker 27 / K3s 1.3x · Terraform 1.9 · GitHub Actions · OpenTelemetry + Prometheus + Grafana + Loki · MLflow 3 + DVC 3 · RAGAS + DeepEval + promptfoo + lm-evaluation-harness · Unsloth/axolotl + PEFT · Metabase · Flutter 3.x · React 18 + TypeScript · WhatsApp Business Cloud API · IMD API.

Full registry (versions, licenses, alternatives): [docs/06-tools.md](docs/06-tools.md).

## Non-negotiable invariants (enforced in code)

1. **The LLM is not the authority** — rules engine + scientist gate control all high-risk output.
2. **Nothing is overwritten** — the case graph is append-only; corrections create new nodes.
3. **No uncontrolled self-modification** — learning candidates need validation + expert approval + versioning.
4. **Reproducibility** — every prescription traces to a version tuple (model + knowledge + rules + prompt policy + speech + schema).
5. **Offline-first** — the edge runs the complete decision pipeline for cached knowledge.
6. **Privacy by design** — pseudonymous farmers, faces blurred by default, DPDP Act 2023 compliant before trial.

## Phases

18 months, 5 waves, 16 phases. This repository implements **Phase 0–1 foundations** (governance artifacts, canonical schema, platform skeleton, kiosk MVP) and provides the structure for all later phases. See [docs/09-roadmap.md](docs/09-roadmap.md).
