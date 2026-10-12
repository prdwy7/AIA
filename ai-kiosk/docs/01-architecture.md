# 01 — Architecture

> Roadmap §3. Edge = per-kiosk device; central = K3s cluster (or VMs) at KVK.

## 1. Architecture principles

1. **Single canonical case service.** All channels and modalities write to one case graph; no channel owns intelligence.
2. **Deterministic core, probabilistic edges.** Rules and safety are pure functions with tests; LLM output is always schema-validated before entering the pipeline.
3. **Append-only history.** Original inputs, interpretations, AI decisions and corrections are immutable; corrections create new nodes, never overwrites.
4. **Edge autonomy.** The kiosk runs the full decision pipeline locally (except live weather and new knowledge); the central platform is the system of record and the publishing authority.
5. **Everything versioned.** Model, knowledge, rules, prompt policy, speech assets and schema form a **version tuple** recorded on every prescription.
6. **Boring technology at the core.** PostgreSQL + Python + Docker; specialized AI components isolated behind service interfaces so models can be swapped without re-architecture.

## 2. System context (C4 Level 1)

```text
                         ┌─────────────────────────────────────────────┐
                         │                FARMER                       │
                         │  voice · touch · text · picture             │
                         └──────┬──────────────┬──────────────┬────────┘
                                │              │              │
                     ┌──────────▼───┐   ┌──────▼─────┐  ┌─────▼──────┐
                     │   KIOSK      │   │  WHATSAPP  │  │ WEB /      │
                     │ (KVK site)   │   │ (Cloud API)│  │ MOBILE     │
                     └──────────┬───┘   └──────────┬──┘  └─────┬──────┘
                                │              │              │
                                │      ┌───────┴──────────────┴──────┐
                                │      │      CHANNEL ADAPTERS       │
                                │      └──────────────┬──────────────┘
                                │                     │
        ┌───────────────────────┼─────────────────────┼───────────────────────┐
        │                       ▼                     ▼                       │
        │   ┌────────────────────────────────────────────────────────────┐    │
        │   │              CANONICAL CASE SERVICE (core)                 │    │
        │   │  Case-to-Solution Tree · Interpretation · Hypotheses ·     │    │
        │   │  Questions · Evidence · Decisions · Outcomes · Escalations │    │
        │   └──────┬───────────────┬──────────────┬──────────────┬───────┘    │
        │          ▼               ▼              ▼              ▼            │
        │   ┌────────────┐  ┌────────────┐ ┌────────────┐ ┌────────────┐     │
        │   │ KNOWLEDGE  │  │   RULES    │ │  WEATHER   │ │  SIMILAR   │     │
        │   │ (RAG/KB)   │  │  ENGINE    │ │  CONTEXT   │ │  CASES     │     │
        │   └────────────┘  └────────────┘ └────────────┘ └────────────┘     │
        │          └───────────────┴──────┬───────┴──────────────┘            │
        │                                 ▼                                   │
        │                     ┌───────────────────────┐                       │
        │                     │  LOCAL LLM (draft)    │                       │
        │                     └───────────┬───────────┘                       │
        │                     ┌───────────────────────┐                       │
        │                     │ SAFETY / CONFIDENCE   │                       │
        │                     └───────────┬───────────┘                       │
        │              ┌──────────────────┴──────────────────┐                │
        │              ▼                                     ▼                │
        │   ┌─────────────────────┐             ┌─────────────────────────┐   │
        │   │ SAFE / APPROVED     │             │ SCIENTIST GATE          │   │
        │   │ (info/advisory)     │             │ (approve/correct/       │   │
        │   └─────────────────────┘             │  escalate)              │   │
        │              └──────────────────┬─────────────────┘                │
        │                                 ▼                                   │
        │                     ┌───────────────────────┐                       │
        │                     │ LOCKED OUTPUT         │                       │
        │                     │ voice+screen+print+QR │                       │
        │                     └───────────┬───────────┘                       │
        │                     ┌───────────────────────┐                       │
        │                     │ FOLLOW-UP → OUTCOME   │                       │
        │                     └───────────┬───────────┘                       │
        │                     ┌───────────────────────┐                       │
        │                     │ LEARNING SANDBOX      │                       │
        │                     │ (knowledge/rule/model │                       │
        │                     │  candidates + tests)  │                       │
        │                     └───────────┬───────────┘                       │
        │                     ┌───────────────────────┐                       │
        │                     │ VERSIONED RELEASE →   │                       │
        │                     │ EDGE SYNCHRONIZATION  │                       │
        │                     └───────────────────────┘                       │
        └─────────────────────────────────────────────────────────────────────┘
 EXTERNAL: IMD · PPQS/CIB&RC · BHASHINI · WhatsApp Business Cloud API ·
           Keycloak · Printer (hardware)
```

## 3. Logical architecture (C4 Level 2) — 26 services

See [02-modules.md](02-modules.md) for full per-module context. Summary:

| # | Service | Layer | Responsibility |
|---|---|---|---|
| S1 | **channel-adapter-kiosk** | Edge | Flutter kiosk app: voice capture, touch flow, text input, camera, print, TTS playback |
| S2 | **channel-adapter-whatsapp** | Central | WhatsApp Cloud API webhook in/out; media download; message → case mapping |
| S3 | **channel-adapter-web** | Central | Web/mobile PWA: chat, photo upload, case lookup by QR/short code |
| S4 | **input-orchestrator** | Core | Routes all inputs (text/audio/image/metadata) to the right processors; owns session state |
| S5 | **speech-service** | Core | ASR (Vaani-Whisper → SraVaani → BHASHINI), TTS (Piper → BHASHINI), audio quality, agri-vocabulary normalization |
| S6 | **image-service** | Core | Image quality checks, structured visual observations (VLM + classifier), media-set management |
| S7 | **case-service** | Core | Canonical case graph (CST): all node types; contradiction detection |
| S8 | **retrieval-service** | Core | Hybrid retrieval: SQL + BM25/FTS + pgvector (BGE-M3) + reranker; evidence ranking |
| S9 | **rules-service** | Core | Deterministic policy: regulatory, crop/target, formulation, dose, method, weather window, PHI/PPE, confidence gates |
| S10 | **llm-service** | Core | Local LLM inference (Ollama), structured output, prompt-policy versioning, shadow runner |
| S11 | **advisory-service** | Core | Composes evidence + rules + LLM draft into grounded advisory/prescription drafts |
| S12 | **prescription-service** | Core | Locked prescription object, print job, QR generation, verification endpoint |
| S13 | **review-service** | Core | Scientist review queue; approve/correct/escalate; context snapshot; decision-delta creation |
| S14 | **learning-service** | Core | Correction classifier; candidate generation; provenance ledger; sandbox orchestration |
| S15 | **outcome-service** | Core | Follow-up scheduling, outcome capture, failure protocol |
| S16 | **escalation-service** | Core | Escalation engine L0–L4, assignment, status workflow, handoff packets |
| S17 | **weather-service** | Core | IMD ingestion (central), normalization, local cache (edge), staleness, spray-window input |
| S18 | **knowledge-service** | Core | KB ingestion, normalization, expert review, versioning, edge bundle publishing, evidence ledger |
| S19 | **sync-agent** | Edge/central | Encrypted, idempotent, resumable sync: events up, bundles down; media queue |
| S20 | **device-agent** | Edge | Health, temperature, printer status, disk, network, graceful shutdown, signed updates |
| S21 | **scientist-portal** | Central UI | React PWA: review queue, correction UX, multimodal feedback, candidate approval, dashboards |
| S22 | **admin-console** | Central UI | React PWA: device management, releases, users/roles, audit views |
| S23 | **identity (Keycloak)** | Central | OIDC; roles: farmer (pseudonymous), operator, scientist, admin, auditor |
| S24 | **analytics** | Central | PostgreSQL + Metabase dashboards (ops, surveillance, AI quality, safety, learning, devices) |
| S25 | **observability** | Cross-cutting | OpenTelemetry; Prometheus + Grafana + Loki |
| S26 | **mlops-service** | Central | MLflow registry, DVC datasets, eval runners, shadow/canary, rollback |

## 4. Edge (kiosk) deployment

```text
┌────────────────────────────────────────────────────────────────────┐
│ KIOSK DEVICE (industrial mini-PC + GPU, or Jetson AGX Orin)       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ kiosk-ui (Flutter) — voice · touch · text · camera · TTS ·  │  │
│  │ print UI                                                    │  │
│  └──────────────┬───────────────────────────────────────────────┘  │
│                 │ local API (localhost)                            │
│  ┌──────────────▼───────────────────────────────────────────────┐  │
│  │ core-api (FastAPI) — runs the full decision pipeline locally │  │
│  │  input-orchestrator · case-service · retrieval-service       │  │
│  │  rules-service · llm-service · advisory-service              │  │
│  │  prescription-service · weather-cache · sync-agent           │  │
│  └──┬──────┬──────┬──────┬──────┬───────────────────────────────┘  │
│  ┌──▼───┐ ┌▼─────┐ ┌▼────┐ ┌▼────────┐ ┌▼──────────────────────┐   │
│  │Ollama│ │faster│ │Piper│ │Postgres │ │EMQX (local) MQTT      │   │
│  │LLM   │ │-whis-│ │TTS  │ │+pgvec   │ │broker                 │   │
│  │Gemma │ │per + │ │Telu-│ │local DB │ │                       │   │
│  │3 12B/│ │VLM   │ │gu   │ │+ KB     │ │                       │   │
│  │Llama │ │obs   │ │     │ │cache    │ │                       │   │
│  └──────┘ └──────┘ └─────┘ └─────────┘ └───────────────────────┘   │
│  Hardware: touchscreen · mic array · speaker · camera · thermal   │
│  printer (ESC/POS) · UPS · Ethernet + Wi-Fi + 4G fallback         │
└────────────────────────────────────────────────────────────────────┘
                 │  TLS + device certificate (MQTT/HTTPS, mTLS)
                 ▼
┌────────────────────────────────────────────────────────────────────┐
│ CENTRAL PLATFORM (K3s cluster or VMs)                              │
│  channel adapters (WhatsApp/web) · scientist portal · admin console│
│  Keycloak · Postgres (system of record) · MLflow · Metabase        │
│  weather ingestion (IMD) · knowledge publishing · model registry   │
│  Prometheus/Grafana/Loki · EMQX (central) · object storage (media) │
└────────────────────────────────────────────────────────────────────┘
```

**Edge rules:**
- The edge runs the *complete* decision pipeline for cached knowledge; it never phones home for a basic answer.
- Live weather is a central concern; the edge keeps the last known snapshot and marks it **STALE** after the policy window (default: 6 h forecast, 2 h nowcast).
- Scientist review of prescriptions: **queued** on the edge when offline and pushed on reconnect. Offline mode prints only information/advisory outputs, or holds the prescription in "pending approval" per institutional policy (open question D1).
- All edge state is encrypted at rest (LUKS); sync is idempotent (event IDs + sequence numbers).

## 5. Central platform deployment

```text
Internet
   │
[Reverse proxy: Caddy — TLS termination, WAF]
   │
   ├── scientist-portal (React PWA)
   ├── admin-console (React PWA)
   ├── web channel adapter (PWA + API)
   ├── whatsapp adapter (webhook in/out)
   │
[Core API gateway: FastAPI — OIDC-protected]
   │
   ├── case-service · retrieval-service · rules-service
   ├── advisory-service · prescription-service · review-service
   ├── learning-service · outcome-service · escalation-service
   ├── knowledge-service · weather-service · mlops-service
   │
[Data tier]
   ├── PostgreSQL 17 + pgvector (system of record + vectors)
   ├── Redis 7 (cache, queues, rate limits)
   ├── Object storage (MinIO) — media, KB bundles, model artifacts
   ├── EMQX 5 (MQTT: device sync, telemetry)
   │
[Identity & ops]
   ├── Keycloak 26 (OIDC)
   ├── Prometheus + Grafana + Loki (observability)
   ├── MLflow 3 + DVC (model/dataset registry)
   ├── Metabase (analytics dashboards)
   │
[Batch/async]
   ├── Weather ingestion worker (IMD, every 15–60 min)
   ├── KB re-index worker · evaluation runner · sync compactor
   └── (GPU node, on-demand): fine-tuning (Unsloth/axolotl), VLM training
```

## 6. Data architecture

| Store | Contents | Location |
|---|---|---|
| **PostgreSQL (central)** | System of record: cases, decisions, corrections, outcomes, escalations, evidence ledger, learning records, version registry, users, audit | Central |
| **PostgreSQL (edge)** | Local copy: active cases, KB cache (structured + vectors), rules, weather cache, event queue, print jobs | Edge |
| **pgvector** | BGE-M3 dense vectors (KB passages, case embeddings for similarity) | Both |
| **MinIO (central)** | Media (photos/audio), KB edge bundles (signed), model artifacts, backups | Central |
| **Redis** | Session state, rate limits, job queues | Central (+ edge for local jobs) |
| **MLflow + DVC** | Model registry, experiment tracking, dataset versions | Central |

**Data flow invariants:**
1. Edge → central: append-only events (inputs, decisions, corrections, outcomes, telemetry), idempotent by event ID.
2. Central → edge: signed, versioned bundles (knowledge, rules, models, prompt policies, lexicon, weather baseline).
3. The central DB is the **only** place learning candidates are promoted; the edge never mutates production artifacts.
4. Media is stored with case references; PII minimization applies (faces blurred by default in stored media unless a scientist explicitly requests the original for diagnosis — policy decision, roadmap §14.6).

## 7. Input modality architecture (voice / touch / text / picture)

All modalities converge on the **input-orchestrator** (S4), which attaches each input
to a `case_id` and produces an immutable `Input` node plus a candidate
`Interpretation` node.

```text
 VOICE ──► speech-service ──► transcript + confidence ─┐
                                                       │
 TOUCH ─► kiosk-ui structured events ──────────────────┤
          (crop/stage/pest pickers, buttons,           │
           confirmations, prescription display)        ▼
 TEXT ───► text normalizer ──────────────────────────► INPUT ORCHESTRATOR
          (Telugu script/Latin, local-term            │
           dictionary, entity extraction)              ▼
                                                       CASE SERVICE (CST)
 PICTURE ► image-service ─────────────────────────────┘
          (quality check → structured observations →
           candidate hypotheses; media-set tracking)
```

- **Voice:** VAD (silero-vad) → ffmpeg 16 kHz mono → ASR engine selection
  (Vaani-Whisper primary → SraVaani fast → BHASHINI online cross-check) →
  agri-vocabulary normalization → entity extraction → confidence assessment →
  confirmation gate when < θ_confirm (0.80). Details: roadmap §9.1.
- **Touch:** typed events `{picker, value, confidence: 1.0, ts}`; highest-confidence
  entity source; resolves ASR ambiguity directly. Details: roadmap §9.2.
- **Text:** script detection → lexicon pass → number/unit normalization → entity
  extraction (same NER as voice path — modality-agnostic). Details: roadmap §9.3.
- **Picture:** quality check (concrete retry instruction if unusable) → VLM
  structured observations (OBSERVED/POSSIBLE/UNCERTAIN/CONTRADICTORY/NOT_VISIBLE) →
  ViT classifier (class + probability) → candidate hypotheses → conflict check vs
  text/voice interpretation. Details: roadmap §9.4.

## 8. Security architecture

- **Identity:** Keycloak OIDC. Roles: `farmer` (pseudonymous, no account at kiosk), `operator`, `scientist`, `admin`, `auditor`. Farmer identity is a pseudonymous `farmer_ref` (opt-in phone/QR), never a name.
- **Device identity:** each kiosk has a TLS client certificate (mTLS) for sync; device registry in central DB.
- **Transport:** TLS 1.3 everywhere (reverse proxy + mTLS for device sync).
- **At rest:** LUKS full-disk encryption on edge; Postgres encryption; MinIO server-side encryption.
- **Artifacts:** signed updates (minisign/cosign) for app, models, KB bundles, rules; edge verifies signatures before activation.
- **Least privilege:** kiosk runs under a dedicated non-admin OS account; unnecessary services/ports disabled; security logs separated from farmer analytics.
- **LLM safety:** prompt-injection defenses (input sanitization, system-prompt hardening, output schema validation, red-team suite in CI); LLM never receives raw regulatory data as "instructions" — regulatory data is consumed by the rules engine only.
- **Privacy:** DPDP Act 2023 compliance program (roadmap §14); consent capture at first interaction; retention schedule; no automatic training on farmer conversations.

Full detail: [07-security-privacy.md](07-security-privacy.md).

## 9. Channel integration

```text
                 ┌── KIOSK (Flutter app, local core)
                 ├── WHATSAPP (Cloud API adapter: text/voice/photo)
                 ├── WEB / MOBILE (PWA: chat/photo/QR case lookup)
                 ├── CALL-CENTRE / OPERATOR (future: telephony adapter)
                 └── FUTURE CHANNEL (any adapter → canonical case API)
                        │
                        ▼
                 CANONICAL CASE API (case-service)
                        │
                        ▼
              CASE-TO-SOLUTION TREE (one case, all channels)
```

- A durable `case_id` (ULID) + short code (e.g. `BNV-4F7K2`) + QR enables: kiosk →
  WhatsApp continuation; WhatsApp → scientist; printed output → follow-up reopen;
  field worker → full history.
- Channel adapters are thin: they translate channel messages to canonical `Input`
  events and render canonical outputs (text/voice/card) back. **No business logic in
  adapters.**

## 10. Observability architecture

- **OpenTelemetry** SDK in every service: traces (question → ASR → retrieval → rules → LLM → gate → output), metrics, structured logs.
- **Prometheus** (metrics) + **Grafana** (dashboards) + **Loki** (logs) on central; edge ships telemetry via MQTT with local buffering.
- Every LLM call, retrieval, rule evaluation and gate decision is a span with input hashes + version tuple → full reproducibility of any production answer.
- Key metric catalog: [08-operations.md](08-operations.md) §4.

## 11. Service interaction map

```text
CHANNELS                EDGE (per kiosk)                          CENTRAL (K3s)
────────                ──────────────────                        ─────────────
S1 kiosk-ui ──localhost──► S4 input-orchestrator ◄── S2 whatsapp adapter
S3 web PWA ──────────────────────────────────────────────────────► S4 (via API gateway)
                              │  audio→S5  image→S6  text→normalizer  touch→S7
                              ▼
                         S7 case-service (CST, state machine, contradictions)
                              │
        ┌──────────┬──────────┼──────────┬───────────┐
        ▼          ▼          ▼          ▼           ▼
     S8 retrieval S9 rules   S10 llm   S17 weather S12 prescription
        └──────────┴────┬─────┴──────────┴───────────┘
                        ▼
                  S11 advisory-service (draft + gates)
                        │
              ┌─────────┴──────────┐
              ▼                    ▼
        S12 locked output      S13 review-service (scientist gate)
              │                    │  snapshot + delta
              ▼                    ▼
        S15 outcome ◄────── S16 escalation
              │                    │
              └────────┬───────────┘
                       ▼
                 S14 learning-service ──► S18 knowledge / S9 rules / S26 mlops
                       │
                       ▼
        S19 sync-agent ◄──► S20 device-agent (MQTT) ──► S22 admin / S24 analytics / S25 observability
```
