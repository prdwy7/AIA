# AIA — AI-Enabled Agricultural Advisory Kiosk

A **governed, offline-first, multimodal agricultural decision-support platform**
for KVK Banavasi (ICAR / ANGRAU), Kurnool district, Andhra Pradesh.

Farmers interact through four **first-class input modalities — voice, touch,
text, and picture** — on a kiosk (and later WhatsApp/web). The system builds a
persistent **Case-to-Solution Tree (CST)**, cross-checks understanding with the
farmer, retrieves authoritative evidence, applies deterministic
regulatory/agronomic/weather rules, drafts grounded answers with a local LLM,
and routes high-risk outputs through a **scientist gate** before any
prescription is printed or delivered.

## What's in this repository

| Path | What |
|---|---|
| [`AI_Kiosk_v2_Multimodal_Case_to_Solution.md`](AI_Kiosk_v2_Multimodal_Case_to_Solution.md) | v2.0 design — the case-to-solution tree + multimodal flow |
| [`AI_Kiosk_v2_Project_Roadmap.md`](AI_Kiosk_v2_Project_Roadmap.md) | Complete project roadmap (architecture, frameworks, 18-month plan) |
| [`ai-kiosk/`](ai-kiosk/) | **Implementation monorepo** — 26 services, canonical schema, rules engine, kiosk/UI, infra, docs, evals |

> For the full implementation README (quickstart, module S1–S26 context, model
> registry, tool stack), see **[ai-kiosk/README.md](ai-kiosk/README.md)**.

## Input modalities

- **Voice** — offline Telugu ASR: **Vaani-Whisper Telugu** (primary) → **SraVaani-1.0** (fast fallback) → **BHASHINI** (online cross-check), with Piper/BHASHINI text-to-speech.
- **Touch / Text** — kiosk touch UI; WhatsApp/web text.
- **Picture** — crop/disease/insect photos: quality checks, VLM observations, ViT classifier.

## Models (local, offline-first)

| Role | Model | Runtime |
|---|---|---|
| ASR primary | `ARTPARK-IISc/whisper-large-v3-vaani-telugu` (~2B) | HuggingFace `transformers` |
| ASR fallback | `ARTPARK-IISc/SraVaani-1.0` (~430M, ONNX) | ONNX Runtime (CPU) |
| ASR cross-check | BHASHINI ASR API | online |
| Edge LLM | Gemma 3 12B (primary), Llama 3.1 8B (fallback) | Ollama (offline) |
| Embeddings / Reranker | BGE-M3 / BGE-Reranker-v2-M3 | pgvector |
| TTS | Piper Telugu → BHASHINI TTS | CPU / online |

## Non-negotiable invariants

1. **The LLM is not the authority** — a deterministic rules engine + scientist
   gate control all high-risk output.
2. **Nothing is overwritten** — the case graph is append-only; corrections add nodes.
3. **No uncontrolled self-modification** — learning candidates need validation + approval.
4. **Reproducibility** — every prescription traces to a version tuple (model + knowledge + rules + prompt policy + speech + schema).
5. **Offline-first** — the edge runs the full pipeline for cached knowledge.
6. **Privacy by design** — pseudonymous farmers, DPDP Act 2023 compliant.

## Quickstart

```bash
# 1. Python workspace
cd ai-kiosk && uv sync --all-packages

# 2. Central dev stack (Postgres+pgvector, SeaweedFS S3, Redis, EMQX, Keycloak, observability)
docker compose -f infra/compose/dev-central.yml up -d

# 3. Tests
make test

# 4. Download ASR models (optional — for voice)
make download-models
```

Full development setup (ports, services, edge stack, kiosk build) is documented
in **[ai-kiosk/README.md](ai-kiosk/README.md)**.
