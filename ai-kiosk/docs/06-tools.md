# 06 — Tools (Dependency Registry)

> Roadmap §5. Versions are the **baseline pins** for the start of implementation
> (Sep 2026). All pins live in lockfiles (`uv.lock`, `package.json`, Dockerfile
> tags); upgrades follow the release framework (roadmap §4.5) with regression gates.
> "Alt" = approved alternative if the primary fails its evaluation gate.

## 1. Platform & infrastructure

| Tool | Baseline version | License | Used for | Alt |
|---|---|---|---|---|
| Python | 3.12.x | PSF | All backend services | 3.11 |
| FastAPI | 0.116.x | MIT | HTTP APIs (core + adapters) | Starlette directly |
| Pydantic | 2.x | MIT | Schema validation (all boundaries, LLM output) | — |
| PostgreSQL | 17.x | PostgreSQL | System of record + vectors | 18 (when pgvector 0.8.2 GA-stable on it) |
| pgvector | 0.8.2 | PostgreSQL | Vector similarity (HNSW) | — |
| Redis | 7.4 | BSD | Cache/queues | — |
| MinIO (prod) | RELEASE.2025-xx | AGPL-3.0 (or S3-compatible cloud) | Object storage | S3-compatible cloud |
| SeaweedFS (dev) | latest | Apache-2.0 | S3-compatible object storage in local/compose dev stack (MinIO stopped publishing free images Oct 2025) | MinIO or any S3 endpoint |
| EMQX | 5.x | Apache-2.0 (CE) | MQTT broker (central) | Mosquitto 2.x |
| Mosquitto | 2.x | EPL-1.0 | Edge MQTT broker | EMQX edge |
| Keycloak | 26.x | Apache-2.0 | OIDC identity | Zitadel |
| Caddy / Traefik | latest stable | Apache-2.0 | TLS termination, WAF | Nginx |
| Docker | 27.x | Apache-2.0 | Container runtime (edge) | Podman 5 |
| K3s | 1.3x | Apache-2.0 | Central cluster | Plain VMs + systemd (pilot) |
| Terraform | 1.9 | BUSL-1.1 | IaC | Pulumi |
| GitHub Actions | — | — | CI/CD | GitLab CI |
| Prometheus | 2.x | Apache-2.0 | Metrics | — |
| Grafana | 11.x | AGPL-3.0 | Dashboards | — |
| Loki | 3.x | AGPL-3.0 | Logs | — |
| OpenTelemetry SDK (Python) | 1.x | Apache-2.0 | Traces/metrics/logs | — |
| Metabase | latest OSS | AGPL-3.0 | Analytics dashboards | Superset |

## 2. AI/ML components

| Component | Baseline | License | Role | Alt / notes |
|---|---|---|---|---|
| Ollama | 0.34.x | MIT | Edge LLM runtime | llama.cpp server |
| Gemma 3 12B (Q4/Q5 GGUF) | Mar 2025 release | Gemma ToU | Edge LLM + vision observations | Llama 3.1 8B (lighter), Qwen2.5 14B |
| Llama 3.1 8B Instruct | Jul 2024 | Llama 3.1 Community License | Lightweight edge LLM | — |
| Sarvam-M 24B | May 2025 | Apache-2.0 | Central LLM (online mode), evaluation judge | Llama 3.3 70B (if infra allows) |
| whisper-large-v3-vaani-telugu (ARTPARK-IISc) | Sep 2026 | Apache-2.0 | **Primary** offline Telugu ASR (2B, Vaani fine-tune, Telugu lexicon) | vanilla Whisper large-v3 (benchmark only) |
| SraVaani-1.0 (ARTPARK-IISc) | 2026 | MIT | **Fast fallback** offline ASR (~430M, ONNX, Telugu WER ~25.1) | IndicWav2Vec Telugu |
| faster-whisper | 1.x | MIT | Runtime for Whisper-family models (int8 quantization) | transformers pipeline |
| IndicWav2Vec (Telugu) | AI4Bharat checkpoint | Research + commercial check | Domain ASR fine-tune candidate (Phase 5) | — |
| BHASHINI ASR/TTS API | current | Govt. platform terms | Online speech (higher quality) | — |
| Piper (piper1-gpl) | current | MIT | Offline Telugu TTS | BHASHINI TTS (online) |
| BGE-M3 | 2024 (v5 paper Dec 2025) | MIT | Embeddings (dense+sparse) | multilingual-e5-large |
| BGE-Reranker-v2-M3 | 2024 | MIT | Reranking | — |
| PyTorch | 2.x | BSD | Classifier training/inference | — |
| ViT / ConvNeXt (timm) | latest | Apache-2.0 | Disease/pest classifier backbone | MobileViT (lighter edge) |
| Unsloth | latest | MIT | LoRA fine-tuning (fast) | axolotl |
| PEFT / transformers (HF) | latest | Apache-2.0 | Fine-tuning + inference | — |
| MLflow | 3.x | Apache-2.0 | Model registry + tracking | W&B (if licensed) |
| DVC | 3.x | Apache-2.0 | Dataset versioning | LakeFS |
| RAGAS | 0.3.x | Apache-2.0 | RAG metrics | DeepEval RAG metrics |
| DeepEval | 2.x | Apache-2.0 | pytest-style app eval | — |
| promptfoo | 0.9x | MIT | Red-teaming, CI eval gates | Garak |
| lm-evaluation-harness | latest | MIT | Model benchmarking (MMLU-IN, VākQA) | — |

## 3. Client & integration

| Tool | Baseline | License | Role |
|---|---|---|---|
| Flutter | 3.3x | BSD-3 | Kiosk app (voice/touch/text/camera/print/TTS) |
| React + TypeScript | 18/5.x | MIT | Scientist portal, admin console, web channel PWA |
| Vite | 6.x | MIT | Frontend build |
| Tailwind CSS | 4.x | MIT | UI styling |
| WhatsApp Business Cloud API | current (Meta) | Meta terms | WhatsApp channel (text/voice/photo) |
| Meta Graph SDK / webhook | current | Meta terms | Webhook handling |
| ESC/POS printer libs (e.g., `python-escpos`, Flutter `esc_pos_printer`) | current | MIT | Thermal printing |
| qrcode (Py) / QR libraries | current | MIT | Prescription QR + case short-code QR |
| Pillow / OpenCV | latest | MIT / Apache-2.0 | Image preprocessing, quality checks |
| silero-vad | latest | MIT | Voice activity detection (kiosk + WhatsApp notes) |
| ffmpeg | 7.x | LGPL | Audio normalization (16 kHz WAV for ASR) |
| pypdf / unstructured / marker | latest | MIT/Apache | KB document ingestion (PDFs, manuals) |

## 4. External data & services (managed dependencies)

| Dependency | Source | Access mode | Refresh policy | Failure behavior |
|---|---|---|---|---|
| Weather forecast/nowcast/warnings | IMD API (api.imd.gov.in) | HTTPS, IP-whitelisted, attribution | 15–60 min poll (central) → edge cache | Mark STALE after window; rules return UNKNOWN; never silently infer |
| Agromet advisory | IMD Agromet Advisory API | HTTPS | Daily | Cache last valid |
| Pesticide regulatory lists (banned/refused/restricted) | PPQS/CIB&RC (ppqs.gov.in) + gazette notifications | Manual + monitored download | On publication + quarterly audit | Last verified version stays active; admin alerted |
| Product registration data | CIB&RC | Manual ingestion | Quarterly | — |
| Speech (online) | BHASHINI API | HTTPS + API key | On-demand | Fallback to offline Piper/Whisper |
| WhatsApp | Meta Cloud API (via BSP) | HTTPS webhooks + REST | Real-time | Queue outbound; retry with backoff; case continues on other channels |

**WhatsApp billing (verified Sep 2026):** per-message billing for template messages
since 1 Jul 2025; service conversations in the 24-h window free (since 1 Nov 2024);
utility templates in an open window free (since 1 Jul 2025); from 1 Oct 2026 a
monthly free tier of 1,000 service messages per business number, then per-message;
India INR billing since Jan 2026 (utility ≈ ₹0.115/msg, marketing ≈ ₹0.8631);
further pricing updates 1 Aug 2026 + 1 Oct 2026; template approval lead time in
India ~2–4 weeks.

## 5. Version pinning & dependency management

1. **Lockfiles are law**: `uv.lock` (Python), `package.json`/`pnpm-lock.yaml` (web), Dockerfile `ARG` pins, `go.sum` where applicable. CI fails on unpinned dependencies.
2. **Model artifacts are content-addressed**: every model/KB/rules bundle has a SHA-256 + signature; the version registry maps logical versions (MODEL-0.1.0) to artifact digests.
3. **Dependency update cadence**: security patches within 7 days; minor updates monthly with regression gate; major updates per release framework with expert sign-off for AI components.
4. **License compliance**: all production dependencies pass a license audit (permitted: MIT/Apache/BSD/PostgreSQL/PSF; reviewed: AGPL for internal-only services like MinIO/Metabase/Loki/Grafana; Gemma ToU and Llama CL reviewed by institution legal).

## 6. Dependency graph (build & runtime)

```text
                    ┌──────────────────────────────┐
                    │        CI/CD (GitHub Actions)│
                    │  lint · test · eval · redteam│
                    │  sign · publish (GHCR/MinIO) │
                    └──────────────┬───────────────┘
                                   │ signed images + bundles
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
 ┌─────────────┐           ┌──────────────┐           ┌──────────────┐
 │ EDGE (kiosk)│           │ CENTRAL (K3s)│           │ GPU NODE     │
 │ Docker      │           │ K3s          │           │ (on-demand)  │
 │ Compose     │           │              │           │ Unsloth/     │
 │             │           │              │           │ axolotl      │
 ├─────────────┤           ├──────────────┤           └──────────────┘
 │ kiosk-ui    │           │ adapters     │                  ▲
 │ core-api    │           │ core services│                  │ fine-tune jobs
 │ Ollama      │◄──signed──│ Keycloak     │                  │ (approved candidates)
 │ whisper     │  bundles  │ Postgres+vec │                  │
 │ piper       │           │ MinIO        │                  │
 │ Postgres    │           │ MLflow/DVC   │                  │
 │ EMQX edge   │──mTLS────►│ EMQX central │                  │
 │ printer/UPS │  sync     │ Prometheus/  │                  │
 └─────────────┘           │ Grafana/Loki │                  │
                           │ Metabase     │                  │
                           └──────────────┘                  │
        External: IMD · PPQS · BHASHINI · WhatsApp/Meta · (IMD IP whitelist)
```
