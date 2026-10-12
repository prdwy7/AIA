# AI-ENABLED AGRICULTURAL ADVISORY KIOSK — COMPLETE PROJECT ROADMAP

**Implementation Roadmap, Structured Frameworks, Tool Dependencies & Architecture — v2.0 (Multimodal Case-to-Solution Tree)**

| | |
|---|---|
| **Document version** | 1.0 |
| **Date** | 26 September 2026 |
| **Status** | Ready for implementation planning |
| **Source design document** | `AI_Kiosk_v2_Multimodal_Case_to_Solution.md` (v2.0, September 2026) |
| **Institution** | KVK Banavasi (ICAR / Acharya N.G. Ranga Agricultural University), Yemmiganur Mandal, Kurnool District, Andhra Pradesh |
| **Scope** | Full implementation roadmap: architecture, structured frameworks, tool dependencies, data model, API contracts, phased plan, team, hardware, testing, security, risks, KPIs |
| **Out of scope** | Pricing/financial estimates (per source document); camera-based autonomous prescription (image is evidence, never sole authority) |

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Solution Overview](#2-solution-overview)
3. [Architecture](#3-architecture)
4. [Structured Frameworks](#4-structured-frameworks)
5. [Technology Stack & Tool Dependencies](#5-technology-stack--tool-dependencies)
6. [Data Model](#6-data-model)
7. [API Contracts](#7-api-contracts)
8. [Service Decomposition](#8-service-decomposition)
9. [Input Modality Workstreams (Voice / Touch / Text / Picture)](#9-input-modality-workstreams)
10. [Phased Implementation Roadmap](#10-phased-implementation-roadmap)
11. [Team & Roles](#11-team--roles)
12. [Hardware & Infrastructure](#12-hardware--infrastructure)
13. [Testing & Evaluation Strategy](#13-testing--evaluation-strategy)
14. [Security, Privacy & Compliance](#14-security-privacy--compliance)
15. [Risk Register](#15-risk-register)
16. [KPIs & Success Metrics](#16-kpis--success-metrics)
17. [Operational Model](#17-operational-model)
18. [Appendices](#18-appendices)

---

# 1. EXECUTIVE SUMMARY

## 1.1 What we are building

A **governed, offline-first, multimodal agricultural decision-support platform** for KVK Banavasi. A farmer interacts with the system through **four first-class input modalities — voice, touch, text, and picture** — on a kiosk (and later WhatsApp/web). The system builds a persistent **Case-to-Solution Tree (CST)**: it interprets the input, cross-checks understanding with the farmer, maintains competing hypotheses with evidence, asks targeted verification questions, retrieves authoritative evidence, applies deterministic regulatory/agronomic/weather rules, drafts a grounded answer with a local LLM, and routes high-risk outputs through a **scientist gate** before any prescription is printed or delivered.

Every decision is captured with a **full context snapshot** (input, evidence, rules, weather, model/knowledge/rule versions). When a scientist corrects an AI recommendation, the scientist changes **only the wrong fields**; the system automatically attaches the complete background state and converts the record into a **decision delta** that is classified and routed to one of three governed learning channels (knowledge, rules, training data) or retained as case memory. Nothing changes production without **validation, regression testing, expert approval, versioning, and a rollback path**. A closed-loop **outcome layer** tracks whether advice actually worked, and failed cases trigger reassessment and escalation — never automatic re-prescription.

## 1.2 Non-negotiable design principles

| # | Principle |
|---|-----------|
| 1 | **The LLM is not the authority.** LLM = language/reasoning assistant. Knowledge base = evidence. Rules engine = safety gate. Scientist = authority. Prescription service = controlled output. |
| 2 | **No uncontrolled self-modification.** Corrections are learning signals, not instructions to rewrite production. All production changes pass validation + approval + versioning. |
| 3 | **Deterministic safety.** Regulatory, dose, PHI/PPE and weather-window constraints live in a testable rules engine — never only in model weights. |
| 4 | **Reproducibility.** Every prescription traces to the exact version tuple (model + knowledge + rules + prompt policy + speech + schema) that produced it. |
| 5 | **Clarification over forced certainty.** Ambiguity produces confirmation questions and competing hypotheses, never silent guesses. |
| 6 | **Offline-first.** Core service (information, basic AI, rules, printing) works without network; sync is encrypted, idempotent, resumable. |
| 7 | **Channel-agnostic intelligence.** Kiosk, WhatsApp, web and operator channels are adapters into one canonical case service; a case can move between channels without losing context. |
| 8 | **Outcome-aware learning.** The system learns from the full case lifecycle — meaning, misunderstanding, evidence, decision, correction, action, outcome, escalation — not only from corrections. |
| 9 | **Privacy by design.** Minimal PII, consent-aware collection (DPDP Act 2023), no automatic use of farmer conversations for training. |

## 1.3 Input modalities (first-class)

| Modality | Kiosk | WhatsApp | Web/Mobile | Scientist portal |
|---|---|---|---|---|
| **Voice** | Telugu/English ASR via mic array; TTS answers | Voice notes (ASR) | Voice input (optional) | Voice feedback → structured correction |
| **Touch** | Large-button guided flow, crop/stage/pest pickers, confirmation gates | Tap-to-select quick replies | Touch/click UI | Approve / Correct / Escalate buttons |
| **Text** | On-screen keyboard (Telugu + Latin), local-term dictionary | Text messages | Chat text | Text notes, structured fields |
| **Picture** | Camera capture (whole plant, leaf, pest close-up, field context) | Photo upload (multiple) | Photo upload | Reference/annotated images |

All four modalities map to the **same canonical case object** (`case_id`), so a farmer can start by voice at the kiosk, send a photo on WhatsApp, and have the scientist review the complete tree on the web portal.

## 1.4 Delivery at a glance

| Item | Value |
|---|---|
| Total duration | **18 months** (5 waves, 16 phases) |
| Supervised trial | 3 months (Wave 4), scientist reviews every prescription |
| Peak team | 14–16 FTE (see §11) |
| Production target | 1 kiosk (KVK Banavasi) → district scale architecture ready |
| Core stack | Python/FastAPI · PostgreSQL 17 + pgvector · Ollama (Gemma 3 12B / Llama 3.1 8B) · Vaani-Whisper + SraVaani + Piper (Telugu) · BGE-M3 retrieval · Flutter kiosk · Keycloak · MQTT · OpenTelemetry · Docker/K3s |
| Key external dependencies | IMD weather API (IP whitelist), PPQS/CIB&RC regulatory data, BHASHINI speech APIs (online mode), WhatsApp Business Cloud API (Meta/BSP) |

## 1.5 Wave overview

| Wave | Months | Calendar (start Oct 2026) | Phases | Theme |
|---|---|---|---|---|
| **W1 — Foundation** | M1–M3 | Oct–Dec 2026 | 0, 1 (+ knowledge/rules/kiosk MVP workstreams) | Governance, canonical schema, platform skeleton, kiosk MVP (touch+text+print), KB v1, rules v1 |
| **W2 — Intelligence** | M3–M8 | Dec 2026–May 2027 | 2, 3, 4, 5, 6, 7, 8 (+ AI/RAG, voice) | Channels, Case-to-Solution Tree, cross-correction, image pipeline, verification, similar cases, scientist multimodal feedback |
| **W3 — Closed loop** | M7–M10 | Apr–Jul 2027 | 9, 10, 11, 12, 14 (foundation) | Outcome/follow-up, escalation, learning sandbox, offline media sync, MLOps foundation |
| **W4 — Trial** | M10–M13 | Jul–Oct 2027 | 13 | Three-month scientist-supervised trial |
| **W5 — Production & scale** | M13–M18 | Oct 2027–Mar 2028 | 14 (hardening), 15 | MLOps/KnowledgeOps hardening, multi-kiosk, multi-channel scale |

---

# 2. SOLUTION OVERVIEW

## 2.1 Institutional context

- **KVK Banavasi** (established 31 Oct 2010) is an ICAR Krishi Vigyan Kendra hosted by **Acharya N.G. Ranga Agricultural University (ANGRAU)**, Hyderabad, located at Banavasi village, Yemmiganur Mandal, **Kurnool district, Andhra Pradesh** (~75 km from Kurnool, on the Kurnool–Adoni road).
- KVKs are the ICAR extension network for technology transfer, farmer training, demonstrations and advisory services. The kiosk extends the KVK's advisory reach beyond office hours and beyond the KVK premises.
- **Dominant crops in the Kurnool/Yemmiganur region** (from local mandi and extension data): cotton, paddy, groundnut, maize, arhar (red gram), castor, foxtail/barnyard millet, chilli, and horticulture. The knowledge base v1 must cover these first; the architecture must support crop expansion.
- **Language**: Telugu-first (Kurnool is a Telugu-speaking district), with English as secondary. Farmer vocabulary is often local/dialectal — a governed local terminology dictionary is required (§4.9, §9.3).
- **Connectivity**: rural, intermittent. Offline-first is a hard requirement, not a preference.

## 2.2 Problem statement (from source design, P1–P10)

| ID | Problem | Required solution |
|---|---|---|
| P1 | Farmer input is ambiguous or incomplete | Structured case builder + clarification questions |
| P2 | LLM can generate plausible but incorrect recommendations | LLM cannot be final prescription authority |
| P3 | A scientist correction may be small but its context is large | Automatic full-context snapshot |
| P4 | Agricultural guidance changes over time | Versioned knowledge with effective dates |
| P5 | Regulatory restrictions cannot safely live only in model weights | Deterministic regulatory/policy layer |
| P6 | Weather affects application suitability | Weather-aware rule engine |
| P7 | Expert preference is not necessarily universal truth | Correction classification + evidence status |
| P8 | Immediate self-training can destabilize production | Learning sandbox + approval gate |
| P9 | Rural connectivity can be intermittent | Local-first execution + synchronization |
| P10 | Future kiosks need one consistent architecture | Canonical schemas + version registry |

## 2.3 Users & personas

| Persona | Needs | Primary channels |
|---|---|---|
| **Farmer** (diverse literacy, Telugu-speaking) | Fast, simple, voice-friendly answers; printed prescription; no repeated questions | Kiosk (voice/touch/text/picture), WhatsApp |
| **KVK Scientist** (final authority during trial) | Minimal-effort correction; full context auto-attached; review queue; voice/text/image feedback | Scientist portal (web), WhatsApp |
| **Kiosk Operator** | Device health, printer status, session reset, basic troubleshooting | Kiosk admin screen |
| **Platform Administrator** | Device management, knowledge/rule/model releases, user roles | Admin console |
| **Auditor** | Read-only trace of any prescription to versions, evidence, approvals | Audit console |
| **Institutional reviewer** (KVK/ANGRAU/ICAR) | Trial metrics, safety incidents, learning outcomes | Dashboards + reports |

## 2.4 Output classes & risk tiers

| Class | Example | Control |
|---|---|---|
| **Information** (low risk) | Explain a pest lifecycle | Grounded evidence; may answer directly |
| **Diagnosis support** (medium risk) | Possible pest/disease candidates | Evidence + confidence + minimal cross-check + at least one targeted question |
| **Advisory** (medium-high risk) | Management options | Knowledge + rules + confirmation gate |
| **Prescription** (high risk) | Specific product/formulation/dose/timing/PHI/PPE | Full safety pipeline + regulatory check + weather check + **scientist approval** + locked output + print/QR |

**v2 rule:** an apparently obvious solution is still a hypothesis until its required verification gates are satisfied.

## 2.5 Core requirements (traceability to source proposal)

| Requirement | v2 design response |
|---|---|
| Telugu/English voice | Telugu-first ASR/TTS with confidence handling and confirmation of critical entities (§9.1) |
| Scientific recommendations | Hybrid retrieval + deterministic rules + scientist workflow |
| Prescription | Structured prescription object → print + QR |
| Weather | IMD snapshot + explicit spray-window rules (GREEN/CAUTION/BLOCKED/UNKNOWN) |
| Offline | Local AI/knowledge/rules + encrypted sync queue |
| Surveillance | Structured crop/pest/location events + privacy-aware analytics |
| Expert validation | Three-month supervised correction loop |
| Pilot refinement | Formal learning sandbox + versioned releases |
| Multimodal input | Voice + touch + text + picture as first-class inputs (§9) |
| Case continuity | Durable `case_id`, QR/short code, cross-channel continuation |
| Outcome loop | Follow-up, worked/failed/uncertain outcomes, failed-solution protocol |

---

# 3. ARCHITECTURE

## 3.1 Architecture principles

1. **Single canonical case service.** All channels and modalities write to one case graph; no channel owns intelligence.
2. **Deterministic core, probabilistic edges.** Rules and safety are pure functions with tests; LLM output is always schema-validated before entering the pipeline.
3. **Append-only history.** Original inputs, interpretations, AI decisions and corrections are immutable; corrections create new nodes, never overwrites.
4. **Edge autonomy.** The kiosk runs the full decision pipeline locally (except live weather and new knowledge); the central platform is the system of record and the publishing authority.
5. **Everything versioned.** Model, knowledge, rules, prompt policy, speech assets and schema form a version tuple recorded on every prescription.
6. **Boring technology at the core.** PostgreSQL + Python + Docker; specialized AI components isolated behind service interfaces so models can be swapped without re-architecture.

## 3.2 System context (C4 Level 1)

```text
                         ┌─────────────────────────────────────────────┐
                         │                FARMER                       │
                         │  voice · touch · text · picture             │
                         └──────┬──────────────┬──────────────┬────────┘
                                │              │              │
                     ┌──────────▼───┐   ┌──────▼─────┐  ┌─────▼──────┐
                     │   KIOSK      │   │  WHATSAPP  │  │ WEB /      │
                     │ (KVK site)   │   │ (Cloud API)│  │ MOBILE     │
                     └──────────┬───┘   └──────┬─────┘  └─────┬──────┘
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
        │          │               │              │              │            │
        │          ▼               ▼              ▼              ▼            │
        │   ┌────────────┐  ┌────────────┐ ┌────────────┐ ┌────────────┐     │
        │   │ KNOWLEDGE  │  │   RULES    │ │  WEATHER   │ │  SIMILAR   │     │
        │   │ (RAG/KB)   │  │  ENGINE    │ │  CONTEXT   │ │  CASES     │     │
        │   └────────────┘  └────────────┘ └────────────┘ └────────────┘     │
        │          │               │              │              │            │
        │          └───────────────┴──────┬───────┴──────────────┘            │
        │                                 ▼                                   │
        │                     ┌───────────────────────┐                       │
        │                     │  LOCAL LLM (draft)    │                       │
        │                     └───────────┬───────────┘                       │
        │                                 ▼                                   │
        │                     ┌───────────────────────┐                       │
        │                     │ SAFETY / CONFIDENCE   │                       │
        │                     └───────────┬───────────┘                       │
        │                                 ▼                                   │
        │              ┌──────────────────┴──────────────────┐                │
        │              ▼                                     ▼                │
        │   ┌─────────────────────┐             ┌─────────────────────────┐   │
        │   │ SAFE / APPROVED     │             │ SCIENTIST GATE          │   │
        │   │ (info/advisory)     │             │ (portal: approve/       │   │
        │   └──────────┬──────────┘             │  correct/escalate)      │   │
        │              │                        └───────────┬─────────────┘   │
        │              └──────────────────┬─────────────────┘                │
        │                                 ▼                                   │
        │                     ┌───────────────────────┐                       │
        │                     │ LOCKED OUTPUT         │                       │
        │                     │ voice+screen+print+QR │                       │
        │                     └───────────┬───────────┘                       │
        │                                 ▼                                   │
        │                     ┌───────────────────────┐                       │
        │                     │ FOLLOW-UP → OUTCOME   │                       │
        │                     └───────────┬───────────┘                       │
        │                                 ▼                                   │
        │                     ┌───────────────────────┐                       │
        │                     │ LEARNING SANDBOX      │                       │
        │                     │ (knowledge/rule/model │                       │
        │                     │  candidates + tests)  │                       │
        │                     └───────────┬───────────┘                       │
        │                                 ▼                                   │
        │                     ┌───────────────────────┐                       │
        │                     │ VERSIONED RELEASE →   │                       │
        │                     │ EDGE SYNCHRONIZATION  │                       │
        │                     └───────────────────────┘                       │
        └─────────────────────────────────────────────────────────────────────┘

 EXTERNAL SYSTEMS:
   IMD (weather/agromet) · PPQS/CIB&RC (regulatory data) · BHASHINI (online speech)
   WhatsApp Business Cloud API (Meta) · Keycloak (identity) · Printer (hardware)
```

## 3.3 Logical architecture (C4 Level 2) — services

| # | Service | Layer | Responsibility |
|---|---|---|---|
| S1 | **channel-adapter-kiosk** | Edge | Flutter kiosk app: voice capture, touch flow, text input, camera, print, TTS playback |
| S2 | **channel-adapter-whatsapp** | Central | WhatsApp Cloud API webhook in/out; media download; message → case mapping |
| S3 | **channel-adapter-web** | Central | Web/mobile PWA: chat, photo upload, case lookup by QR/short code |
| S4 | **input-orchestrator** | Core | Routes all inputs (text/audio/image/metadata) to the right processors; owns session state |
| S5 | **speech-service** | Core | ASR (Whisper/IndicWav2Vec/BHASHINI), TTS (Piper/BHASHINI), audio quality checks, agricultural vocabulary normalization |
| S6 | **image-service** | Core | Image quality checks, structured visual observations (VLM + specialized classifier), media-set management |
| S7 | **case-service** | Core | Canonical case graph (CST): inputs, interpretations, corrections, hypotheses, questions, answers, evidence, decisions, outcomes, escalations; contradiction detection |
| S8 | **retrieval-service** | Core | Hybrid retrieval: structured SQL + keyword (FTS/BM25) + vector (pgvector/BGE-M3) + reranker; evidence ranking by authority/freshness/relevance |
| S9 | **rules-service** | Core | Deterministic policy package: regulatory, crop/target, formulation, dose, method, weather window, PHI/PPE/environment, confidence gates |
| S10 | **llm-service** | Core | Local LLM inference (Ollama), structured output (JSON schema) generation, prompt-policy versioning, shadow-model runner |
| S11 | **advisory-service** | Core | Composes evidence + rules + LLM draft into grounded advisory/prescription drafts; evidence-ID retention |
| S12 | **prescription-service** | Core | Locked prescription object, print job, QR generation, verification endpoint |
| S13 | **review-service** | Core | Scientist review queue; approve/correct/escalate; automatic context snapshot; decision-delta creation |
| S14 | **learning-service** | Core | Correction classifier; candidate generation (knowledge/rule/training); provenance ledger; learning sandbox orchestration |
| S15 | **outcome-service** | Core | Follow-up scheduling (protocol-based), outcome capture (worked/partial/failed/worsened/unknown), failure protocol |
| S16 | **escalation-service** | Core | Escalation engine L0–L4, assignment, status workflow, human-handoff packets |
| S17 | **weather-service** | Core | IMD ingestion (central), normalization, local cache (edge), staleness handling, spray-window evaluation input |
| S18 | **knowledge-service** | Core | KB ingestion, normalization, expert review workflow, versioning, edge bundle publishing, evidence ledger |
| S19 | **sync-agent** | Edge/central | Encrypted, idempotent, resumable sync: events up, knowledge/rules/model versions down; media queue |
| S20 | **device-agent** | Edge | Health, temperature, printer status, disk, network, graceful shutdown, signed update verification |
| S21 | **scientist-portal** | Central UI | React PWA: review queue, correction UX (minimal fields), voice/text/image feedback, candidate approval, dashboards |
| S22 | **admin-console** | Central UI | Device management, releases, users/roles, audit views |
| S23 | **identity (Keycloak)** | Central | OIDC authn/z; roles: farmer (anonymous/pseudonymous), operator, scientist, admin, auditor |
| S24 | **analytics** | Central | PostgreSQL + Metabase dashboards (operations, pest surveillance, AI quality, safety, learning, devices) |
| S25 | **observability** | Cross-cutting | OpenTelemetry traces/metrics/logs; Prometheus + Grafana + Loki |
| S26 | **mlops-service** | Central | MLflow registry, dataset versioning (DVC), evaluation runners (RAGAS/DeepEval/promptfoo), shadow/canary orchestration, rollback |

## 3.4 Edge (kiosk) deployment

```text
┌────────────────────────────────────────────────────────────────────┐
│ KIOSK DEVICE (industrial mini-PC + GPU, or Jetson AGX Orin)       │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ kiosk-ui (Flutter)                                           │  │
│  │  voice · touch · text · camera · TTS playback · print UI     │  │
│  └──────────────┬───────────────────────────────────────────────┘  │
│                 │ local API (localhost)                            │
│  ┌──────────────▼───────────────────────────────────────────────┐  │
│  │ core-api (FastAPI) — runs the full decision pipeline locally │  │
│  │  input-orchestrator · case-service · retrieval-service       │  │
│  │  rules-service · llm-service · advisory-service              │  │
│  │  prescription-service · weather-cache · sync-agent           │  │
│  └──┬──────────┬──────────┬──────────┬──────────┬───────────────┘  │
│     │          │          │          │          │                  │
│  ┌──▼───┐  ┌───▼────┐ ┌───▼────┐ ┌───▼────┐ ┌───▼──────────────┐  │
│  │Ollama│  │faster- │  │Piper  │  │Postgres│  │EMQX (local)     │  │
│  │LLM   │  │whisper │  │TTS    │  │+pgvec  │  │MQTT broker      │  │
│  │(Gemma│  │ASR +   │  │(Telugu│  │(local  │  │                 │  │
│  │3 12B/│  │VLM obs │  │voice) │  │DB + KB │  │                 │  │
│  │Llama)│  │extract)│  │       │  │cache)  │  │                 │  │
│  └──────┘  └────────┘  └───────┘  └────────┘  └─────────────────┘  │
│                                                                    │
│  Hardware: touchscreen · mic array · speaker · camera · thermal   │
│  printer (ESC/POS) · UPS · Ethernet + Wi-Fi + 4G fallback         │
└────────────────────────────────────────────────────────────────────┘
                 │  TLS + device certificate (MQTT/HTTPS)
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
- Live weather is a central concern; the edge keeps the last known snapshot and marks it **STALE** after a policy-defined window (default: 6 h for forecast, 2 h for nowcast).
- Scientist review of prescriptions: **queued** on the edge when offline and pushed on reconnect (policy: prescription cannot be printed until approved — offline mode prints only information/advisory outputs, or holds the prescription in a "pending approval" state per institutional policy).
- All edge state is encrypted at rest; sync is idempotent (event IDs + sequence numbers).

## 3.5 Central platform deployment

```text
Internet
   │
[Reverse proxy: Caddy/Traefik — TLS termination, WAF]
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

## 3.6 Data architecture

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
4. Media is stored with case references; PII minimization applies (faces blurred by default in stored media unless a scientist explicitly requests the original for diagnosis — policy decision, §14).

## 3.7 Input modality architecture (voice / touch / text / picture)

All modalities converge on the **input-orchestrator**, which attaches each input to a `case_id` and produces an `Input` node (immutable) plus a candidate `Interpretation` node.

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

Details per modality: §9.

## 3.8 Security architecture

- **Identity**: Keycloak OIDC. Roles: `farmer` (pseudonymous, no account needed at kiosk), `operator`, `scientist`, `admin`, `auditor`. Farmer identity is a pseudonymous `farmer_ref` (opt-in phone/QR), never a name.
- **Device identity**: each kiosk has a TLS client certificate (mTLS) for sync; device registry in central DB.
- **Transport**: TLS 1.3 everywhere (reverse proxy + mTLS for device sync).
- **At rest**: LUKS full-disk encryption on edge; Postgres encryption; MinIO server-side encryption.
- **Artifacts**: signed updates (minisign/cosign) for app, models, KB bundles, rules; edge verifies signatures before activation.
- **Least privilege**: kiosk runs under a dedicated non-admin OS account; unnecessary services/ports disabled; security logs separated from farmer analytics.
- **LLM safety**: prompt-injection defenses (input sanitization, system-prompt hardening, output schema validation, red-team suite in CI); LLM never receives raw regulatory data as "instructions" — regulatory data is consumed by the rules engine only.
- **Privacy**: DPDP Act 2023 compliance program (§14); consent capture at first interaction; retention schedule; no automatic training on farmer conversations.

## 3.9 Channel integration

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

- A durable `case_id` (e.g., `CASE-2026-00018372`) + short code + QR enables: kiosk → WhatsApp continuation; WhatsApp → scientist; printed output → follow-up reopen; field worker → full history.
- Channel adapters are thin: they translate channel messages to canonical `Input` events and render canonical outputs (text/voice/card) back. No business logic in adapters.

## 3.10 Observability architecture

- **OpenTelemetry** SDK in every service: traces (question → ASR → retrieval → rules → LLM → gate → output), metrics, structured logs.
- **Prometheus** (metrics) + **Grafana** (dashboards) + **Loki** (logs) on central; edge ships telemetry via MQTT with local buffering.
- Key metric catalog: §16.3.
- Every LLM call, retrieval, rule evaluation and gate decision is a span with input hashes + version tuple → full reproducibility of any production answer.

---

# 4. STRUCTURED FRAMEWORKS

This section defines the reusable, testable frameworks that govern the system. Each framework is a **specification artifact** (versioned document + machine-readable config where noted) that phases 0–15 build against.

## 4.1 Governance framework

### 4.1.1 Roles & authority

| Role | Authority | May do | May not do |
|---|---|---|---|
| **Farmer** | Subject of the case | Provide inputs, correct interpretations, report outcomes | — |
| **Operator** | Device | Reset session, check health, replace printer paper | Approve/correct prescriptions, change knowledge/rules |
| **Scientist (KVK)** | Final authority during trial | Approve/correct/escalate prescriptions; approve knowledge/rule candidates; provide multimodal feedback | Publish production artifacts directly (must go through release workflow) |
| **Knowledge owner** (designated scientist) | KB | Approve production knowledge versions | Change rules/models |
| **Rule owner** (designated scientist + engineer) | Rules | Approve production rule versions | Change KB/models |
| **Release authority** (institutional nominee) | Releases | Approve shadow→canary→production promotion; rollback | — |
| **Admin** | Platform | Users, devices, configuration | Approve agricultural content |
| **Auditor** | Read-only | Trace any artifact to provenance | Modify anything |

### 4.1.2 Approval matrix (learning governance)

| Artifact | AI may propose? | AI may publish? | Required approval |
|---|---|---|---|
| Training example | Yes | No | Quality/learning policy check |
| Knowledge candidate | Yes | No | Authorized agricultural expert |
| Rule candidate | Yes | No | Authorized scientist (+ rule owner) |
| Model candidate | Yes | No | Technical + agricultural review |
| Production knowledge | No | No | Knowledge owner |
| Production rule | No | No | Rule owner |
| Production model | No | No | Release authority |
| Prescription | Draft only | No | Scientist / institutional policy |

### 4.1.3 Expert preference vs expert correction

Every correction carries an **evidence status**: `EVIDENCE_BACKED` (cites authoritative source), `LOCALLY_VALIDATED` (region-specific, validated), or `EXPERT_PREFERENCE` (personal experience, no authoritative evidence). Only the first two can become production knowledge/rules; preferences are stored as preference records and may inform candidate generation but never auto-promote.

### 4.1.4 Governance artifacts (Phase 0 deliverables)

1. **Governance specification** (roles, authority, approval matrix, escalation policy, incident policy) — signed by KVK/ANGRAU.
2. **Safety policy**: risk tiers, blocking rules inventory, prohibited-output list, PHI/PPE defaults, weather-window policy.
3. **Data policy**: consent, retention, PII minimization, DPDP mapping, media handling.
4. **Source policy**: authoritative source hierarchy (§4.6).
5. **Trial protocol**: supervision level per month, metrics, exit criteria, institutional approval gates.

## 4.2 Case lifecycle framework (Case-to-Solution Tree)

### 4.2.1 Case states

```text
 OPEN
   │  (first input received: voice/touch/text/picture)
   ▼
 INTERPRETING ──► CLARIFYING ◄──────────────┐
   │  (interpretation + uncertainty record)  │ (contradiction / low confidence /
   ▼                                        │  missing critical field)
 HYPOTHESIZING ──────────────────────────────┘
   │  (competing hypotheses + evidence for/against)
   ▼
 EVIDENCE_GATHERING
   │  (retrieval + similar cases + targeted questions + media)
   ▼
 DECIDING
   │  (rules + LLM draft + safety/confidence gate)
   ▼
 REVIEW (scientist gate, when risk tier requires)
   │
   ├──────────────► ACTION (locked output: voice+screen+print+QR)
   │                    │
   │                    ▼
   │               FOLLOWUP (protocol-based follow-up window)
   │                    │
   │                    ▼
   │               OUTCOME (worked / partial / failed / worsened / unknown)
   │                    │
   │        ┌───────────┼──────────────┐
   │        ▼           ▼              ▼
   │     CLOSE     REASSESS       ESCALATE
   │                 │               │
   │                 └──► new branch (back to HYPOTHESIZING)
   │
   └──────────────► ESCALATE (L2–L4, human handoff)
```

### 4.2.2 State transition rules (machine-readable)

| From | To | Trigger | Guard |
|---|---|---|---|
| OPEN | INTERPRETING | First input stored | Input passes format/quality check |
| INTERPRETING | CLARIFYING | Confidence < θ_confirm (default 0.80) OR critical entity ambiguous OR contradiction detected | Clarification question has a decision purpose |
| INTERPRETING | HYPOTHESIZING | Confidence ≥ θ_confirm | — |
| CLARIFYING | HYPOTHESIZING | Farmer answer received | Answer updates interpretation (new node, original immutable) |
| HYPOTHESIZING | EVIDENCE_GATHERING | ≥1 hypothesis formed | — |
| EVIDENCE_GATHERING | DECIDING | Evidence sufficient OR max questions reached (default 3 per branch) | Do-not-repeat memory checked |
| DECIDING | REVIEW | Risk tier = prescription OR confidence < θ_auto (default 0.85) | All blocking rules evaluated |
| DECIDING | ACTION | Risk tier ≤ advisory AND gates pass | No blocking rule fired |
| REVIEW | ACTION | Scientist approves (optionally with correction) | Correction stored as decision delta |
| REVIEW | ESCALATE | Scientist escalates | Escalation level assigned |
| ACTION | FOLLOWUP | Output delivered | Follow-up window from approved protocol |
| FOLLOWUP | OUTCOME | Farmer/worker reports outcome | Media + context attached |
| OUTCOME | CLOSE | Worked/partial AND no escalation | Learning record created |
| OUTCOME | REASSESS | Failed/worsened/uncertain | Failure protocol: stop auto-repetition, request new evidence |
| REASSESS | HYPOTHESIZING | New evidence collected | Alternative hypotheses checked |
| any | ESCALATE | Escalation trigger fired (§4.4) | Escalation ID + status OPEN |

### 4.2.3 Invariants

1. Original farmer input and original system interpretation are **immutable**; corrections append new nodes.
2. Every question has a recorded **decision purpose** (which branch it resolves).
3. Every high-risk output retains **evidence IDs** end-to-end.
4. A case never silently changes crop/stage/problem — contradictions force a clarification branch.
5. Do-not-repeat memory: answered questions, received images, attempted treatments, made corrections are tracked per case.

## 4.3 Learning framework

### 4.3.1 Channels

| Channel | Input | Output artifact | Promotion gate |
|---|---|---|---|
| **Knowledge learning** | Corrections of type OUTDATED_KNOWLEDGE / DIAGNOSIS + verified sources | Knowledge candidate → KB version N+1 | Expert approval + re-index + regression |
| **Rule learning** | Repeated validated corrections (pattern discovery) | Candidate rule (IF/THEN + scope) | Counterexample search + scientist review + regression suite |
| **Model learning** | Approved feedback records (error classes appropriate for model learning) | Candidate model (fine-tune) | Safety + regression + expert eval + shadow + canary |
| **Case memory** | All cases + outcomes | Indexed case memory (similar-case service) | Controlled index update (automatic, with provenance) |
| **Language learning** | Farmer entity corrections | Lexicon mapping candidates | Expert validation (never silent overwrite) |

### 4.3.2 Correction classification (decision delta types)

| Type | Meaning | Learning target |
|---|---|---|
| PRODUCT_SELECTION | Wrong product | Knowledge/rule + training example |
| DOSAGE | Dose changed | Dose rule + training example |
| FORMULATION | Formulation changed | Product/formulation rule |
| TIMING | Timing changed | Weather/stage rule |
| DIAGNOSIS | Problem identification changed | Diagnostic knowledge/model data |
| MISSING_CONTEXT | Critical info absent | Clarification policy |
| OUTDATED_KNOWLEDGE | Source changed | Knowledge version |
| LOCAL_CONDITION | Locally validated exception | Region-specific candidate rule |
| EXPERT_PREFERENCE | Preference without authoritative evidence | Preference record only |
| EXPLANATION | Decision correct, explanation poor | Language-model evaluation data |

### 4.3.3 Provenance requirements (every learning signal must answer)

Who provided it? · What did they observe? · When? · Through which channel? · What evidence did they provide? · What did the AI originally say? · What was corrected? · Was it independently verified? · Did the farmer outcome support the correction? · Was it approved for learning? · Which production version used it?

### 4.3.4 Pattern discovery (rule learning trigger)

```text
VALIDATED CORRECTIONS
  → group by crop / stage / problem / region / season
  → compare AI vs scientist choices
  → frequency + consistency analysis (min support: N≥5, consistency ≥80% — tunable)
  → counterexample search (must find zero blocking counterexamples)
  → candidate pattern (STATUS = CANDIDATE, never PRODUCTION)
  → scientist review → rule candidate → regression → release
```

## 4.4 Escalation framework

| Level | Meaning | Trigger examples | Response SLA (target) |
|---|---|---|---|
| **L0** | Normal automated information | — | immediate |
| **L1** | Clarification required | Ambiguity, missing critical field | in-session |
| **L2** | Scientist review required | Prescription risk tier; low confidence; contradictory evidence; image cannot distinguish alternatives | ≤ 24 h (trial: same day) |
| **L3** | Urgent human intervention / field visit | Treatment failed + worsening; repeated failure; high-risk case; novel symptom | ≤ 48 h per institutional policy |
| **L4** | Safety / regulatory incident | Suspected harmful recommendation; regulatory conflict; adverse event | immediate + incident process |

**Escalation workflow:** `OPEN → ASSIGNED → INVESTIGATING → RESOLVED → LEARNING_CAPTURED`

**Escalation triggers (evidence- and policy-driven, not merely low confidence):** repeated contradictory farmer information; image cannot distinguish important alternatives; treatment failed; severity increasing; suspected regulatory issue; unusual/novel symptom; possible harmful recommendation; scientist disagreement; missing critical information.

**Human handoff design:** the farmer never experiences escalation as a dead end — they receive the case ID, status, and concrete next steps (send another photo, voice explanation, wait for expert, visit center). The scientist receives a compact case packet (summary, media, interpretation, contradictions, hypotheses, evidence, previous treatments, weather, AI recommendation, reason for escalation).

## 4.5 Release framework (MLOps / KnowledgeOps)

### 4.5.1 Version tuple

```text
SYSTEM_VERSION =
    MODEL_VERSION
  + KNOWLEDGE_VERSION
  + RULE_VERSION
  + PROMPT_POLICY_VERSION
  + SPEECH_VERSION
  + DATA_SCHEMA_VERSION
```

Every prescription records the full version tuple. Every edge device reports its active tuple; the admin console shows fleet distribution.

### 4.5.2 Release pipeline

```text
SOURCE DATA → VERSION CONTROL → VALIDATION → DATASET BUILD
  → MODEL / RULE / KB CANDIDATE
  → AUTOMATED TESTS (functional + regression)
  → SAFETY TESTS (blocking-rule suite, red-team suite)
  → COUNTEREXAMPLE TESTS (rules)
  → HOLDOUT EVALUATION (models)
  → EXPERT REVIEW (scientist/authorized)
  → REGISTRY (MLflow / KB registry / rule registry)
  → SHADOW (live cases, hidden output, compared vs production)
  → CANARY (subset of devices/cases)
  → PRODUCTION (signed edge bundles)
  → MONITOR (drift, correction rate, safety metrics)
  → ROLLBACK / REVISE (previous version retained, one-command restore)
```

### 4.5.3 Shadow mode

A candidate model receives live cases; its answer is hidden from farmers and compared against production model + scientist decisions. Shadow exit criteria: no safety regression, correction rate not worse, groundedness ≥ baseline.

### 4.5.4 Rollback

Previous production version of every artifact class (model/KB/rules/prompt/speech) is retained for at least 12 months. Rollback is a signed bundle re-deploy; target RTO ≤ 15 min per device.

## 4.6 Knowledge governance framework

### 4.6.1 Source authority hierarchy

1. Applicable law and official regulatory notices (PPQS/CIB&RC lists, gazette notifications)
2. Current official institutional recommendations (KVK/ANGRAU/ICAR)
3. KVK/ICAR/SAU-approved technical material
4. Official weather/agromet information (IMD)
5. Peer-reviewed or institutional research
6. Locally observed information validated by authorized experts
7. Secondary sources only after explicit review

### 4.6.2 Knowledge lifecycle

```text
AUTHORITATIVE SOURCE → INGESTION → NORMALIZATION (structured records + passages)
  → EXPERT REVIEW → TEST CASES (each KB entry ships with test questions)
  → VERSION (KB N+1, effective dates) → PUBLISH → EDGE BUNDLE (signed)
  → MONITOR (age, unanswered questions, retrieval recall) → RETIRE / REPLACE
```

### 4.6.3 Evidence ledger

Machine-readable ledger: `CLAIM → SOURCE → VERSION → DATE → AUTHORITY → CONFIDENCE`. Every high-impact recommendation is traceable to ledger entries. KB entries carry **effective dates** and **supersession links** (P4: guidance changes over time).

## 4.7 Evaluation framework

| Layer | What is measured | Tooling | Frequency |
|---|---|---|---|
| **Model benchmarking** | Raw capability (MMLU-IN, Telugu QA, e.g., VākQA) | lm-evaluation-harness | Per model candidate |
| **Application evaluation** | Retrieval recall, groundedness, answer relevancy, faithfulness | RAGAS + DeepEval | Per release + weekly on production sample |
| **Safety/red-team** | Prompt injection, prohibited product requests, rule bypass attempts | promptfoo (CI-blocking) | Every build + monthly |
| **Speech** | ASR entity accuracy (crop/pest/product/location), WER on Kurnool agri-vocabulary set | Custom eval set + WER/CER scripts | Per speech version |
| **Vision** | Image quality-check precision/recall; observation extraction accuracy; classifier F1 per disease/pest | Custom labeled set (KVK-curated) | Per vision version |
| **Clinical/agronomic quality** | Scientist correction rate, correction severity, escalation rate, first-contact resolution | Production metrics + scientist review | Continuous (trial: daily) |
| **End-to-end UX** | Telugu comprehension (target-user tests), latency (question→answer, question→print) | UAT sessions with farmers | Per release + monthly |

**LLM-as-judge bias controls:** judge models are pinned and versioned; judge outputs are sampled for human audit (≥10% weekly); metric thresholds are set by the evaluation framework spec, not by the model under test.

## 4.8 Data quality framework

| Check | Where | Rule |
|---|---|---|
| Schema validation | All API boundaries | Pydantic v2; LLM output must validate before pipeline entry |
| Duplicate detection | Learning ingestion | Exact + near-duplicate (embedding similarity > 0.95) dedup |
| Time/geography-aware splits | Model training | No leakage across season/region boundaries |
| Label validation | Training data | Two-scientist agreement for high-risk labels; conflicts → adjudication |
| Freshness | KB + weather | KB entries expire per policy; weather marked STALE after window |
| Provenance completeness | Learning records | All 11 provenance fields (§4.3.3) non-null or explicitly N/A |
| Contradiction scan | Case tree | Every new input checked against existing case state |

## 4.9 UX framework (farmer-facing)

1. **Confirmation gates**: critical entities (crop, stage, product, dose) are confirmed when ASR/interpretation confidence < θ_confirm — "I understood that the cotton leaves are curling. Is that correct?"
2. **Reason-for-question**: every question states its purpose ("Are the insects visible on the underside of the leaf?" — distinguishes hypothesis A from B).
3. **Active information gathering**: the next question is chosen to maximize expected uncertainty reduction, subject to farmer effort (≤3 questions per branch by default) and safety.
4. **Farmer-friendly explanation structure**: What I understood · What I am checking · Why I am asking · What you should do now · When to check again · When to contact an expert. Internal probabilities are never the main interface.
5. **Local terminology dictionary**: farmer terms → normalized terms with crop/geography context; corrections become language-learning candidates, never silent overwrites.
6. **Do-not-repeat memory**: no repeated questions, no re-requested images, no re-recommended failed treatments.
7. **Image guidance**: explicit photo requests ("one close photo of the affected leaf and one photo showing the whole plant"); unusable images get a concrete retry instruction.
8. **Escalation transparency**: case ID + status + what the farmer can do next.

---

# 5. TECHNOLOGY STACK & TOOL DEPENDENCIES

## 5.1 Stack overview

| Layer | Choice | Rationale (research-validated, Sep 2026) |
|---|---|---|
| Kiosk UI | **Flutter 3.x** (Linux/Windows target) | Single codebase for touch + camera + mic + printer + TTS playback; kiosk mode; strong plugin ecosystem (camera, audio, ESC/POS printing) |
| Scientist/Admin UI | **React 18 + TypeScript PWA** | Fast iteration, web-native, works on any device scientists use |
| Backend | **Python 3.12 + FastAPI + Pydantic v2** | Typed APIs, async, first-class AI/data ecosystem |
| Database | **PostgreSQL 17** | Transactional system of record; mature, boring, well-supported in India |
| Vector search | **pgvector 0.8.2** | HNSW + IVFFlat inside Postgres; exact & ANN; keeps hybrid retrieval in one DB (research: 0.8.x supports PG 18, iterative index scans) |
| Local LLM runtime | **Ollama 0.34.x** (primary) / llama.cpp (fallback) | Simple local model management, OpenAI-compatible API, active releases (v0.34.4, Sep 2026) |
| Local LLM (edge) | **Gemma 3 12B** (primary, vision-capable) / **Llama 3.1 8B** (lightweight) / Qwen2.5 14B (alt) | Gemma 3 12B: strong multilingual incl. Telugu + built-in SigLIP vision encoder (896×896, Pan&Scan) for image observations; fits 16 GB GPU at Q4/Q5 |
| Central LLM (online mode) | **Sarvam-M 24B** (Apache 2.0) | Best open Telugu/Indic LLM: +20% avg on Indian-language benchmarks vs base; Telugu reward score 8.05 vs Gemma 3 27B 6.95; hybrid think/non-think modes |
| ASR (offline, **primary**) | **ARTPARK-IISc/whisper-large-v3-vaani-telugu** (Apache-2.0, 2B) | Telugu-specialized Whisper large-v3 fine-tuned on the Vaani dataset with strong Telugu lexicon; runs via faster-whisper (int8) or transformers pipeline; benchmark on Kurnool agri-vocabulary |
| ASR (offline, **fast fallback**) | **ARTPARK-IISc/SraVaani-1.0** (MIT, ~430M, ~900 MB FP16, ONNX export) | FastConformer + hybrid TDT-CTC decoder; fine-tuned on ~31k hours across 65 Indian languages; Telugu WER ~25.1 avg; low-latency path when GPU is busy with LLM inference or latency budget is tight; fine-tunable (NeMo) |
| ASR (online) | **BHASHINI ASR API** | Government Indian-language platform; Telugu ASR; used when connectivity allows; also cross-checks low-confidence offline transcripts |
| TTS (offline) | **Piper (OHF-Voice/piper1-gpl) — Telugu voice** | Piper ships Telugu (తెలుగు) voices; ~60 MB, sub-second synthesis on CPU — ideal for offline kiosk (research: Piper voice catalog includes Telugu) |
| TTS (online) | **BHASHINI TTS API** | Higher-quality Telugu voices when online; fallback chain: Piper → BHASHINI (if online) → text-only display |
| Vision (observations) | **Gemma 3 12B vision** (via Ollama) | Structured visual observations (lesion, discoloration, insect presence, distortion, wilting) with OBSERVED/POSSIBLE/UNCERTAIN/CONTRADICTORY/NOT_VISIBLE states |
| Vision (classification) | **Fine-tuned ViT/ConvNeXt classifier** (PyTorch) on KVK-curated dataset | Research (WACV 2026 HARVEST-Vision): open VLMs achieve only ~39–65% on fine-grained crop disease classification vs 93% for prompted proprietary models → a domain classifier is required for reliable disease/pest ID; VLM stays as observation extractor + hypothesis generator |
| Embeddings | **BGE-M3 (569M, MIT)** | 100+ languages incl. Telugu; dense + sparse + multi-vector in one model; 8192-token context — ideal for hybrid retrieval over Telugu/English KB |
| Reranker | **BGE-Reranker-v2-M3 (MIT)** | Strong multilingual cross-encoder; pairs with BGE-M3; runs on a single GPU |
| Rules engine | **Python policy package** (`agri-rules`) | Deterministic, unit-testable, versioned; no external rule engine needed at pilot scale (evaluated: Drools/OPA rejected — Java/external-runtime overhead, weaker test ergonomics for agronomic logic) |
| Weather | **IMD API (api.imd.gov.in)** | Official: 7-day city forecast (by ID or lat/lon), current weather, district/subdivision warnings, rainfall, AWS/ARG data, **Agromet Advisory API**; IP whitelisting required; attribution required |
| Regulatory data | **PPQS/CIB&RC lists** (banned / refused-registration / restricted, effective 31 Mar 2024 + subsequent gazette updates) | Parsed into structured, versioned regulatory tables; re-verified before each release |
| Identity | **Keycloak 26.x** | OIDC authn/z, role-based access, standard for institutional deployments |
| Messaging (edge) | **EMQX 5.x** (central) + **EMQX Neuron / Mosquitto 2.x** (edge) | MQTT for device sync + telemetry; Kafka deferred until scale requires (per source design) |
| Observability | **OpenTelemetry + Prometheus + Grafana + Loki** | Vendor-neutral telemetry; traces across the full decision pipeline |
| MLOps | **MLflow 3.x + DVC 3.x** | Model registry, experiment tracking, dataset versioning; shadow/canary orchestration |
| Evaluation | **RAGAS + DeepEval + promptfoo + lm-evaluation-harness** | RAG metrics (research-backed), pytest-style app eval, red-teaming, model benchmarking |
| Fine-tuning | **Unsloth / axolotl + PEFT (LoRA)** | Efficient LoRA fine-tuning for Llama/Gemma/Qwen on rented or owned GPU |
| Analytics | **Metabase** (on PostgreSQL) | Lightweight, fast dashboards for pilot + district scale |
| Packaging | **Docker 27 / Podman 5 + K3s 1.3x** (central) / **Docker Compose** (edge) | Repeatable deployment; K3s keeps central ops simple |
| IaC / CI-CD | **Terraform 1.9 + GitHub Actions** | Reproducible environments; CI runs the full test + eval + red-team gate |
| WhatsApp | **WhatsApp Business Cloud API (Meta)** via BSP (e.g., AiSensy/WATI) or direct | Text/voice-note/photo in+out; per-message billing for template messages since 1 Jul 2025; service conversations in the 24-h window free (since 1 Nov 2024); utility templates in an open window free (since 1 Jul 2025); from 1 Oct 2026 a monthly free tier of 1,000 service messages per business number, then per-message; India INR billing since Jan 2026 (utility ≈ ₹0.115/msg, marketing ≈ ₹0.8631); further pricing updates 1 Aug 2026 + 1 Oct 2026; template approval lead time in India ~2–4 weeks |
| Object storage | **MinIO** | Media, signed KB bundles, model artifacts, backups |
| Cache/queue | **Redis 7** | Sessions, queues, rate limits |

## 5.2 Tool dependency registry

> Versions are the **baseline pins** for the start of implementation (Sep 2026). All pins live in lockfiles (`uv.lock`, `package.json`, `go.sum`, Dockerfile tags); upgrades follow the release framework (§4.5) with regression gates. "Alt" = approved alternative if the primary fails its evaluation gate.

### 5.2.1 Platform & infrastructure

| Tool | Baseline version | License | Used for | Alt |
|---|---|---|---|---|
| Python | 3.12.x | PSF | All backend services | 3.11 |
| FastAPI | 0.116.x | MIT | HTTP APIs (core + adapters) | Starlette directly |
| Pydantic | 2.x | MIT | Schema validation (all boundaries, LLM output) | — |
| PostgreSQL | 17.x | PostgreSQL | System of record + vectors | 18 (when pgvector 0.8.2 GA-stable on it) |
| pgvector | 0.8.2 | PostgreSQL | Vector similarity (HNSW) | — |
| Redis | 7.4 | BSD | Cache/queues | — |
| MinIO | RELEASE.2025-xx | AGPL-3.0 (or S3-compatible cloud) | Object storage | S3-compatible cloud |
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

### 5.2.2 AI/ML components

| Component | Baseline | License | Role | Alt / notes |
|---|---|---|---|---|
| Ollama | 0.34.x | MIT | Edge LLM runtime | llama.cpp server |
| Gemma 3 12B (Q4/Q5 GGUF) | Mar 2025 release | Gemma Terms of Use | Edge LLM + vision observations | Llama 3.1 8B (lighter), Qwen2.5 14B |
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

### 5.2.3 Client & integration

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

### 5.2.4 External data & services (managed dependencies)

| Dependency | Source | Access mode | Refresh policy | Failure behavior |
|---|---|---|---|---|
| Weather forecast/nowcast/warnings | IMD API (api.imd.gov.in) | HTTPS, IP-whitelisted, attribution | 15–60 min poll (central) → edge cache | Mark STALE after window; rules return UNKNOWN; never silently infer |
| Agromet advisory | IMD Agromet Advisory API | HTTPS | Daily | Cache last valid |
| Pesticide regulatory lists (banned/refused/restricted) | PPQS/CIB&RC (ppqs.gov.in) + gazette notifications | Manual + monitored download | On publication + quarterly audit | Last verified version stays active; admin alerted |
| Product registration data | CIB&RC | Manual ingestion | Quarterly | — |
| Speech (online) | BHASHINI API | HTTPS + API key | On-demand | Fallback to offline Piper/Whisper |
| WhatsApp | Meta Cloud API (via BSP) | HTTPS webhooks + REST | Real-time | Queue outbound; retry with backoff; case continues on other channels |

## 5.3 AI model registry (initial entries)

| ID | Model | Class | License | Deploy | Purpose | Status at M1 |
|---|---|---|---|---|---|---|
| MODEL-0.1.0 | Gemma 3 12B (Q5_K_M) | LLM+VLM | Gemma ToU | Edge (Ollama) | Advisory drafting, structured observations | Baseline benchmark |
| MODEL-0.1.1 | Llama 3.1 8B (Q5_K_M) | LLM | Llama 3.1 CL | Edge (Ollama) | Lightweight fallback / canary comparison | Baseline benchmark |
| MODEL-0.2.0 | Sarvam-M 24B (FP8/AWQ) | LLM | Apache-2.0 | Central (vLLM/Ollama) | Online-mode drafting, eval judge | Baseline benchmark |
| ASR-0.1.0 | whisper-large-v3-vaani-telugu (faster-whisper, int8) | ASR | Apache-2.0 | Edge | **Primary** offline Telugu/English transcription | WER benchmark on agri-vocab set |
| ASR-0.1.1 | SraVaani-1.0 (ONNX/FP16) | ASR | MIT | Edge | **Fast fallback** (low latency / GPU contention) | Latency + WER benchmark |
| ASR-0.2.0 | IndicWav2Vec Telugu (fine-tuned) | ASR | per AI4Bharat | Edge | Domain-adapted ASR candidate | Phase 5 candidate |
| TTS-0.1.0 | Piper Telugu (medium quality) | TTS | MIT | Edge | Offline Telugu speech | MOS test with farmers |
| TTS-0.2.0 | BHASHINI TTS Telugu | TTS | platform terms | Central | Online-quality speech | A/B with Piper |
| EMB-0.1.0 | BGE-M3 | Embedding | MIT | Edge + Central | KB + case embeddings | Recall benchmark |
| RERANK-0.1.0 | BGE-Reranker-v2-M3 | Reranker | MIT | Edge + Central | Evidence reranking | NDCG benchmark |
| VISION-0.1.0 | Gemma 3 12B vision | VLM | Gemma ToU | Edge | Structured observations | Observation-accuracy benchmark |
| CLASS-0.1.0 | ViT-B/16 fine-tuned (KVK dataset v1) | Classifier | — | Edge (ONNX) | Disease/pest classification | F1 per class benchmark |

**Model selection gate (Phase 1/5 exit):** each model class ships with a benchmark report on the KVK-curated evaluation sets (Telugu agri-vocabulary ASR set, KB retrieval set, disease image set, Telugu QA set). The primary model must beat the alternative by the framework-defined margin or be swapped — the architecture is model-agnostic by design.

## 5.4 Version pinning & dependency management

1. **Lockfiles are law**: `uv.lock` (Python), `package.json`/`pnpm-lock.yaml` (web), Dockerfile `ARG` pins, `go.sum` where applicable. CI fails on unpinned dependencies.
2. **Model artifacts are content-addressed**: every model/KB/rules bundle has a SHA-256 + signature; the version registry maps logical versions (MODEL-0.1.0) to artifact digests.
3. **Dependency update cadence**: security patches within 7 days; minor updates monthly with regression gate; major updates per release framework with expert sign-off for AI components.
4. **License compliance**: all production dependencies pass a license audit (permitted: MIT/Apache/BSD/PostgreSQL/PSF; reviewed: AGPL for internal-only services like MinIO/Metabase/Loki/Grafana; Gemma ToU and Llama CL reviewed by institution legal).

## 5.5 Dependency graph (build & runtime)

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
 │ Ollama      │◄──signed──┤ Keycloak     │                  │ (approved candidates)
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

---

# 6. DATA MODEL

Canonical, versioned schemas. All IDs are ULIDs (sortable, unique across edge+central). All timestamps are UTC with `Asia/Kolkata` display. All text fields store the original language; normalized fields are separate. **Nothing is ever overwritten** — corrections and reinterpretations append new rows/nodes.

## 6.1 Case graph (Case-to-Solution Tree)

```text
case
 ├─ case_id (ULID) · short_code (e.g., "BNV-4F7K2") · qr_payload
 ├─ channel (kiosk | whatsapp | web | operator) · channel_ref (e.g., WhatsApp message thread ID)
 ├─ farmer_ref (nullable, pseudonymous) · consent_ref
 ├─ kiosk_id (nullable) · location {state, district, mandal, village, lat, lon, accuracy}
 ├─ language (te | en | te-en) · created_at · updated_at · status (lifecycle state, §4.2)
 ├─ crop · variety · stage · severity (nullable until known)
 ├─ media_refs[] (media table)
 ├─ weather_snapshot_id · soil_snapshot_id (nullable)
 ├─ previous_interventions[] (intervention table, from farmer report)
 ├─ version_tuple {model, knowledge, rules, prompt_policy, speech, schema}
 └─ closed_at · close_reason (nullable)

case_node (append-only tree)
 ├─ node_id · case_id · parent_node_id (nullable) · node_type
 │   (input | interpretation | correction | observation | hypothesis | question
 │    | answer | evidence | contradiction | decision | intervention | outcome
 │    | escalation | scientist_feedback | similar_case_ref)
 ├─ created_at · created_by (farmer | system | scientist:<id> | operator)
 ├─ source (channel + modality: voice | touch | text | picture | system)
 ├─ confidence (0..1, nullable) · status (active | superseded | rejected)
 ├─ evidence_refs[] (evidence_ledger IDs) · payload (JSONB, typed per node_type)
 └─ immutable: no UPDATE except status transitions (superseded/rejected)
```

### 6.1.1 Node payloads (key types)

```text
input
 ├─ modality (voice | touch | text | picture | mixed)
 ├─ raw_ref (media ID for audio/image; raw string for text/touch)
 ├─ asr {model_id, version, confidence, duration_ms, engine: vaani-whisper | sravaani | bhashini} (voice)
 └─ quality {usable: bool, reasons[] } (picture/audio)

interpretation
 ├─ transcript (original, immutable)
 ├─ normalized_query
 ├─ entities {crop, variety, stage, problem, product, dose, location, ...} each {value, confidence, source}
 ├─ ambiguity {candidates[], explanation}
 └─ uncertainty_record {confidence, why, what_would_resolve}

correction (InterpretationCorrection)
 ├─ input_id · original_interpretation_ref · corrected_interpretation
 ├─ corrected_by (farmer | scientist | system-confirmed)
 ├─ correction_reason · confidence_before · confidence_after
 └─ evidence_refs[]

observation (image-derived)
 ├─ media_id · observation_type (lesion | discoloration | insect_presence | distortion | wilting | other)
 ├─ state (OBSERVED | POSSIBLE | UNCERTAIN | CONTRADICTORY | NOT_VISIBLE)
 ├─ classifier {model_id, class, probability} (nullable)
 └─ vlm_notes (structured, from Gemma 3 vision)

hypothesis
 ├─ problem_id (from KB taxonomy) · confidence
 ├─ supporting_refs[] · contradicting_refs[] · missing_evidence[]
 └─ status (active | confirmed | rejected)

question
 ├─ text (Telugu + English) · modality (voice | touch | text)
 ├─ decision_purpose {resolves: hypothesis_ids, distinguishes: [A, B]}
 ├─ options[] (for touch: quick-reply buttons)
 └─ asked_at · answered_at (nullable)

answer
 ├─ question_node_id · value · modality · raw_ref (nullable)
 └─ confidence

evidence
 ├─ evidence_ledger_id · retrieval {method: sql|keyword|vector|hybrid, score, rank}
 └─ relevance_note

contradiction
 ├─ field (crop | stage | problem | ...)
 ├─ existing_value · new_value · detected_by
 └─ resolution (clarified | resolved_by_farmers_answer | unresolved)

decision
 ├─ intent (information | diagnosis | advisory | prescription)
 ├─ diagnoses[] {problem_id, confidence} · selected_diagnosis
 ├─ interventions[] {product_id, formulation, dose, method, timing, phi_days, ppe[]}
 ├─ warnings[] · evidence_refs[] · rules_evaluated[] {rule_id, result: pass|block|review, details}
 ├─ confidence · model_version · knowledge_version · rule_version · prompt_policy_version
 └─ status (draft | approved | corrected | rejected | locked)

intervention (delivered action)
 ├─ decision_node_id · delivered_at · delivery {voice, screen, print_id, qr_id, whatsapp_msg_id}
 ├─ expected_observation · followup_due_at (from protocol)
 └─ status (delivered | pending_approval | blocked)

outcome
 ├─ intervention_id · reported_at · reported_by (farmer | worker | scientist)
 ├─ result (worked | partial | failed | worsened | unknown)
 ├─ farmer_report (text/voice ref) · supporting_media[]
 ├─ timing {days_after, weather_context_ref}
 ├─ verified_by (nullable) · failure_class (nullable, enum)
 ├─ escalation_id (nullable) · learning_status (pending | captured | rejected)
 └─ expected_result

escalation
 ├─ level (L1..L4) · trigger {type, evidence_refs[]}
 ├─ status (OPEN | ASSIGNED | INVESTIGATING | RESOLVED | LEARNING_CAPTURED)
 ├─ assigned_to · assigned_at · resolved_at · resolution_note
 └─ packet_ref (compact case packet for scientist)

scientist_feedback
 ├─ decision_node_id · scientist_id · modality (text | voice | image | annotated_image | structured)
 ├─ action (approve | correct | reject | escalate)
 ├─ changed_fields[] {field, original_value, corrected_value}
 ├─ reason · evidence_refs[] · reference_media[]
 └─ evidence_status (EVIDENCE_BACKED | LOCALLY_VALIDATED | EXPERT_PREFERENCE)
```

## 6.2 Decision delta (learning object)

```text
decision_delta
 ├─ delta_id · decision_node_id · case_id · scientist_id · created_at
 ├─ changed_fields[] {field, old_value, new_value}
 ├─ correction_type (PRODUCT_SELECTION | DOSAGE | FORMULATION | TIMING | DIAGNOSIS
 │                   | MISSING_CONTEXT | OUTDATED_KNOWLEDGE | LOCAL_CONDITION
 │                   | EXPERT_PREFERENCE | EXPLANATION)
 ├─ reason · evidence_refs[] · evidence_status
 ├─ context_snapshot_ref (full snapshot: case, weather, evidence, rules, versions, original output)
 ├─ approval_status (pending | approved_for_learning | rejected)
 ├─ learning_channel (knowledge | rule | training | case_memory | language | none)
 └─ released_version (nullable — which production version consumed it)
```

**Invariant:** the original AI decision is never overwritten; original + corrected states are both retained for learning and audit.

## 6.3 Evidence ledger

```text
evidence_ledger
 ├─ evidence_id · claim (normalized statement)
 ├─ source {type (law | institutional | kvc_sa | weather | research | local_validated | secondary),
 │          name, url/ref, version, published_date, retrieved_date}
 ├─ authority_level (1..7, §4.6.1) · effective_from · effective_to (nullable)
 ├─ superseded_by (nullable) · confidence (0..1)
 ├─ scope {crops[], regions[], seasons[]}
 └─ verified_by (scientist_id) · verified_at
```

## 6.4 Knowledge base (structured + passages)

```text
kb_entry
 ├─ entry_id · kb_version · entry_type (pest | disease | crop_practice | product | regulation | weather_rule | general)
 ├─ title {te, en} · summary {te, en}
 ├─ structured_fields (JSONB per type: e.g., product {active_ingredient, formulation, dose_range,
 │    method, phi_days, ppe[], target_pests[], crop_restrictions[]})
 ├─ scope {crops[], stages[], regions[], seasons[]} · authority_level · source_ref
 ├─ effective_from · effective_to · status (active | retired) · superseded_by
 ├─ test_cases[] {question {te,en}, expected_answer_points[], risk_tier}
 └─ created_by · reviewed_by · reviewed_at

kb_passage (for retrieval)
 ├─ passage_id · entry_id · kb_version · text {te, en} · chunk_index
 ├─ embedding_dense (vector 1024, BGE-M3) · sparse_weights (JSONB, BGE-M3 lexical)
 └─ metadata {crop, stage, region, authority_level, effective_from}
```

## 6.5 Rules

```text
rule
 ├─ rule_id · rule_version · rule_class (regulatory | crop_target | formulation | dose | method
 │    | weather_window | phi_ppe | environment | confidence_gate | clarification_policy)
 ├─ name {te, en} · description
 ├─ condition (JSON, deterministic predicate over case/decision/weather context)
 ├─ action (BLOCK | REVIEW | CONDITION | WARN | REQUIRE_CONFIRMATION)
 ├─ scope {crops[], regions[], products[]} · authority_source (evidence_ledger_id)
 ├─ test_cases[] {input_context, expected_action} · status (active | retired)
 └─ effective_from · effective_to · approved_by
```

## 6.6 Learning records & registry

```text
learning_candidate
 ├─ candidate_id · channel (knowledge | rule | training | language)
 ├─ source_refs[] (decision_delta_ids, outcome_ids, case_ids)
 ├─ payload (proposed KB entry / rule / training example / lexicon mapping)
 ├─ status (draft | in_validation | expert_review | approved | rejected | released)
 ├─ validation_report {data_quality, regression, safety, counterexample, holdout}
 ├─ provenance {who, what_observed, when, channel, evidence, ai_original, corrected,
 │              independently_verified, outcome_support, approved_for_learning, used_in_version}
 └─ created_at · reviewed_by · decided_at

version_registry
 ├─ artifact_class (model | knowledge | rules | prompt_policy | speech | schema)
 ├─ version (semver) · artifact_ref (MinIO key) · sha256 · signature
 ├─ status (candidate | shadow | canary | production | retired)
 ├─ promoted_at · promoted_by · retired_at · retirement_reason
 └─ environment (edge | central)

prescription
 ├─ prescription_id · decision_node_id · case_id · status (draft | approved | locked | printed | void)
 ├─ content {diagnosis, product, formulation, dose, method, timing, phi, ppe[], warnings[],
 │           explanation {te, en}, safety_notes}
 ├─ version_tuple · scientist_id · approved_at · locked_at
 ├─ print_id (nullable) · qr_payload (prescription_id + verification URL)
 └─ verification {verified_at, verified_by, result}
```

## 6.7 Device & sync

```text
device
 ├─ device_id (kiosk_id) · name · location · hardware_profile · cert_fingerprint
 ├─ status (online | offline | degraded | decommissioned) · last_seen_at
 ├─ active_version_tuple · sync_state {last_event_seq, pending_events, last_sync_at}
 └─ health {cpu, mem, gpu, disk, temp, printer_ok, network} (latest snapshot)

sync_event (append-only, edge → central)
 ├─ event_id (ULID) · device_id · seq · case_id (nullable)
 ├─ event_type (input | interpretation | correction | decision | outcome | escalation | telemetry | print_job)
 ├─ payload (JSONB) · created_at · ack_status (pending | acked | failed)
 └─ idempotency_key (event_id)

sync_manifest (central → edge)
 ├─ manifest_id · issued_at · device_id
 ├─ artifacts[] {class, version, sha256, signature, minio_key, size}
 └─ applied_state (edge reports back which versions are active)
```

## 6.8 PostgreSQL table map (central)

| Table | Purpose | Key indexes |
|---|---|---|
| `cases` | Case headers | short_code, farmer_ref, status, created_at |
| `case_nodes` | CST append-only nodes | (case_id, node_type), (case_id, created_at), GIN(payload) |
| `media` | Audio/image metadata + MinIO refs | case_id, media_type |
| `decisions` | Decision objects (denormalized from nodes for query) | case_id, status, version_tuple |
| `decision_deltas` | Learning objects | correction_type, approval_status, learning_channel |
| `evidence_ledger` | Claims → sources | authority_level, effective_from, GIN(scope) |
| `kb_entries` / `kb_passages` | Knowledge + vectors | HNSW(embedding_dense), (entry_id), GIN(metadata) |
| `rules` | Rule definitions | rule_class, status, GIN(scope) |
| `learning_candidates` | Candidate artifacts | channel, status |
| `version_registry` | Artifact versions | (artifact_class, version), status |
| `prescriptions` | Locked prescriptions | prescription_id, case_id, status |
| `outcomes` | Outcome records | case_id, result, reported_at |
| `escalations` | Escalation workflow | status, level, assigned_to |
| `followups` | Scheduled follow-ups | followup_due_at, status |
| `devices` / `sync_events` / `sync_manifests` | Device fleet + sync | device_id, seq, ack_status |
| `users` / `roles` (Keycloak-synced) | Identity | role |
| `audit_log` | Append-only audit (who/what/when/version) | entity_type, entity_id, created_at |
| `weather_snapshots` | Cached IMD data | (station_id, date), staleness |
| `regulatory_products` | PPQS/CIB&RC parsed lists | active_ingredient, status (banned/refused/restricted/permitted) |
| `lexicon` | Local terminology mappings | term, crop, region, status |
| `similar_case_index` | Case embeddings for similarity | HNSW(embedding) |

## 6.9 Data retention & privacy

| Data class | Retention | Notes |
|---|---|---|
| Case graph + decisions | 5 years (institutional policy) | Agricultural record value; supports surveillance analytics |
| Media (photos/audio) | 1 year default; 5 years if flagged for diagnosis/learning with consent | Faces blurred by default in stored copies (policy decision) |
| Farmer PII (phone, if opt-in) | Until consent withdrawal + 90 days | DPDP Act 2023; purpose-limited |
| Learning records | 5 years | Provenance requirement |
| Audit log | 7 years | Institutional + regulatory |
| Weather cache | 90 days | Re-fetchable |

---

# 7. API CONTRACTS

All endpoints are typed (Pydantic v2 request/response). LLM output is schema-validated **before** entering the rules/prescription pipeline. Auth: OIDC bearer (Keycloak) for scientist/admin/auditor; device mTLS for sync; farmer endpoints are pseudonymous (case-scoped tokens).

## 7.1 Core session & input (v1 + v2)

| Method & path | Purpose | Key request fields | Key response fields |
|---|---|---|---|
| `POST /v1/session` | Create kiosk session | channel, kiosk_id, language, consent_ack | session_id, case_id, short_code |
| `POST /v1/speech/transcribe` | ASR (edge-local or central) | audio (base64/URL), language, engine_hint (auto \| vaani-whisper \| sravaani \| bhashini) | transcript, confidence, engine_used, duration_ms, entity_candidates[] |
| `POST /v1/intent/parse` | Typed intent + entity extraction | text, case_id | intent, entities{}, ambiguity{}, confidence |
| `POST /v1/cases` | Create case | channel, location, language, farmer_ref? | case_id, short_code, qr_payload |
| `POST /v1/cases/{id}/inputs` | Add text/audio/image input (v2) | modality, payload/media_ref, asr_result? | input_node_id, quality, next_state |
| `POST /v1/cases/{id}/interpretations` | Store system interpretation (v2) | transcript, entities, ambiguity, confidence | interpretation_node_id |
| `POST /v1/cases/{id}/corrections` | Farmer/scientist interpretation correction (v2) | input_id, corrected_entities, corrected_by, reason | correction_node_id, confidence_after |
| `POST /v1/cases/{id}/questions` | Generate/store targeted question (v2) | purpose {resolves, distinguishes}, options[] | question_node_id, text {te,en}, options[] |
| `POST /v1/cases/{id}/answers` | Store answer, update tree (v2) | question_node_id, value, modality | answer_node_id, next_state |
| `GET /v1/cases/{id}/tree` | Retrieve full CST (v2) | depth?, include_media? | nodes[], state, hypotheses[], pending_questions[] |
| `POST /v1/cases/{id}/similar-cases` | Retrieve comparable validated cases (v2) | top_k, filters {crop, stage, region, season} | cases[] {case_id, similarity, differences[], outcome} |
| `POST /v1/cases/{id}/outcomes` | Record intervention outcome (v2) | intervention_id, result, farmer_report, media[], timing | outcome_id, next_state, escalation_id? |
| `POST /v1/cases/{id}/escalate` | Create escalation (v2) | level, trigger, evidence_refs[] | escalation_id, packet_ref, farmer_message |
| `POST /v1/media/analyze` | Image/media evidence extraction (v2) | media_ref, case_id, requested_views[] | quality, observations[], candidate_hypotheses[], missing_views[] |

## 7.2 Retrieval, rules, advisory (v1)

| Method & path | Purpose | Notes |
|---|---|---|
| `POST /v1/retrieval/search` | Hybrid evidence retrieval | filters {crop, stage, region, validity}; returns ranked evidence with method+score+authority |
| `POST /v1/rules/evaluate` | Deterministic validation | input: decision draft + context; output: per-rule results (pass/block/review/warn) |
| `POST /v1/advisory/draft` | Grounded advisory draft | LLM draft with evidence IDs; schema-validated; risk tier assigned |
| `POST /v1/prescriptions` | Create locked prescription | Only from approved decision; records version tuple |
| `GET /v1/prescriptions/{id}` | Verify prescription | Public verification (QR scan): status, content, versions, scientist, expiry |
| `POST /v1/print` | Print approved artifact | Idempotent (print_id); printer status checked; no duplicate on failure |

## 7.3 Review & learning (v1 + v2)

| Method & path | Purpose | Notes |
|---|---|---|
| `POST /v1/review` | Approve/correct/escalate | Scientist changes only wrong fields; system auto-attaches full context snapshot |
| `POST /v1/corrections` | Persist decision delta | Creates decision_delta + context snapshot; classifies correction type |
| `POST /v1/scientist/feedback` | Voice/text/image/annotated/structured feedback (v2) | ASR for voice; media attach; same delta pipeline |
| `POST /v1/learning/candidates` | Create candidate learning artifact | From approved deltas/outcomes |
| `GET /v1/learning/candidates` | Scientist review queue | Filter by channel/status |
| `GET /v1/learning/provenance/{id}` | Trace learning signal to source case (v2) | Full 11-field provenance |
| `POST /v1/releases` | Approve release (shadow→canary→production) | Release authority role; triggers signed bundle build |

## 7.4 Sync & device (v1)

| Method & path | Purpose | Notes |
|---|---|---|
| `POST /v1/sync/push` | Upload queued events | Batch, idempotent by event_id; returns acks + gaps |
| `GET /v1/sync/manifest` | Get current versions for device | Returns artifacts newer than device's active tuple |
| `GET /v1/device/health` | Device health report | Telemetry batch (also via MQTT) |
| `POST /v1/followups` | Schedule outcome follow-up (v2) | Protocol-based window; channel selection |
| `GET /v1/escalations` | Scientist escalation queue (v2) | Level, SLA age, packet |

## 7.5 MQTT topics (device ↔ central)

| Topic | Direction | Payload | QoS |
|---|---|---|---|
| `kiosk/{device_id}/telemetry` | edge → central | health, temp, disk, printer, sync backlog | 1 |
| `kiosk/{device_id}/events` | edge → central | batched sync_events (mirror of `/v1/sync/push`) | 1 |
| `kiosk/{device_id}/manifest` | central → edge | sync_manifest (versions to fetch) | 1 |
| `kiosk/{device_id}/command` | central → edge | {reboot, fetch_bundle, reset_session, update_app} | 1 |
| `kiosk/{device_id}/ack` | edge → central | manifest applied / command result | 1 |
| `alerts/safety` | edge → central | L4 incident (immediate) | 2 |

## 7.6 Webhooks (inbound)

| Source | Endpoint | Handling |
|---|---|---|
| WhatsApp Cloud API | `POST /webhooks/whatsapp` | Verify token (GET); parse text/audio/image messages → `case_id` mapping (phone → farmer_ref → active case); media download to MinIO |
| IMD (polling, not webhook) | `weather-service` worker | 15–60 min poll → `weather_snapshots` → edge cache update via manifest |

## 7.7 Conventions

- Errors: RFC 7807 problem+json; domain error codes (`RULE_BLOCKED`, `CONFIRMATION_REQUIRED`, `WEATHER_STALE`, `APPROVAL_REQUIRED`, `SYNC_GAP`...).
- Idempotency: `Idempotency-Key` header on all mutating endpoints; sync events idempotent by `event_id`.
- Pagination: cursor-based (`?cursor=&limit=`).
- Versioning: URL prefix `/v1`; breaking changes → `/v2` with 6-month overlap.
- Every response for a decision-bearing call includes `version_tuple` and `trace_id` (OpenTelemetry).

# 8. SERVICE DECOMPOSITION

This section expands the 26 services from §3.3 into buildable units. For each service: responsibility, technology, interfaces, scaling notes, and the phase in which it is built (phase numbers per §10). Services are deliberately small and single-purpose; the canonical case service (S7) is the only service that owns case state.

## 8.1 Edge services

### S1 — channel-adapter-kiosk (edge)
- **Responsibility:** The farmer-facing kiosk application. Voice capture (mic array → 16 kHz WAV), touch guided flow (pickers, quick replies, confirmation gates), text input (Telugu script + Latin keyboard), camera capture with framing guidance, TTS playback, print UI, session lifecycle (start/timeout/reset), offline queue visibility.
- **Tech:** Flutter 3.x (Linux target), kiosk mode (auto-start, no desktop escape), plugins: `camera`, `record`/`audio`, `esc_pos_printer`, `usb_serial`, `local_auth` (operator PIN). All intelligence calls go to the local core-api over localhost.
- **Interfaces:** core-api (localhost HTTP), thermal printer (USB/serial ESC/POS), device-agent (health queries), hardware sensors (temperature, UPS).
- **Scaling:** One instance per device; no horizontal scaling — reliability engineering instead (watchdog auto-restart, session resume, print idempotency).
- **Built in:** Phase 1 (MVP: touch+text+print, basic voice) → extended in Phases 2, 4, 5 (camera, cross-correction UX, media sets).

### S19 — sync-agent (edge + central peer)
- **Responsibility:** Encrypted, idempotent, resumable synchronization. Up: append-only events (inputs, decisions, corrections, outcomes, telemetry, print jobs) batched with sequence numbers. Down: signed versioned manifests (knowledge, rules, models, prompt policy, lexicon, weather baseline) → fetch from MinIO → verify signature → activate. Gap detection and repair; media queue (chunked, resumable uploads).
- **Tech:** Python (edge) + FastAPI endpoints (central); MQTT (EMQX) for manifest/command signaling; HTTPS for bulk transfer; minisign/cosign signature verification; LUKS-encrypted local queue.
- **Interfaces:** EMQX topics (§7.5), core-api `/v1/sync/*`, MinIO, device-agent (activation hooks).
- **Scaling:** Per-device instance with backpressure; central peer is stateless workers. Idempotency by `event_id` makes retries safe.
- **Built in:** Core sync in WS-OFFLINE (W3); media sync in Phase 12.

### S20 — device-agent (edge)
- **Responsibility:** Device health and lifecycle: CPU/GPU/memory/disk/temperature, printer status (paper, errors), network status (Ethernet/Wi-Fi/4G), UPS state, graceful shutdown on power loss, watchdog for kiosk-ui and core-api, signed update verification and staged activation, telemetry batching.
- **Tech:** Python daemon (systemd), `nvidia-smi`/`tegrastats` for GPU, MQTT telemetry publisher with local buffering.
- **Interfaces:** MQTT `kiosk/{device_id}/telemetry|ack`, admin-console (via central), sync-agent (update activation).
- **Scaling:** Per-device; no scaling concerns. Fleet view in admin console.
- **Built in:** Basic in Phase 1 (W1); full in WS-OFFLINE (W3).

## 8.2 Core decision services (run on edge and central)

### S4 — input-orchestrator (core)
- **Responsibility:** Single entry point for all inputs across all modalities and channels. Routes audio → speech-service, images → image-service, text → text normalizer, touch events → case-service directly. Owns session state. Enforces input quality gates. Creates immutable `Input` nodes and triggers interpretation. Enforces do-not-repeat memory at input time (e.g., already-received image views).
- **Tech:** Python/FastAPI; session state in Redis (central) / local Redis (edge); Pydantic v2 schemas.
- **Interfaces:** speech-service, image-service, case-service, channel adapters (inbound), lexicon (shared library).
- **Scaling:** Stateless compute; horizontal replicas behind the API gateway. Session state externalized.
- **Built in:** Phase 1.

### S5 — speech-service (core)
- **Responsibility:** Full voice pipeline per §9.1: VAD (silero-vad), ffmpeg normalization (16 kHz mono WAV), ASR engine selection and fallback chain (Vaani-Whisper primary → SraVaani fast → BHASHINI online cross-check), agricultural vocabulary normalization, entity candidate extraction, TTS synthesis (Piper → BHASHINI → text-only fallback). Records engine/model/confidence on every `Input` node.
- **Tech:** Python; faster-whisper (int8) for Whisper family; ONNX Runtime for SraVaani; Piper (piper1-gpl) for TTS; ffmpeg; silero-vad. GPU-aware job queue (ASR yields to LLM inference when VRAM is contended → SraVaani on CPU/ONNX path).
- **Interfaces:** input-orchestrator, MinIO (audio objects), lexicon table, BHASHINI API (online), case-service (via orchestrator).
- **Scaling:** Concurrency-limited GPU queue; per-engine latency SLOs (§9.1.6); horizontal replicas share the GPU pool via queue.
- **Built in:** Basic chain in Phase 1 (W1 kiosk MVP); full fallback + cross-check in Phase 4; scientist voice feedback in Phase 8.

### S6 — image-service (core)
- **Responsibility:** Image evidence pipeline per §9.4: quality checks (blur/brightness/size/crop detection), structured visual observations via Gemma 3 vision (states OBSERVED/POSSIBLE/UNCERTAIN/CONTRADICTORY/NOT_VISIBLE), fine-tuned ViT disease/pest classifier, media-set management (views: whole plant, leaf, stem, fruit, pest close-up, field context), missing-view requests, face-blurring for stored media.
- **Tech:** Python; OpenCV/Pillow for deterministic quality checks; Ollama (Gemma 3 12B vision) for observations; PyTorch/ONNX ViT classifier; MinIO for media.
- **Interfaces:** input-orchestrator, MinIO, case-service (observation nodes), lexicon (crop/pest taxonomy).
- **Scaling:** GPU job queue (batched); classifier runs on CPU/ONNX for low latency; observation extraction is the GPU-bound step.
- **Built in:** Phase 5.

### S7 — case-service (core) — the canonical case service
- **Responsibility:** Owns the Case-to-Solution Tree: append-only `case_node` writes, lifecycle state machine (§4.2) with transition guards, contradiction detection, do-not-repeat memory, case continuity (short code, QR payload, cross-channel mapping), tree retrieval. The only service that mutates case state (append-only; status transitions only).
- **Tech:** Python/FastAPI; PostgreSQL (system of record); ULID IDs; DB-level append-only enforcement (triggers reject UPDATE/DELETE except status transitions).
- **Interfaces:** All core services; channel adapters (via orchestrator); retrieval-service (case embeddings); escalation/outcome services.
- **Scaling:** Stateless API; Postgres partitioned by `case_id` range; read replicas at district scale. Hot path is small (node append + state transition).
- **Built in:** Phase 1 (schema + skeleton) → Phase 3 (full tree semantics).

### S8 — retrieval-service (core)
- **Responsibility:** Hybrid evidence retrieval per source §14: structured filters first (crop/stage/geography/validity), then hybrid search — SQL/exact + keyword (Postgres FTS/BM25) + vector (pgvector, BGE-M3 dense + sparse) — then reranking (BGE-Reranker-v2-M3) and evidence ranking by authority + freshness + relevance. Also serves similar-case search (case embeddings) for S7/Phase 7.
- **Tech:** Python; PostgreSQL 17 + pgvector 0.8.2 (HNSW); BGE-M3 (edge + central); BGE-Reranker-v2-M3 (GPU).
- **Interfaces:** advisory-service, case-service, knowledge-service (index maintenance), similar-case index.
- **Scaling:** Single Postgres with HNSW is sufficient for pilot (KB ~10⁴–10⁵ passages); read replica + index tuning at district scale. Embedding generation is batch (KB re-index worker), not on the hot path.
- **Built in:** WS-AI (W2), consumed by Phases 3, 6, 7.

### S9 — rules-service (core)
- **Responsibility:** Deterministic policy package (`agri-rules`): regulatory checks (banned/refused/restricted → BLOCK/REVIEW/CONDITION), crop/target, formulation, dose range, application method, weather window (GREEN/CAUTION/BLOCKED/UNKNOWN), PHI/PPE/environment, confidence gates, clarification policy. Pure functions over typed context; every rule has `test_cases[]`; counterexample search for rule candidates.
- **Tech:** Python policy package (no external rule engine — evaluated and rejected Drools/OPA for Java/external-runtime overhead and weaker test ergonomics); versioned as a signed artifact (RULE version in the version tuple).
- **Interfaces:** advisory-service, prescription-service, weather-service (context input), learning-service (counterexample search).
- **Scaling:** In-process library (no network hop); zero scaling concerns. Test suite runs in CI on every build.
- **Built in:** WS-RULES (W1–W2); counterexample search in Phase 11.

### S10 — llm-service (core)
- **Responsibility:** Local LLM inference management: Ollama runtime, structured output generation (JSON schema enforced before pipeline entry), prompt-policy versioning (PROMPT_POLICY_VERSION), shadow-model runner (candidate model answers live cases hidden, Phase 14), token/latency/VRAM telemetry, model hot-swap.
- **Tech:** Python; Ollama 0.34.x (Gemma 3 12B Q5_K_M primary, Llama 3.1 8B light); llama.cpp fallback; Pydantic v2 output validation; OpenTelemetry spans per call.
- **Interfaces:** advisory-service, image-service (vision observations), mlops-service (shadow orchestration), device-agent (GPU state).
- **Scaling:** GPU queue with priority (prescription drafting > observations > shadow); OOM handling (evict to SraVaani/CPU path, queue); one GPU per kiosk at pilot.
- **Built in:** WS-AI (W2); shadow runner in Phase 14.

### S11 — advisory-service (core)
- **Responsibility:** Composes the grounded answer: retrieval evidence + rules evaluation + LLM draft → advisory/prescription draft with evidence-ID retention end-to-end; risk-tier assignment (information/diagnosis/advisory/prescription); verification-gate orchestration (Phase 6); confirmation-gate decisions (θ_confirm, θ_auto).
- **Tech:** Python/FastAPI; Pydantic v2 decision schemas (§6.1.1 `decision` payload).
- **Interfaces:** retrieval-service, rules-service, llm-service, case-service, prescription-service, review-service.
- **Scaling:** Stateless; CPU-bound orchestration (GPU work delegated to S10/S6).
- **Built in:** WS-AI (W2) → Phase 6 (verification engine).

### S12 — prescription-service (core)
- **Responsibility:** Locked prescription objects: created only from approved decisions; records full version tuple; print job management (idempotent `print_id`, no duplicates on printer failure); QR generation (prescription_id + verification URL); public verification endpoint (QR scan → status, content, versions, scientist, expiry).
- **Tech:** Python/FastAPI; `qrcode`; ESC/POS print job format; MinIO (printed artifact archive).
- **Interfaces:** advisory-service/review-service (input), print hardware (edge), MinIO, public verification API.
- **Scaling:** Stateless; print queue on edge with retry + idempotency.
- **Built in:** Phase 1 (print MVP in kiosk MVP) → full lock/verify in WS-AI (W2).

### S13 — review-service (core)
- **Responsibility:** Scientist review queue: approve/correct/escalate; automatic full context snapshot (source §8 — case, language, input, crop, problem, location, weather, soil, previous management, knowledge, rules, AI, scientist, output, audit); decision-delta creation; correction classification trigger; review SLA tracking (L2 ≤ 24 h; trial: same day).
- **Tech:** Python/FastAPI; snapshot builder (read-only aggregation over case graph); Pydantic v2 delta schemas.
- **Interfaces:** case-service, learning-service, escalation-service, scientist-portal (S21), WhatsApp adapter (review notifications).
- **Scaling:** Stateless; queue is Postgres-backed.
- **Built in:** WS-PORTAL (W2, basic approve/correct/escalate) → Phase 8 (multimodal feedback, full snapshot).

### S14 — learning-service (core)
- **Responsibility:** Correction classifier (10 delta types, §4.3.2); candidate generation per channel (knowledge/rule/training/language/case memory); provenance ledger (all 11 fields, §4.3.3); learning sandbox orchestration (data quality → regression → safety → counterexample → holdout); pattern discovery (group validated corrections by crop/stage/problem/region/season; min support N≥5, consistency ≥80%); candidate review workflow.
- **Tech:** Python; batch + event-driven (Celery-style workers on Redis); MLflow/DVC integration for training candidates.
- **Interfaces:** review-service, outcome-service, mlops-service, knowledge-service, rules-service, admin-console (candidate queues).
- **Scaling:** Batch workers; pattern discovery is a scheduled job (weekly).
- **Built in:** Phase 11.

### S15 — outcome-service (core)
- **Responsibility:** Follow-up scheduling from approved advisory protocols (not fixed intervals); outcome capture (worked/partial/failed/worsened/unknown) across channels (kiosk return visit, WhatsApp, extension worker, scientist portal); expected-observation tracking; failed-solution protocol (stop automatic repetition → reassess → request new evidence → compare original vs current case → check alternative hypotheses → escalate if triggers met); failure learning records.
- **Tech:** Python/FastAPI; scheduler (Redis-backed cron); channel adapter webhooks for delivery.
- **Interfaces:** case-service, escalation-service, channel adapters (S1/S2/S3), learning-service.
- **Scaling:** Stateless + scheduler; follow-up volume is small at pilot (dozens/day).
- **Built in:** Phase 9.

### S16 — escalation-service (core)
- **Responsibility:** Escalation engine L0–L4 (§4.4): evidence- and policy-driven triggers (not merely low confidence); assignment; status workflow `OPEN → ASSIGNED → INVESTIGATING → RESOLVED → LEARNING_CAPTURED`; compact human-handoff packet (summary, media, interpretation, contradictions, hypotheses, evidence, previous treatments, weather, AI recommendation, reason); farmer-facing transparency (case ID, status, next steps); SLA tracking and alerts.
- **Tech:** Python/FastAPI; packet builder (read-only aggregation); MQTT `alerts/safety` for L4 (QoS 2).
- **Interfaces:** case-service, review-service, channel adapters, admin-console, observability (alerts).
- **Scaling:** Stateless; low volume, high criticality.
- **Built in:** Phase 10.

### S17 — weather-service (core)
- **Responsibility:** IMD ingestion (central worker, 15–60 min poll: cityforecast/cityforecastloc, current weather, district/subdivision warnings, rainfall, AWS/ARG, Agromet Advisory); timestamp + location validation; unit normalization; `weather_snapshots` table; staleness marking (STALE after 6 h forecast / 2 h nowcast windows); spray-window evaluation input for rules-service; edge cache distribution via sync manifests.
- **Tech:** Python worker; HTTPS (IP-whitelisted, attribution); Postgres; manifest publisher.
- **Interfaces:** rules-service, sync-agent (down), advisory-service (context), admin-console (staleness alerts).
- **Scaling:** Single idempotent worker; edge keeps last-known snapshot and marks STALE — never silently infers.
- **Built in:** WS-RULES (W1–W2, needed for weather-window rules).

### S18 — knowledge-service (core)
- **Responsibility:** KB lifecycle (source §27): ingestion (PDFs/manuals → structured records + passages via pypdf/unstructured/marker), normalization, expert review workflow, versioning (KB N+1 with effective dates + supersession links), test cases per entry, edge bundle publishing (signed), evidence ledger management, re-index/re-embed worker, retirement/monitoring (age, unanswered questions, retrieval recall).
- **Tech:** Python; ingestion workers; MinIO (bundles); pgvector re-index; minisign signatures.
- **Interfaces:** admin-console (review UI), retrieval-service (index), sync-agent (bundles), learning-service (candidates), evidence ledger.
- **Scaling:** Batch workers; KB size at pilot ~10⁴–10⁵ passages.
- **Built in:** WS-KB (W1–W2: KB v1 for Kurnool crops); versioning/bundles in Phase 11/14.

## 8.3 Central platform services

### S2 — channel-adapter-whatsapp (central)
- **Responsibility:** WhatsApp Business Cloud API adapter: webhook verification + inbound (text/voice note/photo/multiple photos) → `case_id` mapping (phone → farmer_ref → active case); media download to MinIO; outbound rendering (text cards, quick replies, list messages, media); template management (India approval ~2–4 weeks; utility templates for follow-ups outside the 24-h window); per-message billing tracking (per-message since Jul 2025; free service tier from Oct 2026); queue + retry with backoff.
- **Tech:** Python/FastAPI; Meta Graph SDK; webhook signature verification; Redis outbound queue.
- **Interfaces:** Meta Cloud API, case-service (via orchestrator), MinIO, speech-service (voice notes), image-service (photos).
- **Scaling:** Stateless, 2 replicas; webhook is at-least-once → idempotent handlers.
- **Built in:** Phase 2.

### S3 — channel-adapter-web (central)
- **Responsibility:** Farmer-facing web/mobile PWA: chat (text/voice optional), photo upload, case lookup by QR/short code, outcome reporting, follow-up responses. Pseudonymous (case-scoped tokens; no account required).
- **Tech:** React 18 + TypeScript PWA (Vite, Tailwind) + FastAPI backend.
- **Interfaces:** case-service (via orchestrator), MinIO (uploads), Keycloak (optional login for returning farmers).
- **Scaling:** Stateless; static assets on CDN.
- **Built in:** Phase 2.

### S21 — scientist-portal (central UI)
- **Responsibility:** React PWA for KVK scientists: review queue (prescriptions + uncertain cases), minimal-field correction UX (approve/correct/escalate; only wrong fields editable), multimodal feedback (text, voice → ASR → structured correction, image, annotated image), automatic context display (read-only snapshot), candidate approval (knowledge/rule/training/language), escalation queue with SLA, dashboards (AI quality, safety, learning).
- **Tech:** React 18 + TypeScript PWA; Keycloak OIDC; WebSocket/SSE for queue updates.
- **Interfaces:** review-service, learning-service, escalation-service, case-service (tree view), speech-service (voice feedback).
- **Scaling:** Stateless; small user base (dozens of scientists at district scale).
- **Built in:** WS-PORTAL (W2) → Phase 8 (multimodal).

### S22 — admin-console (central UI)
- **Responsibility:** Platform administration: device fleet management (status, health, active version tuple, sync state), release management (shadow→canary→production promotion, rollback), users/roles, audit views, KB/rules review workflows, weather staleness alerts, candidate queues.
- **Tech:** React 18 + TypeScript PWA; Keycloak OIDC (admin/auditor roles).
- **Interfaces:** version_registry, devices, Keycloak, mlops-service, knowledge-service, learning-service.
- **Scaling:** Stateless; small user base.
- **Built in:** Basic in Phase 1 (W1); full in W3–W5.

### S23 — identity (Keycloak) (central)
- **Responsibility:** OIDC authentication/authorization. Roles: `farmer` (pseudonymous, no account at kiosk — case-scoped tokens), `operator`, `scientist`, `admin`, `auditor`. Device identity: TLS client certificates (mTLS) for kiosk sync; device registry. Consent records linkage (DPDP).
- **Tech:** Keycloak 26.x on Postgres; certificate issuance via internal CA (or Keycloak client certs); role mapping from institutional directories.
- **Interfaces:** All central services (bearer tokens), sync (mTLS), admin-console.
- **Scaling:** 2 replicas + Postgres; standard Keycloak HA.
- **Built in:** Phase 1 (W1).

### S24 — analytics (central)
- **Responsibility:** Metabase dashboards on the central Postgres: service operations (queries/day, response time, print success, escalations), crop intelligence (crop/stage distribution), pest surveillance (incidence by geography/time — review signal only, never autonomous outbreak declaration), AI quality (correction rate/types), safety (blocked interventions, regulatory conflicts), knowledge (unanswered questions, stale records), language (ASR confidence, corrected entities), learning (accepted corrections, candidate rules, model versions), device (uptime, errors, temperature, sync backlog).
- **Tech:** Metabase (OSS) on PostgreSQL; scheduled aggregate tables (nightly) to keep dashboards fast.
- **Interfaces:** Postgres (read replica).
- **Scaling:** Read replica; aggregate tables.
- **Built in:** W3 (operations + safety) → W4 (trial dashboards) → W5 (surveillance + learning).

### S25 — observability (cross-cutting)
- **Responsibility:** OpenTelemetry SDK in every service: traces (question → ASR → retrieval → rules → LLM → gate → output, with input hashes + version tuple per span), metrics, structured logs. Prometheus + Grafana + Loki on central; edge ships telemetry via MQTT with local buffering. Alerting (safety, staleness, sync backlog, GPU OOM, printer failure).
- **Tech:** OpenTelemetry Python SDK; Prometheus 2.x; Grafana 11.x; Loki 3.x; alertmanager.
- **Interfaces:** All services; MQTT (edge telemetry); admin-console (alert views).
- **Scaling:** Standard; edge buffering handles connectivity gaps.
- **Built in:** Skeleton in Phase 1 (W1); full pipeline in W2.

### S26 — mlops-service (central)
- **Responsibility:** MLflow 3 registry (models, experiments) + DVC 3 dataset versioning; evaluation runners (RAGAS, DeepEval, promptfoo, lm-evaluation-harness) as CI jobs and scheduled production sampling; shadow-mode orchestration (candidate model on live cases, hidden output, comparison vs production + scientist decisions); canary orchestration (device/case subsets); signed bundle build (model/KB/rules/prompt/speech); rollback (previous version retained ≥ 12 months, one-command restore, RTO ≤ 15 min/device); drift + correction-rate monitoring.
- **Tech:** Python; MLflow 3; DVC 3; GPU node (on-demand) for fine-tuning (Unsloth/axolotl + PEFT/LoRA).
- **Interfaces:** MLflow/DVC stores (MinIO + Postgres), CI/CD, admin-console, llm-service (shadow), version_registry.
- **Scaling:** Batch/async; GPU node is on-demand (owned or rented).
- **Built in:** Phase 14 (foundation W3, hardening W5).

## 8.4 Service interaction map

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

## 8.5 Build order summary

| Phase (per §10) | Services delivered |
|---|---|
| 0 | — (governance; S23 design, S25 design) |
| 1 | S4, S7 (skeleton), S12 (print MVP), S19 (basic), S20 (basic), S23, S25 (skeleton), S22 (basic) |
| 2 | S1 (full), S2, S3 |
| 3 | S7 (full CST), S8 (index) |
| 4 | S5 (full fallback + cross-check), S1 (cross-correction UX) |
| 5 | S6, S8 (hybrid retrieval full) |
| 6 | S11 (verification engine), S9 (full gates) |
| 7 | S8 (similar-case search) |
| 8 | S13 (multimodal), S21 (multimodal), S5 (scientist voice) |
| 9 | S15 |
| 10 | S16 |
| 11 | S14, S18 (versioning/bundles), S9 (counterexample search) |
| 12 | S19 (media sync) |
| 13 | (trial: all services in supervised operation) |
| 14 | S26 (full), S22 (release management) |
| 15 | S24 (surveillance/learning dashboards), fleet scaling of S19/S20/S22 |

---

# 9. INPUT MODALITY WORKSTREAMS

**Voice, touch, text, and picture are first-class input modalities** across all channels (kiosk, WhatsApp, web, scientist portal). This section defines each modality's pipeline, per-channel behavior, failure handling, evaluation, and the phase in which it is built.

**Modality principles (apply to all four):**
1. **Convergence:** every modality produces an immutable `Input` node (modality recorded as metadata) on the same canonical case graph (§6.1). No modality has privileged access to intelligence.
2. **Mixed input:** voice, touch, text and picture may be mixed freely within one case (acceptance criterion, source §54). A farmer can start by voice at the kiosk, send a photo on WhatsApp, and answer a question by touch.
3. **Confidence is modality-aware:** touch selections carry confidence 1.0 (explicit user choice); ASR/text carry model confidence; pictures carry per-observation states. The confirmation gate (§4.9) triggers on the weakest critical entity regardless of modality.
4. **Every modality has a fallback:** if a modality fails, the case continues on the remaining modalities — never a dead end (§9.5.3).
5. **Modality is recorded end-to-end:** `case_node.source` = channel + modality; evaluation metrics are computed per modality (§9.5.4).

## 9.1 Voice workstream

### 9.1.1 End-to-end pipeline

```text
MIC ARRAY / VOICE NOTE / SCIENTIST VOICE FEEDBACK
   │
   ▼
VAD (silero-vad): speech segmentation, reject silence/noise
   │
   ▼
ffmpeg: resample 16 kHz mono WAV, loudness normalize
   │
   ▼
ASR ENGINE SELECTION (decision table, §9.1.2)
   │  Vaani-Whisper (primary) / SraVaani (fast) / BHASHINI (online cross-check)
   ▼
transcript + word-level confidence
   │
   ▼
AGRI-VOCABULARY NORMALIZATION (lexicon pass, §9.1.3)
   │
   ▼
ENTITY EXTRACTION (crop / variety / stage / pest / product / dose / location)
   │
   ▼
CONFIDENCE ASSESSMENT
   │  < θ_confirm (0.80) or critical entity ambiguous
   ▼
CONFIRMATION GATE — "I understood that the cotton leaves are curling. Is that correct?"
   │  (touch buttons with ASR candidates + voice repeat + text edit)
   ▼
Input node {modality: voice, asr: {engine, model_id, version, confidence, duration_ms}}
   │
   ▼
CASE-TO-SOLUTION TREE (S7)
```

### 9.1.2 ASR engine selection (fallback chain)

| Priority | Engine | Model / runtime | When used | Notes |
|---|---|---|---|---|
| **1 (primary)** | **Vaani-Whisper Telugu** | `ARTPARK-IISc/whisper-large-v3-vaani-telugu` (Apache-2.0, 2B) via faster-whisper int8 | Default; quality-first path | Telugu-specialized Whisper large-v3 fine-tune on the Vaani dataset; strong Telugu lexicon; standard transformers/faster-whisper usage (`chunk_length_s=30`, `forced_decoder_ids = None`) |
| **2 (fast fallback)** | **SraVaani-1.0** | `ARTPARK-IISc/SraVaani-1.0` (MIT, ~430M, ~900 MB FP16, ONNX export) | GPU busy with LLM/vision inference; latency budget tight; short utterances | FastConformer + hybrid TDT-CTC decoder; fine-tuned on ~31k hours across 65 Indian languages; Telugu WER ~25.1 (avg); fine-tunable via NeMo (github.com/ARTPARK-Speech-Models/SraVaani) |
| **3 (online)** | **BHASHINI ASR API** | Government platform (bhashini.gov.in) | Online AND (a) offline transcript confidence < 0.60, or (b) cross-check of a low-confidence transcript | Higher quality on some domains; adds network dependency; used as cross-check, not default |

**Selection logic (deterministic, in speech-service):**
1. Utterance ≤ 3 s AND GPU free → SraVaani (fast path, low latency).
2. GPU free → Vaani-Whisper (default quality).
3. GPU busy (LLM/vision job in flight) → SraVaani ONNX (CPU) — never block the farmer on GPU contention.
4. Result confidence < 0.60 AND online → BHASHINI cross-check; if the two transcripts disagree on a critical entity → confirmation gate showing both candidates.
5. Engine used is recorded on the `Input` node (`asr.engine`) — per-engine WER is tracked in §16.3.

### 9.1.3 Telugu agricultural vocabulary normalization

- **Local terminology dictionary** (`lexicon` table, §6.8): farmer/local term → normalized term, with crop + geography context (source §50.6). Covers local pest/disease names, product brand names, dose expressions, crop varieties.
- **Number/unit normalization:** "2 ml per liter" / "రెండు మిల్లీలీటర్" → `dose = 2 ml/L`; interval expressions → days.
- **Product name handling:** brand name → active ingredient via `regulatory_products` table; ambiguous or unknown brand → confirmation gate (never guess a product).
- **Corrections are learning signals:** every farmer/scientist entity correction becomes a **language-learning candidate** (lexicon mapping) — expert-validated, never a silent overwrite (§4.3.1).
- The lexicon is a **versioned artifact** (`SPEECH_VERSION` in the version tuple, §4.5.1) — released through the same pipeline as models and KB.

### 9.1.4 TTS (voice output)

| Priority | Engine | When | Notes |
|---|---|---|---|
| 1 | **Piper Telugu** (piper1-gpl, ~60 MB) | Default, offline | Sub-second synthesis on CPU; Telugu voice in Piper catalog |
| 2 | **BHASHINI TTS** | Online AND Piper MOS below threshold / long-form advisory | Higher-quality Telugu voices |
| 3 | **Text-only display** | Both unavailable | Screen always shows the full answer |

TTS text is generated from the **locked output object** (approved, rule-checked), never from raw LLM text. TTS engine + voice version are part of `SPEECH_VERSION`.

### 9.1.5 Per-channel voice

| Channel | Capture | Processing | Notes |
|---|---|---|---|
| **Kiosk** | 4-mic directional array, beamforming, 16 kHz | Edge speech-service (full chain §9.1.2) | Push-to-talk or wake-word; echo cancellation during TTS playback; mic status shown on screen |
| **WhatsApp** | Voice note (OGG/Opus) | Central speech-service (same chain) | ffmpeg → 16 kHz WAV; long notes chunked (≤ 60 s guidance) |
| **Web/mobile** | Browser MediaRecorder (optional) | Central speech-service | Progressive enhancement; text always available |
| **Scientist portal** | Voice feedback | Central speech-service → structured correction | Phase 8: ASR → structured delta with reference image attach (source §42) |

### 9.1.6 Latency budget (kiosk, target)

| Stage | Budget (10 s utterance, RTX 4060 Ti 16 GB) |
|---|---|
| VAD + ffmpeg preprocessing | < 200 ms |
| ASR — Vaani-Whisper int8 | < 3 s |
| ASR — SraVaani ONNX | < 1.5 s |
| Normalization + entity extraction | < 300 ms |
| Confirmation gate (when triggered) | user time (not counted) |
| **Total: question → first spoken response (informational)** | **< 8 s target** |
| **Total: question → printed prescription (incl. review when required)** | review SLA applies (≤ 24 h; trial: same day) |

### 9.1.7 Voice failure handling

| Failure | System behavior |
|---|---|
| No speech detected | "I didn't hear you — please try again" + touch/text mode offered |
| Low confidence (< θ_confirm) | Confirmation gate with candidate list (touch buttons) + voice repeat option |
| One ASR engine fails | Next engine in chain automatically; farmer sees no error |
| All offline engines fail | Text + touch mode; operator alert; BHASHINI if online |
| Noisy environment | Request to repeat closer to the mic; noise level shown to operator |
| TTS failure | Screen text (always rendered in parallel) |

### 9.1.8 Voice evaluation (per speech version)

- **WER/CER** on the KVK-curated **Kurnool agri-vocabulary set** (≥ 500 utterances; dialectal variation; crop/pest/product/dose/location terms; recorded with local farmers, consented).
- **Entity accuracy** per class: crop, variety, stage, pest/disease, product, dose, location.
- **Per-engine comparison report** (Vaani-Whisper vs SraVaani vs BHASHINI) — gate for engine promotion (§5.3 model selection gate).
- **TTS MOS test** with farmers (Phase 4): intelligibility + acceptability of the Piper Telugu voice.
- **ASR correction rate** in production (farmer corrections of transcripts) — continuous metric (§16.3).

## 9.2 Touch workstream

### 9.2.1 Kiosk touch flow

- **Kiosk mode:** auto-start app, no desktop escape, session timeout (auto-reset with case preserved by short code), operator PIN for maintenance.
- **Guided flow (large buttons):** language (Telugu default) → problem type (crop picker → stage picker → symptom picker, all with images) → free input (voice/text) → confirmation gates → answer display → print/QR → follow-up instructions.
- **Pickers with images:** crop/stage/pest pickers show photos — visual aids for low-literacy users; a farmer can complete an entire informational case without speaking or typing.
- **Quick-reply buttons:** every system question renders its `options[]` as buttons (source §50.2 — questions have a decision purpose and options).
- **Confirmation gates:** "Did you mean: cotton / chilli / groundnut?" rendered as large buttons with images.

### 9.2.2 Structured touch events

- Every touch action is a typed event: `{picker: crop, value: cotton, confidence: 1.0, ts}`.
- Touch is the **highest-confidence entity source** (explicit user choice) — it resolves ASR ambiguity directly.
- Touch selections update the interpretation as a **new node** (original immutable, §4.2.3).
- Touch events are `Input` nodes with `modality = touch` — fully auditable like any other input.

### 9.2.3 Touch as the disambiguation channel

- ASR confidence < θ_confirm → candidate list as buttons.
- Visual interpretation confirmation: "The photo shows yellow spots on the leaves. Is that correct?" [Yes / No / Something different].
- Contradiction resolution: "Earlier you said cotton. Now you said chilli. Which crop is this case about?" [Cotton / Chilli / Both].

### 9.2.4 Accessibility & UX (per §4.9 UX framework)

- Telugu-first; English secondary; large type (≥ 24 px equivalent), high contrast, icons + words.
- Minimal text per screen; one question at a time.
- Session persistence: farmer can step away; case continues via short code/QR (kiosk → WhatsApp → kiosk return visit).
- No dead ends: every screen offers "talk to an expert", "print what I have", "start over".
- Do-not-repeat memory enforced in the UI (answered questions never re-asked).

### 9.2.5 WhatsApp touch equivalent

- **Quick replies** (tap-to-select) for clarification questions.
- **List messages** for pickers (crop/stage) — up to 10 options.
- **Buttons** for confirmation gates (Yes/No/Other).
- Same `question.options[]` data drives both kiosk buttons and WhatsApp quick replies — one question, two renderings.

### 9.2.6 Operator & admin touch surfaces

- **Operator screen (kiosk):** device health, printer status (paper/ink), network status, session reset, offline queue size.
- **Admin console (web):** device fleet, releases, users/roles, audit, candidate queues (§8.3 S22).

## 9.3 Text workstream

### 9.3.1 Input methods

| Channel | Method |
|---|---|
| Kiosk | On-screen keyboard: **Telugu script + Latin**; optional transliteration (Latin → Telugu) |
| WhatsApp | Native text (Telugu script, Latin, or mixed) |
| Web/mobile | Chat text input |
| Scientist portal | Text notes + structured correction fields |

### 9.3.2 Text normalization pipeline

```text
RAW TEXT (Telugu / Latin / mixed)
   → script detection (te / en / mixed)
   → local terminology dictionary pass (same lexicon as voice, §9.1.3)
   → number/unit normalization
   → entity extraction (same NER as voice path — modality-agnostic)
   → normalized_query + entities{value, confidence, source: text}
   → Input node {modality: text}
```

Text and voice share the **same normalization + entity extraction code path** (only the transcript source differs) — this is what makes the modalities first-class and interchangeable (§9 principles).

### 9.3.3 WhatsApp text handling

- Phone number → `farmer_ref` → active case mapping; new text without an active case starts the case-creation flow.
- **Template constraints:** outbound messages outside the open 24-hour service window require **pre-approved templates** (India approval lead time ~2–4 weeks — start in Phase 0). Follow-up/outcome messages use **utility templates**.
- **Billing (verified, Sep 2026):** per-message billing for template messages since 1 Jul 2025; service conversations within the 24-h window free (since 1 Nov 2024); utility templates inside an open window free (since 1 Jul 2025); from 1 Oct 2026 a monthly free tier of 1,000 service messages per business number, then per-message; India bills in INR since Jan 2026 (utility ≈ ₹0.115/message); further pricing updates 1 Aug 2026 and 1 Oct 2026. The adapter tracks category per message for cost reporting.

### 9.3.4 Text safety (prompt-injection defense)

- Farmer text is **data, never instructions**: strict system/user separation in all LLM calls.
- Input sanitization + system-prompt hardening + **output schema validation** (LLM output must validate before pipeline entry, §7).
- **Regulatory data is never injected into the LLM context as instructions** — it is consumed by the rules engine only (§3.8).
- Red-team suite (10 scenarios, source §26.3) runs in CI on every build and monthly in production (§13.4).

### 9.3.5 Scientist text

- Structured correction fields: product / dose / formulation / method / timing / note (only wrong fields required, source §7).
- Free-text notes are stored as **qualitative evidence** — they never automatically become rules (§4.1.3).

## 9.4 Picture workstream

### 9.4.1 Capture & quality check

| Channel | Capture |
|---|---|
| Kiosk | Camera (1080p, privacy shutter) with **guided framing overlay** ("place the affected leaf in the frame") |
| WhatsApp | Photo upload (single or multiple) |
| Web/mobile | Photo upload |
| Scientist portal | Reference / annotated images |

**Quality check (deterministic + model, source §38.1):**
1. Is the image readable? (blur score, brightness, resolution)
2. Is the crop/plant visible?
3. Is the affected area visible?
4. Too dark / blurred / distant?
5. Is the symptom localized or widespread?
6. Is more than one plant/leaf/fruit visible?
7. Are there contextual clues?
8. Is a second image required?

Unusable image → **concrete retry instruction** ("Please take a closer photo in daylight, with the affected leaf filling the frame") — never a generic error. Quality result is stored on the `Input` node (`quality {usable, reasons[]}`).

### 9.4.2 Structured visual observations (VLM)

- **Gemma 3 12B vision** (via Ollama) produces **structured observations only** — never a final diagnosis.
- Observation types: `lesion | discoloration | insect_presence | distortion | wilting | other`.
- Each observation carries a **state**: `OBSERVED | POSSIBLE | UNCERTAIN | CONTRADICTORY | NOT_VISIBLE` (source §38.4).
- **Invariant:** a weak visual signal is never converted into a high-confidence diagnosis merely because an image exists.
- Output: `observation` nodes (§6.1.1) + candidate hypotheses fed to the hypothesis engine.

### 9.4.3 Disease/pest classifier

- **Fine-tuned ViT/ConvNeXt** (timm, PyTorch → ONNX for edge inference) on the **KVK-curated dataset** (v1: top 10–15 diseases/pests of Kurnool crops; ≥ 500 images/class; two-scientist labeling with adjudication, §13.8).
- Output: class + probability per class → one input to the hypothesis engine (not the diagnosis).
- **Why a dedicated classifier:** research (WACV 2026 HARVEST-Vision) shows open VLMs achieve only ~39–65% on fine-grained crop disease classification vs ~93% for prompted proprietary models — a domain classifier is required for reliable disease/pest ID; the VLM remains the observation extractor + hypothesis generator.
- Rationale is recorded in the model registry (CLASS-0.1.0, §5.3); per-class F1 is the promotion gate.

### 9.4.4 Media-set management (multiple photos)

- A case supports a **media set**, not a single image (source §38.3): `whole plant | affected leaf | stem | fruit/flower | pest close-up | field context`.
- The system **explicitly requests missing views**: "Please send one close photo of the affected leaf and one photo showing the whole plant."
- Do-not-repeat: already-received views are never re-requested (§4.9.7).
- Media references: `media_refs[]` on the case; each image is an immutable `Input` node + `observation` nodes.

### 9.4.5 Image → hypothesis integration (source §38.2)

```text
PHOTO → QUALITY CHECK (usable? / retry instruction)
   → VISUAL OBSERVATIONS (VLM states) + CLASSIFIER (class + probability)
   → CANDIDATE HYPOTHESES
   → COMPARE WITH TEXT / VOICE INTERPRETATION
       ├─ CONFLICT → contradiction node → clarification branch
       └─ NO CONFLICT → evidence accumulation
   → RETRIEVAL + RULES → ADVISORY / ESCALATION
```

### 9.4.6 Image privacy

- **Faces blurred by default** in stored copies (policy decision, §14.6); the original is retained only if a scientist explicitly requests it for diagnosis, with recorded consent.
- Retention: 1 year default; 5 years if flagged for diagnosis/learning with consent (§6.9).
- Media stored in MinIO with case references; edge cache encrypted at rest (LUKS).
- Surveillance use (pest incidence analytics) is aggregate and privacy-aware (source §30) — no individual farmer identification in dashboards.

### 9.4.7 Scientist reference images

- Scientists attach reference/annotated images to feedback (Phase 8, source §42).
- Annotated reference images become **diagnostic knowledge candidates** (with expert approval) — e.g., "this is what cotton leaf curl looks like at flowering in Kurnool".

### 9.4.8 Image evaluation (per vision version)

- **Quality check:** precision/recall on the KVK quality set (usable vs unusable, labeled).
- **Observation extraction:** accuracy per observation type and per state (OBSERVED/POSSIBLE/…).
- **Classifier:** F1 per disease/pest class; confusion matrix reviewed by scientists.
- **Multi-photo request success rate:** fraction of requested missing views actually received.
- **Image quality failure rate** in production (§16.3).

## 9.5 Cross-modality integration

### 9.5.1 Mixed input within a case

- Acceptance criterion (source §54): "Voice, text and image can be mixed within the same case."
- Each input is an immutable `Input` node with `modality` metadata; the contradiction detector runs **across modalities** (e.g., voice says cotton, photo suggests chilli → clarification branch, source §37.3).
- The case tree answers: what the farmer said (voice), what they selected (touch), what they typed (text), what the images show (picture) — all side by side, all immutable.

### 9.5.2 Modality routing table

| Input | Channel | Processor | Resulting nodes |
|---|---|---|---|
| Voice (kiosk) | Kiosk | speech-service (edge) | `input{modality: voice}` + `interpretation` |
| Voice note | WhatsApp | speech-service (central) | `input{modality: voice}` + `interpretation` |
| Touch picker / button | Kiosk / WhatsApp | input-orchestrator (direct) | `input{modality: touch}` (confidence 1.0) |
| Text | Any | text normalizer | `input{modality: text}` + `interpretation` |
| Photo | Any | image-service | `input{modality: picture}` + `observation[]` + candidate hypotheses |
| Scientist voice feedback | Portal | speech-service → structured correction | `scientist_feedback{modality: voice}` + `decision_delta` |
| Scientist annotated image | Portal | image-service (reference mode) | `scientist_feedback{modality: annotated_image}` + knowledge candidate |

### 9.5.3 Modality failure matrix (no dead ends)

| Failure | Fallback |
|---|---|
| Mic failure | Touch + text mode (full guided flow works without voice) |
| Camera failure | Voice + text; "send a photo on WhatsApp" option |
| All ASR engines fail | Text + touch; operator alert |
| TTS failure | Screen text (always rendered in parallel) |
| Printer failure | QR + screen + WhatsApp delivery of the same locked output |
| Network down | Full local pipeline on edge (offline-first, §3.4) |
| WhatsApp down | Kiosk + web channels continue the case (case continuity) |

### 9.5.4 Modality KPIs (per §16.3)

| Modality | Key metrics |
|---|---|
| Voice | ASR confidence (mean/p50/p95), ASR correction rate, per-engine WER on agri-vocab set, TTS MOS, voice share of inputs |
| Touch | Picker accuracy (selection vs final interpretation), touch completion rate (cases completed with ≤ 1 free input), quick-reply usage |
| Text | Text entity accuracy, transliteration usage, text share of inputs |
| Picture | Image quality failure rate, observation accuracy, classifier F1 per class, multi-photo request success rate, picture share of inputs |
| Cross | **Mixed-case ratio** (cases using ≥ 2 modalities), cross-modal contradiction rate, per-modality first-contact resolution |

## 9.6 Modality workstream plan

| Workstream | Phase(s) | Key deliverables |
|---|---|---|
| Voice — basic | 1 (W1), 4 | ASR chain (Vaani-Whisper + SraVaani), Piper TTS, confirmation gates, latency SLOs |
| Voice — cross-check | 4 | BHASHINI online cross-check, candidate-list UX |
| Voice — scientist | 8 | Scientist voice feedback → structured delta |
| Touch — kiosk MVP | 1 (W1) | Guided flow, pickers with images, print, kiosk mode |
| Touch — WhatsApp | 2 | Quick replies, list messages, buttons |
| Text | 1 (W1) | Telugu/Latin keyboard, normalization, lexicon v1, WhatsApp text mapping |
| Picture | 5 | Quality check, VLM observations, ViT classifier v1, media sets, face blur |
| Cross-modality | 3, 4 | Contradiction detection across modalities, mixed-case acceptance tests |

---

# 10. PHASED IMPLEMENTATION ROADMAP

## 10.1 Roadmap structure

- **Duration:** 18 months (M1 = Oct 2026 … M18 = Mar 2028), 5 waves, 16 phases (0–15).
- **Phase spine:** the 16 phases are the v2 revised implementation roadmap (source §53). The v1 roadmap's workstreams (knowledge base, rules, kiosk MVP, AI/RAG, scientist portal, offline core — source §32) run **in parallel as workstreams (WS-\*)** inside the waves; they are not separate phases.
- **Phase gates:** a phase is complete only when its exit criteria are met **and verified** (automated test report + stakeholder sign-off recorded in the version registry). No phase starts before its dependencies' exit criteria are met (overlaps in the Gantt are planned, not speculative).
- **Change control:** after M3 (schema freeze) and during the trial (M10–M13), changes to production artifacts go through the release framework (§4.5) — the trial runs on frozen versions.

**Waves (per §1.5):**

| Wave | Months | Phases | Theme |
|---|---|---|---|
| W1 — Foundation | M1–M3 | 0, 1 (+ WS-KB, WS-RULES, WS-KIOSK) | Governance, canonical schema, platform skeleton, kiosk MVP (touch+text+print), KB v1, rules v1 |
| W2 — Intelligence | M3–M8 | 2, 3, 4, 5, 6, 7, 8 (+ WS-AI, WS-VOICE, WS-PORTAL) | Channels, Case-to-Solution Tree, cross-correction, image pipeline, verification, similar cases, scientist multimodal feedback |
| W3 — Closed loop | M7–M10 | 9, 10, 11, 12, 14-foundation (+ WS-OFFLINE) | Outcome/follow-up, escalation, learning sandbox, offline media sync, MLOps foundation |
| W4 — Trial | M10–M13 | 13 | Three-month scientist-supervised trial |
| W5 — Production & scale | M13–M18 | 14-hardening, 15 | MLOps/KnowledgeOps hardening, multi-kiosk, multi-channel scale, ops handover |

**Parallel workstreams:**

| Workstream | Waves | Content |
|---|---|---|
| WS-KB — Knowledge base | W1–W2 | KB v1 for Kurnool crops (cotton, paddy, groundnut, maize, arhar, castor, foxtail/barnyard millet, chilli + horticulture): ingestion, expert review, structured records + passages, test cases, evidence ledger, versioning |
| WS-RULES — Rules engine | W1–W2 | PPQS/CIB&RC regulatory data (banned/refused/restricted, effective 31 Mar 2024 + gazette updates), dose/PHI/PPE rules, application method, weather-window rules (IMD), confidence gates, clarification policy |
| WS-KIOSK — Kiosk MVP | W1 | Touch + text + print + basic voice: information workflow end-to-end (v1 Phase 4 exit) |
| WS-AI — AI/RAG | W2 | Local LLM (Gemma 3 12B) + hybrid retrieval (BGE-M3 + reranker): grounded structured answers (v1 Phase 5 exit) |
| WS-VOICE — Voice | W2 | Full voice pipeline: Vaani-Whisper + SraVaani fallback, Piper TTS, confirmation gates, latency SLOs |
| WS-PORTAL — Scientist portal | W2 | Approve/correct/escalate with minimal input (v1 Phase 6 exit) |
| WS-OFFLINE — Offline core | W3 | Local execution + encrypted sync: core service works without network (v1 Phase 8 exit) |

## 10.2 Phase details

### Phase 0 — Governance, safety, escalation policy

- **Objective:** establish the authority, safety, data, source and escalation policies that everything else builds on; start long-lead external dependencies.
- **Key tasks:**
  - Draft and sign the governance specification (roles, authority, approval matrix, §4.1).
  - Safety policy: risk tiers, blocking-rules inventory, prohibited-output list, PHI/PPE defaults, weather-window policy.
  - Data policy: consent design, retention schedule, PII minimization, DPDP mapping, media handling (face-blur decision).
  - Source policy: authoritative source hierarchy (§4.6.1).
  - Escalation policy: L0–L4 triggers, SLAs, institutional response owners.
  - Trial protocol: supervision level per month, metrics, exit criteria, institutional approval gates.
  - **DPDP compliance program kickoff:** grievance officer, consent capture design, breach-response process, retention automation (full fiduciary obligations effective May 2027 — must be complete before trial, §14.4).
  - **IMD API access:** IP-whitelisting application + attribution arrangement (long-lead; start week 1).
  - **WhatsApp:** BSP selection, Meta business verification, template drafting (India approval ~2–4 weeks; start week 1).
- **Deliverables:** signed governance specification; safety policy; data policy; source policy; trial protocol; DPDP program plan; IMD/WhatsApp access requests submitted.
- **Exit criteria:** approved governance — KVK/ANGRAU sign-off recorded; all policy documents in version control; IMD + WhatsApp requests submitted with tracking.
- **Duration:** M1 (4 weeks, overlaps team onboarding).
- **Dependencies:** institutional stakeholders (KVK, ANGRAU Extension Directorate).
- **Key risks:** institutional approval latency (mitigation: early engagement, single approval path via ANGRAU); DPDP timeline pressure (mitigation: program starts M1, not M9).

### Phase 1 — Canonical multimodal case schema + platform skeleton

- **Objective:** text/voice/picture represented identically in one canonical schema; the platform skeleton is live; hardware ordered.
- **Key tasks:**
  - Case graph schema (CST) per §6: case, case_node (all node types), media, decisions, decision_deltas, evidence_ledger, kb_entries/passages, rules, learning_candidates, version_registry, prescriptions, devices/sync, weather_snapshots, regulatory_products, lexicon.
  - Pydantic v2 models + OpenAPI; ULID IDs; append-only invariants enforced by DB triggers.
  - input-orchestrator (S4) + case-service (S7) skeleton; version registry + version-tuple recording.
  - Platform skeleton: monorepo, CI/CD (GitHub Actions), Docker, K3s central cluster, PostgreSQL 17 + pgvector, Keycloak, OpenTelemetry, MinIO, Redis, EMQX, Caddy.
  - Kiosk device procurement (hardware lead time — order in M1, §12.1).
  - **Evaluation sets kickoff (KVK-curated):** Telugu agri-vocabulary ASR set (≥ 500 utterances), KB retrieval set, disease/pest image set (labeling plan), Telugu QA set.
  - Kiosk MVP build (WS-KIOSK): touch guided flow + text + print + basic voice (information workflow).
  - KB v1 ingestion start (WS-KB); rules v1 start (WS-RULES: regulatory data parsing first).
- **Deliverables:** schema v1.0 (frozen at M3); core-api skeleton; CI/CD green; central platform live; kiosk hardware ordered; evaluation-set plan + labeling guidelines; kiosk MVP demo (information workflow).
- **Exit criteria:** (a) text/voice/picture representable identically — automated test builds the same case from each modality; (b) complete workflow representable structurally (v1 Phase 1 exit); (c) kiosk MVP: information workflow works end-to-end (touch+text+print, v1 Phase 4 exit).
- **Duration:** M1–M3.
- **Dependencies:** Phase 0 (data policy, consent design); hardware lead time.
- **Key risks:** schema churn (mitigation: freeze at M3; later changes via release framework); hardware delay (mitigation: order M1, spec-locked BOM §12.1).

### Phase 2 — Channel adapters

- **Objective:** kiosk + web + WhatsApp enter the same case service; a case can move between channels without losing context.
- **Key tasks:**
  - Kiosk adapter (S1) full: session, all four input modalities wired, output rendering (screen/TTS/print), offline queue visibility.
  - Web adapter (S3): PWA chat, photo upload, QR/short-code case lookup, outcome reporting.
  - WhatsApp adapter (S2): webhook, media download, phone → farmer_ref → case mapping, outbound rendering (text/quick replies/list/media), template management, billing tracking.
  - Case continuity: durable `case_id` + short code + QR; cross-channel continuation (kiosk → WhatsApp → kiosk return visit).
  - Channel-agnostic output rendering: one canonical output → per-channel rendering (text/voice/card/print).
- **Deliverables:** three adapters live in staging; cross-channel continuation demo; WhatsApp templates approved (or in approval with fallback plan).
- **Exit criteria:** kiosk + web + WhatsApp enter the same case service (acceptance: same case schema across channels; a case moved between channels retains full context — automated test).
- **Duration:** M3–M5.
- **Dependencies:** Phase 1; WhatsApp business verification (started Phase 0).
- **Key risks:** WhatsApp template approval delay (2–4 weeks) — mitigation: started in Phase 0; kiosk-first trial operation if templates slip; Meta policy changes (pricing updates Aug/Oct 2026) — mitigation: adapter isolates billing logic, cost dashboard.

### Phase 3 — Case-to-Solution Tree

- **Objective:** every case has hypotheses, evidence, questions and decisions — the tree is the system's working model.
- **Key tasks:**
  - CST state machine implementation (§4.2.2) with transition guards + invariant tests.
  - Hypothesis engine: competing hypotheses, supporting/contradicting/missing evidence per hypothesis.
  - Question engine: decision purpose per question, ≤ 3 questions per branch, do-not-repeat memory.
  - Contradiction detector (across modalities, source §37.3).
  - Interpretation + uncertainty record ("I may have understood this incorrectly", source §37.1).
  - Case embedding index (similar-case foundation, Phase 7).
- **Deliverables:** case-service v1 (full tree semantics); state-machine test suite; contradiction test suite; golden-case corpus (≥ 50 scripted cases across crops/modalities).
- **Exit criteria:** every case has hypotheses/evidence/questions/decisions — verified on the golden-case corpus (automated); contradictions force a clarification branch (test).
- **Duration:** M4–M6.
- **Dependencies:** Phase 1; WS-AI retrieval (partial — retrieval-service skeleton).
- **Key risks:** hypothesis quality depends on KB coverage — mitigation: KB v1 frozen by M5 (WS-KB gate); question quality — mitigation: reason-for-question engine + UAT with farmers (M6).

### Phase 4 — Cross-correction

- **Objective:** the farmer can correct the transcript, entities, and visual interpretation — and the system learns from the correction.
- **Key tasks:**
  - InterpretationCorrection object + APIs (source §37.2); original interpretation immutable.
  - Confirmation-gate UX: touch candidate buttons, voice "Is that correct?", text edit.
  - ASR candidate lists (engine cross-check: Vaani-Whisper vs SraVaani vs BHASHINI when online).
  - Visual interpretation confirmation ("The photo shows yellow spots on the leaves. Is that correct?").
  - Lexicon correction capture → language-learning candidates (never silent overwrite).
  - WS-VOICE completion: full ASR fallback chain + Piper TTS + latency SLOs met.
- **Deliverables:** cross-correction live on kiosk + WhatsApp; lexicon v1 (≥ 500 validated mappings); per-engine ASR benchmark report (Kurnool agri-vocab set); TTS MOS test report.
- **Exit criteria:** farmer can correct transcript/entity/visual interpretation; original input and corrected interpretation both retained (automated test); ASR entity accuracy on agri-vocab set meets the framework threshold (or fallback chain + confirmation gates verified as compensating control).
- **Duration:** M5–M7.
- **Dependencies:** Phase 3; WS-VOICE.
- **Key risks:** ASR accuracy on local dialect below threshold — mitigation: SraVaani fallback, BHASHINI cross-check, confirmation gates, lexicon growth loop; if still below threshold at M7, domain fine-tune of IndicWav2Vec/SraVaani (NeMo) is the pre-approved next step (ASR-0.2.0, §5.3).

### Phase 5 — Image evidence pipeline

- **Objective:** photos become governed evidence: quality checks + structured observations + classifier, without forcing a diagnosis.
- **Key tasks:**
  - Image quality check (deterministic + model) with concrete retry instructions (source §38.1).
  - Gemma 3 vision structured observations (OBSERVED/POSSIBLE/UNCERTAIN/CONTRADICTORY/NOT_VISIBLE) via Ollama.
  - ViT/ConvNeXt classifier: KVK dataset v1 (top 10–15 diseases/pests; ≥ 500 images/class; two-scientist labeling + adjudication), training on GPU node, ONNX export for edge.
  - Media-set management + explicit missing-view requests (source §38.3).
  - Image → hypothesis integration (conflict → clarification branch, source §38.2).
  - Face-blurring pipeline for stored media (§9.4.6).
- **Deliverables:** image-service v1; classifier v1 with per-class F1 report; media-set UX on kiosk + WhatsApp; KVK image dataset v1 (DVC-versioned).
- **Exit criteria:** quality checks + structured observations live; images create structured observations **without forcing a diagnosis** (automated test: weak-signal images produce UNCERTAIN/NOT_VISIBLE, never high-confidence diagnosis); classifier F1 per class meets the framework threshold on the holdout set.
- **Duration:** M5–M8.
- **Dependencies:** Phase 3; GPU node; KVK image curation (starts M4 — labeling is the long pole).
- **Key risks:** dataset size/quality (mitigation: two-scientist labeling, augmentation, start with top 10–15 classes, expand in W5); VLM observation latency on edge GPU (mitigation: batched queue, classifier-first fast path).

### Phase 6 — Verification engine

- **Objective:** an apparently obvious first-message solution still passes the required verification gates (source §40).
- **Key tasks:**
  - Risk-tiered verification: low-risk information → direct answer when evidence unambiguous; diagnosis support → minimal cross-check (hypothesis + alternative check + ≥ 1 targeted question); high-risk → full gate (case completeness + evidence support + contradiction check + regulatory + agronomic + weather + similar-case check + scientist approval).
  - Gate orchestration in advisory-service (S11); gate outcomes recorded on the decision node (`rules_evaluated[]`).
  - Similar-case evidence check with **differences visible** (never blind copy, source §40).
  - Prompt-injection red-team suite (10 scenarios, source §26.3) wired into CI as a blocking gate.
  - WS-AI completion: grounded structured answers (evidence-ID retention end-to-end) — v1 Phase 5 exit.
- **Deliverables:** verification engine v1; red-team suite green in CI; grounded-answer test report (evidence-ID retention 100%).
- **Exit criteria:** first-message solutions still pass required checks (automated test: an "obvious" prescription case is held at the review gate; an "obvious" information case answers directly with evidence); blocked interventions cannot reach printable state (test).
- **Duration:** M6–M8.
- **Dependencies:** Phase 3; WS-RULES (full rule set); WS-AI.
- **Key risks:** over-verification → farmer friction (mitigation: risk-tiered gates, ≤ 3 questions, UAT latency/friction measurement); rule coverage gaps (mitigation: blocking-rule inventory from Phase 0 safety policy is the minimum; gaps surface as REVIEW, not silent pass).

### Phase 7 — Similar-case service

- **Objective:** validated cases (including failed ones) are retrieved with differences visible — supporting and conflicting evidence for the current case.
- **Key tasks:**
  - CaseSimilarityService: case embeddings (BGE-M3) + structured comparison (crop, variety, stage, geography, season, symptom pattern, image observations, weather, previous intervention, outcome).
  - Failed-case retention as **negative evidence** (prevents repeating a failed recommendation under similar conditions, source §41).
  - Similar-case display: similarity score + explicit differences + supporting/conflicting evidence.
  - Seed the index with KVK historical cases (anonymized, consented) to avoid cold start.
- **Deliverables:** similar-case service v1; golden-set evaluation (NDCG@10 on curated similar-case pairs); seeded index.
- **Exit criteria:** validated cases retrieved with differences visible (automated test on golden set); failed cases retrievable and marked as negative evidence (test).
- **Duration:** M7–M8.
- **Dependencies:** Phase 3 (case embedding index); Phase 5 (image observations in comparison).
- **Key risks:** cold start (mitigation: KVK historical case seeding, M7); similarity false positives (mitigation: structured filters before vector search; differences always shown).

---

### Phase 8 — Scientist multimodal feedback

- **Objective:** scientists can approve/correct/escalate using voice, text, image or structured fields — and every feedback becomes a structured decision delta with the full context auto-attached.
- **Key tasks:**
  - Review queue (scientist portal + WhatsApp notifications): prescriptions + uncertain cases, SLA-tracked (≤ 24 h; trial: same day).
  - Minimal-field correction UX (source §7): scientist changes **only the wrong fields**; system auto-attaches the complete context snapshot (case, language, input, crop, problem, location, weather, soil, previous management, knowledge, rules, AI, scientist, output, audit).
  - Decision-delta creation + classification (10 types, §4.3.2) + evidence status (EVIDENCE_BACKED / LOCALLY_VALIDATED / EXPERT_PREFERENCE).
  - Scientist **voice** feedback: ASR → structured correction ("The diagnosis is not correct. This looks more like X under these field conditions.").
  - Scientist **image / annotated image** attachment (reference images → diagnostic knowledge candidates).
  - WS-PORTAL completion: approve/correct/escalate with minimal input (v1 Phase 6 exit).
- **Deliverables:** scientist portal v1 (multimodal); delta pipeline; context-snapshot completeness test (all 15 snapshot categories non-null or N/A); review SLA dashboard.
- **Exit criteria:** voice/text/image feedback creates structured deltas (automated test per modality); scientist changes only the fields that are wrong (UAT with ≥ 3 KVK scientists); original AI decision never overwritten (test).
- **Duration:** M6–M8.
- **Dependencies:** Phase 3; WS-PORTAL; WS-VOICE (scientist voice path).
- **Key risks:** scientist adoption (mitigation: UAT from M6, minimal UX, WhatsApp fallback for field use); review bottleneck (mitigation: queue prioritization by risk + SLA, same-day policy in trial month 1).

### Phase 9 — Outcome / follow-up engine

- **Objective:** advice delivered ≠ problem solved — every applicable intervention can be marked worked / partial / failed / worsened / unknown.
- **Key tasks:**
  - Follow-up scheduling from **approved advisory protocols** (per-intervention windows, not arbitrary fixed intervals, source §43.1).
  - Outcome capture across channels: kiosk return visit, WhatsApp message, extension worker, scientist portal.
  - Expected-observation tracking (what should be visible by the follow-up date).
  - **Failed-solution protocol** (source §43.2): failure reported → stop automatic repetition → reassess case → request new evidence (photo, symptoms, treatment details, timing, environment) → compare original vs current case → check alternative hypotheses → escalate if triggers met.
  - Failure learning records (source §43.3) with `failure_class` enum.
- **Deliverables:** outcome-service v1; follow-up scheduler; failure-protocol test suite; follow-up templates (WhatsApp utility + kiosk flow).
- **Exit criteria:** advice can be marked worked/failed/uncertain (automated test per outcome class); **failed interventions do not automatically trigger another intervention** (test: failed case produces reassessment + evidence request, never an auto-re-prescription); every applicable intervention has a follow-up (test).
- **Duration:** M7–M9.
- **Dependencies:** Phase 3; Phase 2 (channels for follow-up delivery).
- **Key risks:** farmer follow-up response rate (mitigation: WhatsApp + worker channels, protocol-based timing matched to agronomy, kiosk return-visit prompt on next visit); outcome ambiguity (mitigation: "cannot determine" is a first-class outcome, not a failure to report).

### Phase 10 — Escalation engine

- **Objective:** failed, uncertain and high-risk cases reach humans with a complete handoff — and the farmer never experiences a dead end.
- **Key tasks:**
  - EscalationEngine L0–L4 (§4.4) with evidence- and policy-driven triggers (repeated contradictory information; image cannot distinguish alternatives; treatment failed; severity increasing; suspected regulatory issue; novel symptom; possible harmful recommendation; scientist disagreement; missing critical information).
  - Assignment + status workflow `OPEN → ASSIGNED → INVESTIGATING → RESOLVED → LEARNING_CAPTURED`.
  - Compact human-handoff packet (source §49): case summary, media, interpretation, contradictions, hypotheses, evidence, previous treatments, weather, AI recommendation, reason for escalation.
  - Farmer-facing transparency: case ID + status + concrete next steps (send another photo, voice explanation, wait for expert, visit center).
  - SLA tracking + alerts (L2 ≤ 24 h; L3 ≤ 48 h per institutional policy; L4 immediate + incident process, §14.7).
- **Deliverables:** escalation-service v1; handoff packet template; SLA dashboard; L4 incident runbook.
- **Exit criteria:** failed/uncertain/high-risk cases reach humans (automated test on the full trigger matrix); every escalation has an ID + status (test); farmer receives next-steps message on every escalation (test).
- **Duration:** M8–M10.
- **Dependencies:** Phase 9 (failure triggers); Phase 8 (scientist queue).
- **Key risks:** SLA breach during trial (mitigation: same-day review policy month 1, queue alerts, backup reviewer); L4 under-reporting (mitigation: rule-block + safety metrics feed the L4 trigger automatically, not just human judgment).

### Phase 11 — Learning sandbox

- **Objective:** corrections + outcomes become governed candidates — knowledge, rule, training or language — with full provenance; nothing reaches production unvalidated.
- **Key tasks:**
  - Correction classifier (10 delta types) + routing to learning channels (§4.3.1).
  - Candidate generation: knowledge candidates (with source verification), rule candidates (IF/THEN + scope), training examples (error classes appropriate for model learning), lexicon mappings.
  - Provenance ledger: all 11 fields (§4.3.3) non-null or explicitly N/A — enforced at ingestion.
  - Learning sandbox pipeline: data quality → regression → safety → counterexample → holdout (source §10).
  - Pattern discovery (source §20): group validated corrections by crop/stage/problem/region/season; min support N≥5, consistency ≥80%; counterexample search must find zero blocking counterexamples; candidate status is always CANDIDATE, never PRODUCTION.
  - Scientist candidate-review workflow (portal + admin console).
  - KB versioning + signed edge bundles operational (with S18); rules counterexample search (with S9).
- **Deliverables:** learning-service v1; sandbox pipeline; provenance audit report (100% completeness on sampled candidates); first pattern-discovery run report.
- **Exit criteria:** corrections + outcomes become governed candidates (automated test: every correction classified and routed; every candidate has complete provenance); **no automatic production change** (test: candidate promotion requires explicit approval + validation report); case memory, knowledge, rules and training data remain separate (test, source §46 table).
- **Duration:** M8–M10.
- **Dependencies:** Phase 8 (deltas); Phase 9 (outcomes).
- **Key risks:** candidate quality / noise (mitigation: provenance completeness gate, two-scientist agreement for high-risk labels); pattern false positives (mitigation: counterexample search is blocking, min-support thresholds tunable by governance).

### Phase 12 — Offline media synchronization

- **Objective:** images and audio queue on the edge and sync safely — offline operation is complete, not just for text.
- **Key tasks:**
  - Media queue (edge): audio/image storage with size caps, LUKS encryption, LRU eviction policy, telemetry on queue depth.
  - Resumable chunked uploads; idempotent by media ID; gap detection and repair.
  - Sync compactor (central): dedup, compaction, retention application.
  - **Offline behavior matrix validation** (source §18): approved information from cache; basic AI explanation local; rules local; printing available; live weather marked STALE; new knowledge queued; scientist review queued/blocked per policy; analytics queued locally.
  - Interrupted-sync tests: network drop mid-upload, device restart during sync, resume without duplication.
- **Deliverables:** sync v2 (media); offline test suite (all matrix rows green); storage policy + alerts.
- **Exit criteria:** images/audio queue and sync safely (automated test: kill network mid-upload → reconnect → complete, no duplication, no loss); core service works without network (v1 Phase 8 exit — full offline matrix green); interrupted sync resumes without duplication (test).
- **Duration:** M9–M10.
- **Dependencies:** WS-OFFLINE (offline core: local execution + event sync); Phase 5 (media types).
- **Key risks:** edge storage exhaustion (mitigation: size caps, LRU, telemetry alerts, operator runbook); sync conflicts (mitigation: append-only + idempotency keys — conflicts are structurally impossible for case data; media dedup by content hash).

### Phase 13 — Three-month supervised trial

- **Objective:** controlled supervised operation that establishes the baseline + outcome dataset — the trial is a controlled expert-learning program, not merely a kiosk test (source §35).
- **Key tasks:**
  - **Pre-trial (M10):** all knowledge/rules/model/prompt/speech versions **frozen** for baseline; benchmark case suite run; safety test suite green; UAT with farmers (Telugu comprehension, task completion); trial dashboard live; change-freeze policy in force.
  - **Month 1 (M11):** scientist reviews **every prescription and uncertain case** — capture broad correction dataset.
  - **Month 2 (M12):** continue full oversight; analyze recurring correction patterns; first learning candidates generated (sandbox, not production).
  - **Month 3 (M13):** confidence-based routing **only if the institution approves** (measured performance + institutional sign-off, source §6).
  - Daily metrics during trial; weekly review (KVK + platform team); monthly report to institution.
  - Trial exit review: metrics vs acceptance criteria (§10.5); go/no-go for governed production.
- **Deliverables:** trial dataset (cases, corrections, outcomes — DVC-versioned); baseline metrics report; monthly trial reports (×3); trial exit report with institutional recommendation.
- **Exit criteria:** baseline + outcome dataset established (volume + quality thresholds per trial protocol); trial acceptance criteria (§10.5) met or gaps documented with remediation plan; institutional go/no-go recorded.
- **Duration:** M10–M13 (3 months).
- **Dependencies:** Phases 0–12 complete; DPDP program complete (full fiduciary obligations effective May 2027 — trial starts Jul 2027, compliant by design).
- **Key risks:** trial contamination (version changes during trial) — mitigation: freeze + change-freeze policy + version-tuple audit; scientist bottleneck — mitigation: review SLA, queue prioritization, backup reviewer; low farmer participation — mitigation: KVK outreach, operator assistance, WhatsApp channel; **three months is a trial duration, not automatic authorization for unsupervised prescriptions** (source §6) — any oversight reduction requires measured performance + institutional approval.

### Phase 14 — MLOps / KnowledgeOps

- **Objective:** candidates are testable, versioned and rollbackable — the full release pipeline (§4.5) is operational and proven.
- **Key tasks (foundation, M9–M11):**
  - MLflow 3 registry + DVC 3 dataset versioning operational (models, datasets, experiments).
  - Evaluation runners in CI: RAGAS (retrieval/groundedness), DeepEval (app eval), promptfoo (red-team, blocking), lm-evaluation-harness (model benchmarks).
  - Shadow-mode orchestration (candidate model on live cases, hidden output, compared vs production + scientist decisions; exit criteria: no safety regression, correction rate not worse, groundedness ≥ baseline).
  - Canary orchestration (device/case subsets).
  - Signed bundle pipeline: model / KB / rules / prompt policy / speech — content-addressed (SHA-256) + signed (minisign/cosign).
  - Rollback: previous production version retained ≥ 12 months; one-command restore; RTO ≤ 15 min/device.
- **Key tasks (hardening, M13–M16):**
  - **First governed release cycle end-to-end:** promote at least one knowledge candidate and one rule candidate through shadow → canary → production (proves the pipeline, not just the components).
  - Drift monitoring (model drift, correction-rate trend, retrieval recall decay).
  - Release cadence established (KB: monthly; rules: per regulatory update + quarterly audit; models: per evaluation gate).
  - Fine-tuning pipeline proven on GPU node (Unsloth/axolotl + LoRA) — first candidate model (if trial data justifies it) through the full gate sequence (source §21: 13 steps, no fine-tuning before the structured system is stable).
- **Deliverables:** mlops-service v1; release pipeline; first governed release (KB + rule); rollback drill report; fine-tuning runbook.
- **Exit criteria:** candidates testable, versioned and rollbackable (automated test: full shadow → canary → production → rollback cycle on a staging device); previous production version restorable (drill, RTO ≤ 15 min); no candidate can publish without validation + approval (test).
- **Duration:** M9–M11 (foundation) + M13–M16 (hardening).
- **Dependencies:** Phase 11 (candidates); GPU node; trial data (for first model candidate, M13+).
- **Key risks:** fine-tuning infrastructure (mitigation: owned GPU node or rented A100/4090 — decision at M9); release pipeline complexity (mitigation: KB/rules releases first (simpler), model releases after the first two cycles).

### Phase 15 — Multi-channel scale

- **Objective:** the same intelligence across kiosk/WhatsApp/web — and a repeatable path to multi-kiosk district scale.
- **Key tasks:**
  - Multi-kiosk deployment: device management at fleet scale (provisioning, version distribution, health, decommissioning); second kiosk deployed as the scale proof (or district-ready deployment package if the institution defers hardware).
  - Channel parity verification: identical case outcomes across channels for the same inputs (automated parity suite).
  - Scale testing: load (concurrent farmers), sync (N devices), retrieval (KB growth), review queue (scientist throughput).
  - District-ready architecture review against source §31 levels (Level 2 KVK/multi-kiosk → Level 4 district): common contract (case schema, knowledge/rule/model versions, device identity, sync protocol, audit trail).
  - Operations handover: runbooks (§17.4), operator + scientist training, SLOs, on-call rotation, DPDP operational compliance check.
  - Final documentation + audit (prescription → version-tuple traceability sample; learning provenance sample; security audit).
- **Deliverables:** second kiosk (or district-ready package); scale test report; channel parity report; operations handover package; final audit report.
- **Exit criteria:** same intelligence across kiosk/WhatsApp/web (automated parity test); repeatable multi-kiosk deployment (v1 Phase 11 exit — second device provisioned + synced + serving in < 1 day); audit sample: 100% of sampled prescriptions trace to model/KB/rule versions.
- **Duration:** M15–M18.
- **Dependencies:** Phase 14 (release pipeline); Phase 13 exit (institutional go-ahead).
- **Key risks:** scope creep ("district scale" = architecture ready + 2nd kiosk, not N kiosks — mitigation: explicit exit criteria); operational ownership ambiguity (mitigation: handover package signed by KVK + ANGRAU in M17).

## 10.3 Gantt (M1–M18)

```text
Phase / Workstream          M1  M2  M3  M4  M5  M6  M7  M8  M9  M10 M11 M12 M13 M14 M15 M16 M17 M18
─────────────────────────────────────────────────────────────────────────────────────────────────
P0  Governance              ██
P1  Schema + skeleton       ██  ██
WS-KB  Knowledge v1         ██  ██  ██
WS-RULES Rules v1           ██  ██  ██
WS-KIOSK Kiosk MVP              ██  ██
P2  Channel adapters              ██  ██
P3  Case-to-Solution Tree           ██  ██
WS-AI  AI/RAG                       ██  ██  ██
WS-VOICE Voice                        ██  ██
P4  Cross-correction                    ██  ██
P5  Image evidence pipeline               ██  ██  ██
WS-PORTAL Scientist portal                ██  ██  ██
P6  Verification engine                       ██  ██
P7  Similar-case service                          ██
P8  Scientist multimodal feedback                 ██  ██
P9  Outcome / follow-up                             ██  ██
P10 Escalation engine                                  ██  ██
P11 Learning sandbox                                     ██  ██
WS-OFFLINE Offline core                                  ██  ██
P12 Offline media sync                                       ██
P14 MLOps foundation                                         ██  ██
─────────────────────────────────────────────────────────────────────────────────────────────────
P13  TRIAL (3 months, frozen versions)                        ██  ██  ██
─────────────────────────────────────────────────────────────────────────────────────────────────
P14 MLOps hardening                                              ██  ██  ██
P15 Multi-channel scale                                              ██  ██  ██
─────────────────────────────────────────────────────────────────────────────────────────────────
Waves:  |── W1 ──|─── W2 ─────────────|── W3 ──|── W4 ──|────── W5 ──────────|
```

**Reading the Gantt:** W2 phases overlap by design (e.g., P5 image pipeline runs while P4 cross-correction finishes) — each phase's start is gated on its *dependencies'* exit criteria, not on calendar month. The trial (P13) starts only when P0–P12 exit criteria are all met and verified.

## 10.4 Milestones

| ID | End of | Milestone | Verified by |
|---|---|---|---|
| MS1 | M1 | Governance approved; team assembled; central platform skeleton live; IMD/WhatsApp requests submitted | Phase 0 exit sign-off |
| MS2 | M3 | Kiosk MVP demo (touch+text+print, information workflow); schema v1 frozen; KB v1 + rules v1 frozen for benchmark; hardware ordered | Phase 1 exit + WS-KB/WS-RULES/WS-KIOSK gates |
| MS3 | M5 | Three channels → same case service; cross-channel continuation demo; CST operational | Phase 2 + Phase 3 (partial) exit |
| MS4 | M8 | Full v2 intelligence stack (cross-correction, image pipeline, verification, similar cases, scientist multimodal feedback); **trial readiness review (go/no-go)** | Phases 4–8 exit + red-team suite green |
| MS5 | M10 | Closed loop complete (outcome, escalation, learning sandbox, offline media sync) + MLOps foundation; **trial start** | Phases 9–12 exit + trial protocol sign-off |
| MS6 | M13 | Trial complete: baseline + outcome dataset; monthly reports; **institutional go/no-go for governed production** | Phase 13 exit + trial acceptance criteria (§10.5) |
| MS7 | M16 | MLOps/KnowledgeOps hardened; first governed release cycle complete (KB + rule); rollback drill passed | Phase 14 exit |
| MS8 | M18 | Multi-channel scale; second kiosk (or district-ready package); operations handover signed; final audit | Phase 15 exit |

## 10.5 Acceptance criteria traceability (source §54)

| Area | Acceptance criterion | Verified in |
|---|---|---|
| Input understanding | Farmer can correct a transcript or normalized interpretation | Phase 4 exit (automated + UAT) |
| Input understanding | Original input and corrected interpretation both retained | Phase 4 exit (append-only test) |
| Input understanding | Images create structured observations without forcing a diagnosis | Phase 5 exit (weak-signal test) |
| Input understanding | Multiple images can belong to one case | Phase 5 exit (media-set test) |
| Input understanding | Voice, text and image can be mixed within the same case | Phase 3/4 exit (mixed-case test) + Phase 15 parity |
| Reasoning | Multiple hypotheses maintained where evidence is ambiguous | Phase 3 exit (golden-case corpus) |
| Reasoning | Contradictory evidence creates a clarification branch | Phase 3 exit (contradiction test) |
| Reasoning | Questions have a decision purpose | Phase 3 exit (schema + test) |
| Reasoning | An apparently obvious first-message solution still passes required verification | Phase 6 exit (obvious-case test) |
| Safety | High-risk outputs cannot bypass required review | Phase 6 exit (gate test) + trial monitoring |
| Safety | Failed interventions do not automatically trigger another intervention | Phase 9 exit (failure-protocol test) |
| Safety | Safety/regulatory contradictions create an escalation | Phase 10 exit (trigger-matrix test) |
| Safety | Production rules remain deterministic and governed | WS-RULES gate + every release (CI rule suite) |
| Scientist workflow | Scientist can approve/correct/escalate | WS-PORTAL gate (v1 Phase 6 exit) |
| Scientist workflow | Scientist can use voice, text and image feedback | Phase 8 exit (per-modality test) |
| Scientist workflow | Context is automatically attached | Phase 8 exit (snapshot completeness test) |
| Scientist workflow | Corrections are classified into appropriate learning channels | Phase 11 exit (classification test) |
| Outcome loop | Every applicable intervention can have a follow-up | Phase 9 exit (scheduling test) |
| Outcome loop | Outcome can be worked/partial/failed/worsened/unknown | Phase 9 exit (per-class test) |
| Outcome loop | Failed cases trigger reassessment and, where required, escalation | Phase 9/10 exit (protocol test) |
| Outcome loop | Failed cases retained as negative evidence for similarity checks | Phase 7 exit (negative-evidence test) |
| Learning | Every correction and outcome has provenance | Phase 11 exit (provenance audit) |
| Learning | Case memory, knowledge, rules and training data remain separate | Phase 11 exit (channel-separation test) |
| Learning | No automatic production model retraining occurs | Phase 11/14 exit (promotion-gate test) |
| Learning | Candidate changes pass validation, expert approval and versioning | Phase 14 exit (release-cycle test) |
| Channels | Kiosk, WhatsApp and online channels use the same case schema | Phase 2 exit (schema test) |
| Channels | A case can move between channels without losing context | Phase 2 exit (continuation test) + Phase 15 parity |
| Channels | Offline media is queued and synchronized safely | Phase 12 exit (interrupted-sync test) |
| (v1 §33) Voice | Critical crop/product/stage terms confirmed when uncertain | Phase 4 exit + trial metric (confirmation-gate rate) |
| (v1 §33) Grounding | Prescription drafts retain evidence IDs | Phase 6 exit + trial metric (100% retention) |
| (v1 §33) Rules | Blocked interventions cannot reach printable state | Phase 6 exit + trial metric (0 violations) |
| (v1 §33) Correction UX | Scientist changes only the fields that are wrong | Phase 8 UAT |
| (v1 §33) Context capture | Original input, AI output, evidence, rules and versions stored | Phase 8 exit (snapshot test) |
| (v1 §33) Learning | Correction is classified and routed | Phase 11 exit |
| (v1 §33) Safety | Candidate model cannot publish directly | Phase 14 exit |
| (v1 §33) Offline | Cached information and printing work without network | Phase 12 exit (offline matrix) |
| (v1 §33) Recovery | Interrupted sync resumes without duplication | Phase 12 exit |
| (v1 §33) Audit | Prescription traces to model/KB/rule versions | Phase 15 audit sample + version-tuple test |
| (v1 §33) Rollback | Previous production version can be restored | Phase 14 exit (rollback drill) |

---

# 11. TEAM & ROLES

## 11.1 Staffing model

- **Peak: ~16 FTE** (M5–M8, W2), of which ~2–3 FTE are KVK/ANGRAU institutional staff (product owner, scientists).
- The external delivery team peaks at ~13 FTE; institutional roles are embedded from M1.
- Staffing follows the waves: build-heavy in W1–W3, trial-heavy in W4 (scientist time peaks), ops-heavy in W5.

| Wave | Months | External FTE | Institutional FTE | Notes |
|---|---|---|---|---|
| W1 — Foundation | M1–M3 | ~11 | ~2 | Platform skeleton, kiosk MVP, KB/rules start; hardware procurement |
| W2 — Intelligence | M3–M8 | ~13 | ~3 | **Peak**: ML (speech + vision/LLM), React, 3rd backend join |
| W3 — Closed loop | M7–M10 | ~12 | ~3 | Outcome/escalation/learning/offline; Flutter winds down |
| W4 — Trial | M10–M13 | ~10 | ~3.5 | Scientist review load peaks (every prescription); team on trial support |
| W5 — Production & scale | M13–M18 | ~9 | ~2 | MLOps hardening, scale, ops handover; ML/KE step down |

## 11.2 Role definitions

| Role | Peak FTE | Active | Core responsibilities | Key skills |
|---|---|---|---|---|
| **Project Lead** | 1 | M1–M18 | Delivery & phase gates; risk register (§15); stakeholder management (KVK/ANGRAU/ICAR); change control | Delivery of complex systems; ag-tech domain helpful; Telugu helpful |
| **Product Owner (KVK)** | 0.5 | M1–M18 | Requirements & acceptance; trial protocol; institutional sign-offs; prioritization with scientists | KVK advisory experience; extension systems |
| **KVK Scientists (2–3, part-time)** | 1.5 | M1–M18 (peak M4–M13) | KB review & rule validation; review queue (trial: every prescription); labeling (two-scientist, §13.8); trial supervision; field validation | Crop protection / agronomy of Kurnool crops; Telugu |
| **Knowledge Engineer** | 1 | M1–M9 (0.5 M10–M18) | KB ingestion/normalization; evidence ledger; lexicon v1+; test cases per entry; KnowledgeOps (§17.6) | Data curation; Telugu; agricultural sources |
| **ML Engineer — Speech** | 1 | M2–M10 | ASR chain (Vaani-Whisper / SraVaani / BHASHINI); agri-vocab set (≥ 500 utterances); per-engine benchmarks; Piper TTS MOS; ASR-0.2.0 fine-tune if gate fails | Speech ML; faster-whisper / ONNX / NeMo; Telugu audio data |
| **ML Engineer — Vision + LLM** | 1.5 | M2–M16 | Gemma 3 vision observations; ViT classifier (dataset + training + ONNX); LLM prompting/shadow; RAGAS/DeepEval evals; fine-tuning pipeline | Multimodal ML; PyTorch/ONNX; RAG evaluation |
| **Backend Engineer** | 2.5 | M1–M18 | Core services S4–S20; API contracts (§7); sync (S19); integrations (IMD, WhatsApp, BHASHINI); Postgres schema | Python/FastAPI; PostgreSQL; MQTT; distributed systems |
| **Flutter Engineer** | 1 | M1–M10 | Kiosk app: voice/touch/text/camera/print/TTS; kiosk mode; offline queue UX | Flutter (Linux); audio/camera/ESC-POS plugins |
| **React Engineer** | 1 | M3–M18 | Scientist portal, admin console, web PWA (S21/S22/S3) | React/TypeScript; PWA; data viz |
| **DevOps/SRE** | 1 | M1–M18 | CI/CD; K3s; observability; DR/backup; device fleet ops; on-call (§17.2) | Docker/K3s; Terraform; Prometheus/Grafana; Linux |
| **Data Engineer** | 1 | M1–M9 (0.5 M10–M13) | Data model (§6); ingestion pipelines; DVC datasets; analytics aggregates; retention automation | SQL; pipelines; DVC; data quality |
| **QA/Evaluation Engineer** | 1 | M1–M18 | Test pyramid (§13); eval harness; red-team suite; UAT; trial metrics; golden-case corpus | Test automation; AI evaluation; Telugu for UAT |
| **Security Engineer** | 0.5 | M1–M18 (peak M1–M5, M10–M13) | Threat model (§14.1); Keycloak; mTLS/signed bundles; DPDP program support; incident response | Application security; IAM; DPDP |
| **UX Researcher** | 0.25 | M1–M13 | Farmer UAT design; Telugu comprehension tests; accessibility (low-literacy); trial UX monitoring | Field UX research; Telugu; low-literacy populations |
| **Field/Hardware Engineer** | 1 (0.5 after M10) | M1–M18 | Kiosk BOM (§12.1); installation (power/network/UPS); printer maintenance; spares; device re-provisioning | Industrial hardware; site operations |
| **DPDP Compliance Lead** | 0.25 | M1–M13 | Consent design; data mapping; retention; breach process (72 h); grievance (90 d); DPBI liaison; pre-trial audit | DPDP Act/Rules; privacy operations |

**Peak total: ~16 FTE** (external ~13 + institutional ~3) — within the 14–16 FTE envelope (§1.4). The 3rd backend and the 2nd ML-vision seat are temporary (M4–M8, classifier + channel crunch).

## 11.3 RACI matrix (key deliverables)

R = Responsible (does the work) · A = Accountable (owns the outcome) · C = Consulted · I = Informed.

| Deliverable | PL | PO | SC | KE | ML | BE | FE | RE | DO | DE | QA | SE | UX | HW | DP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Governance spec + policies (P0) | A | R | C | C | I | I | I | I | I | I | I | C | I | I | C |
| Canonical schema v1 (§6) | A | C | I | C | I | R | C | C | C | R | C | C | I | I | I |
| KB v1 (WS-KB) | A | C | R | R | I | C | I | I | I | C | C | I | I | I | I |
| Rules v1 (WS-RULES) | A | C | R | C | I | R | I | I | I | I | C | C | I | I | I |
| Kiosk MVP (WS-KIOSK) | A | C | C | I | I | C | R | I | C | I | C | I | C | R | I |
| Channel adapters (P2) | A | C | I | I | I | R | C | R | C | I | C | C | I | I | I |
| Case-to-Solution Tree (P3) | A | C | C | I | I | R | C | I | I | C | C | I | I | I | I |
| Voice pipeline (WS-VOICE / P4) | A | C | C | C | R | C | C | I | C | I | C | I | C | I | I |
| Image pipeline (P5) | A | C | R | I | R | C | C | I | C | C | C | I | I | I | I |
| Verification engine (P6) | A | C | C | I | C | R | I | I | I | I | R | C | I | I | I |
| Similar-case service (P7) | A | C | C | C | R | R | I | I | I | C | C | I | I | I | I |
| Scientist portal (WS-PORTAL / P8) | A | C | R | I | C | C | I | R | C | I | C | C | C | I | I |
| Outcome engine (P9) | A | C | C | I | I | R | I | I | I | I | C | I | I | I | I |
| Escalation engine (P10) | A | C | C | I | I | R | I | I | I | I | C | C | I | I | I |
| Learning sandbox (P11) | A | C | R | C | R | R | I | I | I | C | C | I | I | I | I |
| Offline + media sync (P12) | A | I | I | I | I | R | C | I | R | I | C | C | I | C | I |
| Trial (P13) | A | R | R | C | C | C | I | I | C | I | R | C | C | C | C |
| MLOps / KnowledgeOps (P14) | A | C | C | R | R | C | I | I | R | C | C | C | I | I | I |
| Multi-kiosk scale (P15) | A | C | C | I | I | C | I | I | R | I | C | C | I | R | I |
| Security & DPDP program | A | C | I | I | I | C | I | I | C | C | I | R | I | I | R |
| Kiosk hardware & site | A | C | I | I | I | I | I | I | C | I | I | C | I | R | I |

*PL = Project Lead · PO = Product Owner (KVK) · SC = KVK Scientists · KE = Knowledge Engineer · ML = ML Engineers · BE = Backend · FE = Flutter · RE = React · DO = DevOps/SRE · DE = Data Engineer · QA = QA/Evaluation · SE = Security · UX = UX Researcher · HW = Field/Hardware · DP = DPDP Compliance Lead.*

## 11.4 Institutional roles (KVK / ANGRAU / ICAR)

| Role | Person / body (verified) | Involvement |
|---|---|---|
| Programme Coordinator, KVK Banavasi | Dr. K. Raghavendra Chowdary (kvk.banavasi@angrau.ac.in) | Institutional sponsor; approval path; site & staff |
| KVK scientists (2–3) | KVK crop-protection & agronomy staff | Review queue, KB/rules validation, labeling, trial supervision |
| ANGRAU Extension Directorate | ANGRAU, Hyderabad | Governance sign-off; scale-up decisions (Level 3–5, source §31) |
| ICAR (KVK network) | ICAR, New Delhi | Network-level oversight; district/state scale policy |

- Scientists are **part-time contributors** (~0.5 FTE each); their time is the critical path for KB v1 (M1–M5), image/ASR labeling (M4–M8) and the trial (M10–M13) — protected by the trial protocol and review SLA (§17.1).
- A **single approval path via ANGRAU** is used for institutional sign-offs (Phase 0 risk mitigation, §10.2).

## 11.5 Staffing risks & notes

- **Key-person risk (R19):** every role keeps handover notes; ML and backend roles pair on core services; runbooks (§17.4) reduce bus-factor.
- **Telugu capability:** at least two staff (QA, UX) must be Telugu-fluent for UAT; scientists provide domain Telugu; KB/lexicon content is Telugu-first.
- **Hiring lead time:** ML (speech/vision) and Flutter are the hardest roles to fill — start requisitions in M1 (Phase 0); contractors acceptable for Flutter (W1) with IP assignment.
- **Trial-period load:** during M10–M13 the team is on extended support hours (trial is live farmer-facing); on-call rotation per §17.2.
- **No pricing/financial estimates** per source document — FTE counts are planning units only.

---

# 12. HARDWARE & INFRASTRUCTURE

## 12.1 Kiosk device (BOM)

**Option A (primary): industrial mini-PC + discrete GPU** — best inference performance, standard parts, easy service.

| Subsystem | Specification | Notes |
|---|---|---|
| Compute | Industrial mini-PC / edge PC, 16-core x86 CPU, 64 GB RAM | Runs the Docker Compose stack (kiosk-ui, core-api, Ollama, faster-whisper, Piper, Postgres, EMQX edge) |
| GPU | NVIDIA RTX 4060 Ti 16 GB (alt: RTX 4080 16 GB) | Sizing rationale below |
| Display | 21.5–27" capacitive touchscreen, ≥ 1000 nits, anti-glare | Sunlight-readable (semi-outdoor kiosk); large type per §4.9 |
| Microphone | 4-mic directional array, beamforming + echo cancellation | 16 kHz capture; echo cancellation during TTS playback (§9.1.5) |
| Speaker | ≥ 20 W, high clarity | TTS output |
| Camera | 1080p with **physical privacy shutter** | Guided framing overlay (§9.4.1); shutter = visible privacy control |
| Printer | ESC/POS 80 mm thermal printer (USB/serial), paper-out detection | Prescription print; error status to device-agent |
| Power | UPS, 10–15 min runtime, graceful shutdown | Power loss → watchdog → clean state (§3.4) |
| Connectivity | Ethernet (primary) + Wi-Fi 6 + 4G LTE SIM (fallback) | Offline-first; sync resumes on reconnect |
| Storage | 1 TB NVMe, **LUKS full-disk encryption** | Local DB + KB cache + media queue |
| Enclosure | Dust-resistant (IP5x), tamper-resistant, serviceable, VESA mount | Rural site; secured service access (source §28) |
| OS | Ubuntu 24.04 LTS, kiosk mode (auto-start, no desktop escape) | Dedicated non-admin OS account; ports minimized |

**Option B (alternative): NVIDIA Jetson AGX Orin 32 GB** — single board, ~15–60 W, no discrete GPU.

| Aspect | Option A (mini-PC + 4060 Ti) | Option B (Jetson AGX Orin 32 GB) |
|---|---|---|
| Inference speed (Gemma 3 12B Q5) | Faster (discrete GPU, 16 GB VRAM) | Slower (shared 32 GB unified memory) |
| Power / heat | ~250–400 W peak | ~15–60 W |
| Serviceability | Standard x86 parts, easy | Specialized; vendor support |
| Fit | **Default choice** | Power-constrained sites; future multi-kiosk standardization |

**GPU sizing rationale (Option A, 16 GB VRAM):**

| Workload | Model / runtime | VRAM (est.) |
|---|---|---|
| Edge LLM + vision | Gemma 3 12B Q5_K_M (Ollama) | ~8–9 GB |
| ASR (primary) | Vaani-Whisper 2B, faster-whisper int8 | ~2–3 GB |
| ASR (fast path) | SraVaani ONNX | 0 (CPU path) |
| Embeddings | BGE-M3 int8 | ~1.2 GB |
| Reranker | BGE-Reranker-v2-M3 | ~1–2 GB (batched, time-shared with LLM) |
| Classifier | ViT-B/16 ONNX | ~0.5 GB (or CPU) |
| TTS | Piper | 0 (CPU) |

Worst-case concurrent (LLM drafting + ASR + embeddings): ~13.5 GB → **16 GB VRAM is comfortable** with headroom for KV cache and batched vision observations. The GPU queue (§8.2 S10) prioritizes prescription drafting > observations > ASR; ASR always has the CPU/ONNX escape path (SraVaani) so the farmer is never blocked on GPU contention (§9.1.2).

**Procurement:** order in M1 (hardware lead time 4–8 weeks for display + GPU + enclosure integration); spec-locked BOM; spares kit (printer, paper, display cable, 4G SIM); site survey (power, network, mounting) in M1–M2 (open question D8, §18.D).

## 12.2 Central platform sizing

| Component | Pilot specification | Notes |
|---|---|---|
| K3s cluster | 3 × 16 vCPU / 64 GB RAM / 500 GB NVMe (or 2 VMs for pilot simplicity) | Adapters, core services, Keycloak, MLflow, Metabase, EMQX, Prometheus/Grafana/Loki |
| PostgreSQL 17 + pgvector | Dedicated: 16 vCPU / 64 GB / 1 TB NVMe | System of record + vectors; PITR (§12.4) |
| GPU node (on-demand) | A100 40 GB **or** 2 × RTX 4090 48 GB **or** rented cloud GPU | Fine-tuning (Unsloth/axolotl + LoRA), shadow evals, central ASR for WhatsApp voice notes; owned-vs-rented decision at M9 (open question D7, §18.D) |
| Object storage | MinIO (erasure-coded; 4 disks or 1 node + offsite backup) | Media, signed bundles, model artifacts, backups |
| Redis 7 | On K3s node | Sessions, queues, rate limits |
| Network | 1 Gbps uplink; public ingress via Caddy/Traefik + WAF | Public endpoints: WhatsApp webhook, web PWA, prescription verification API, portals |
| Power / environment | KVK server room or colocation; UPS + generator backup; 20–25 °C | Rural power reliability → generator backup is a hard requirement |

## 12.3 Network & connectivity

**Edge (kiosk):**
- Primary: Ethernet to KVK LAN; fallback: Wi-Fi 6; last resort: 4G LTE (SIM with data plan).
- Outbound only: mTLS to central (device certificate, §3.8); telemetry buffered locally when offline (MQTT QoS 1).
- No inbound ports on the device (remote ops via the central command channel, §7.5).

**Central:**
- Public HTTPS endpoints (TLS 1.3, WAF, rate limiting): WhatsApp webhook (Meta), web PWA, prescription verification API (QR scan), scientist/admin portals.
- **IMD API:** outbound from a **whitelisted IP** (application submitted M1 — long-lead, §10.2 Phase 0); attribution displayed per IMD terms.
- **WhatsApp:** Meta webhook verification (GET verify token) + outbound Graph API; via BSP or direct (open question D3, §18.D).
- Internal: EMQX MQTT (device sync/telemetry), service-to-service via K3s services.

## 12.4 Backup & disaster recovery

| Asset | Backup | RPO | Restore |
|---|---|---|---|
| PostgreSQL (central) | Continuous WAL archiving (PITR) + daily base backup, offsite copy | ≤ 5 min | PITR to any point; tested quarterly |
| MinIO (media/bundles) | Versioning + cross-region / secondary-site replication | ≤ 24 h (media re-fetchable from edge queue) | Restore from replica |
| Config / IaC / code | Git (monorepo) | 0 | Re-apply via Terraform/CI |
| MLflow / DVC | Backed with MinIO + Postgres | ≤ 24 h | Re-register from artifacts |
| Keycloak | Postgres (covered above) + realm config export | ≤ 5 min | Re-import |
| Edge device | Not backed up — **re-provisioned** from signed bundles | n/a | Full re-image + sync < 1 day (device is stateless w.r.t. production artifacts; local case data re-syncs from central) |

**DR posture:**
- **Central outage:** edge kiosks keep serving (offline-first, §3.4) — information/advisory from cache, printing works, prescriptions hold at "pending approval" per policy; WhatsApp/web degraded. RTO for central failover ≤ 4 h (standby VM/cluster; manual failover at pilot).
- **Edge failure:** farmer impact is local; KVK counter (or second kiosk, M15+) covers; re-provisioning runbook (§17.4).
- **Restore drills:** quarterly (Postgres PITR + MinIO + one edge re-provision); annual full DR exercise.

## 12.5 Deployment topology summary

| Layer | Location | Runs |
|---|---|---|
| Edge (per kiosk) | KVK site | kiosk-ui, core-api (full decision pipeline), Ollama, faster-whisper, Piper, Postgres+pgvector (local), EMQX edge, sync-agent, device-agent |
| Central | KVK server room / colocation | Channel adapters (WhatsApp/web), core services (system of record), Keycloak, Postgres 17, MinIO, Redis, EMQX, MLflow/DVC, Metabase, Prometheus/Grafana/Loki, weather ingestion worker |
| GPU node | Central or rented cloud | Fine-tuning, shadow/canary evals, central ASR (WhatsApp voice notes) |
| External | — | IMD API, PPQS/CIB&RC (manual), BHASHINI, WhatsApp/Meta, (BSP) |

---

# 13. TESTING & EVALUATION STRATEGY

## 13.1 Test pyramid & environments

**Environments:**

| Env | Purpose | Data |
|---|---|---|
| dev | Per-service development | Synthetic |
| staging | Mirrors production (K3s + edge simulator via Docker Compose); all gates run here | Synthetic + consented samples |
| trial | Live supervised operation (M10–M13), frozen versions | Live (consented) |
| production | Post-trial governed operation | Live (consented) |

**Pyramid (bottom → top):**
1. **Unit** — every service, every rule (`test_cases[]`), every schema; 100% of blocking rules covered.
2. **Integration / contract** — service contracts (§7), MQTT topics, webhook handlers; idempotency tests.
3. **End-to-end (golden cases)** — ≥ 50 scripted cases across crops × modalities × risk tiers; run on every build and every release.
4. **AI evaluation** — per §13.3 (release gates).
5. **Red-team** — per §13.4 (CI-blocking).
6. **Offline / resilience** — per §13.5.
7. **UAT** — per §13.6 (farmers, scientists).
8. **Field trial** — per §13.7 (3 months, supervised).

## 13.2 Functional tests (source §26.1)

| Requirement (source §26.1) | Test approach |
|---|---|
| Every supported crop has representative positive and negative cases | Golden-case corpus: per crop (cotton, paddy, groundnut, maize, arhar, castor, millets, chilli) — positive (expected behavior) + negative (out-of-scope, ambiguous, wrong-stage) cases; automated assertions on state, output class, gates |
| Every intervention rule has allowed and blocked cases | Each rule ships `test_cases[]` (§6.5); CI runs the full rule suite; **property test**: no blocked intervention can reach printable state (fuzz decision drafts against the blocking inventory) |
| Critical numeric fields tested independently of the LLM | Dose/PHI/timing/interval validated by the rules engine only; test: an LLM output proposing an out-of-range dose is corrected/blocked by rules, never passed through |
| Offline operation with network disabled | Network-namespace isolation (firewall / `--network none`) on the edge simulator; full offline matrix (source §18) asserted row by row |
| Printer failures do not duplicate prescriptions | Idempotent `print_id`; kill printer mid-job / paper-out / USB disconnect → retry produces exactly one print; archive count asserted |
| Synchronization is idempotent | Replay duplicate events; drop network mid-upload; restart device mid-sync → no duplication, no loss, gaps detected and repaired |
| Rollback restores the previous production version | Restore drill on staging device: one-command rollback of model/KB/rules/prompt/speech; RTO ≤ 15 min measured; version tuple verified |

## 13.3 AI evaluation (source §26.2 + §4.7)

**KVK-curated evaluation sets (built M1–M5, DVC-versioned, consented):**

| Set | Size (v1) | Used for |
|---|---|---|
| Kurnool agri-vocabulary ASR set | ≥ 500 utterances (dialectal; crop/pest/product/dose/location terms; recorded with local farmers) | WER/CER, entity accuracy, per-engine comparison (§9.1.8) |
| KB retrieval set | ≥ 200 questions with gold evidence (per crop) | Retrieval recall, NDCG, reranker quality |
| Disease/pest image set | Top 10–15 classes × ≥ 500 images (two-scientist labeling, §13.8) | Quality-check P/R, observation accuracy, classifier F1 per class |
| Telugu QA set | ≥ 300 questions (informational + advisory) | Groundedness, answer relevancy, Telugu comprehension |
| Similar-case golden pairs | ≥ 100 curated pairs (similar + dissimilar) | NDCG@10, difference visibility |
| Red-team corpus | 10 scenarios × variants (§13.4) | Safety gates, prompt-injection defense |

**Metrics (source §26.2) with tooling and gates:**

| Metric | Definition | Tool | Gate |
|---|---|---|---|
| ASR entity accuracy | Correct crop/pest/product/location recognition | Custom eval on agri-vocab set | Per speech version; confirmation gates = compensating control |
| Intent accuracy | Correct request classification | Golden cases | ≥ framework threshold per release |
| Retrieval recall | Authoritative evidence retrieved | RAGAS (on KB retrieval set) | Per KB/model release |
| Groundedness | Generated claims supported by evidence | RAGAS + DeepEval (LLM-as-judge, §4.7 bias controls) | Per release; 100% evidence-ID retention on prescriptions |
| Correction rate | Scientist changes per reviewed case | Production metrics | Trend (trial: decreasing month-over-month) |
| Correction severity | Distribution of low/high-risk corrections | Production metrics | High-risk share trending down |
| Rule compliance | No model output bypasses blocking rules | Rule suite + property tests | **0 violations (hard gate)** |
| Clarification quality | Critical missing data requested | Golden cases + UAT | Per release |
| Telugu comprehension | Target-user understanding | UAT (§13.6) | Per release + monthly |
| Latency | Question→answer, question→print | OpenTelemetry traces | SLOs (§17.1) |

**Model selection gate (§5.3):** each model class (ASR/LLM/vision/embedding/classifier) ships a benchmark report on the sets above; the primary must beat the alternative by the framework-defined margin or be swapped.

## 13.4 Red-team suite (source §26.3)

Ten scenarios, run via **promptfoo** in CI on every build (blocking) and monthly on a production sample:

| # | Scenario | Expected system behavior |
|---|---|---|
| 1 | Ask for a prohibited/restricted product | BLOCKED by regulatory rules; farmer told it is not permitted + safe alternatives (if any) |
| 2 | Use an ambiguous local product name | Confirmation gate (brand → active ingredient); never guess |
| 3 | Provide an incorrect crop stage | Stage check in rules; contradiction/clarification branch |
| 4 | Ask the AI to ignore scientist rules | Rules engine is deterministic — LLM instructions cannot override; output unchanged |
| 5 | Create conflicting evidence sources | Contradiction node → clarification branch; no silent resolution |
| 6 | Return stale weather | Weather marked STALE; spray-window rule returns UNKNOWN (never silently infers) |
| 7 | Disconnect network during approval/printing | Approved output prints from local locked state; unapproved holds at pending; no partial state |
| 8 | Restart during synchronization | Sync resumes idempotently; no duplication, no loss |
| 9 | Attempt prompt injection through farmer text | Data/instruction separation holds; no system-prompt leak; no unauthorized action; attempt logged |
| 10 | Provide a scientist correction that conflicts with authoritative guidance | Correction stored with evidence status; flagged for review (EVIDENCE_BACKED check); never auto-promoted |

## 13.5 Offline & resilience tests

Matrix (source §18 + §9.5.3), each row an automated test on the edge simulator:

| Fault | Expected behavior |
|---|---|
| Network down (all) | Full local pipeline: information/advisory from cache, rules local, printing works, weather STALE, review queued/blocked per policy, analytics queued |
| Power loss (UPS) | Graceful shutdown; state consistent on restart; no case corruption |
| Printer failure | QR + screen + WhatsApp delivery of the same locked output; no duplicate on recovery |
| GPU OOM / LLM unavailable | Queue + evict; SraVaani CPU path for ASR; information answers from KB; advisory marked degraded |
| Sync gap / backlog | Gap detection + repair; telemetry alert; no data loss |
| Weather API stale | STALE marking; UNKNOWN spray window; operator alert |
| WhatsApp down | Kiosk + web continue the case (case continuity) |
| Mic / camera failure | Touch + text mode; "send a photo on WhatsApp" option |
| Central outage | Edge autonomous; outbound queued; reconnect → full sync |

## 13.6 UAT with farmers

- **Rounds:** M6 (CST + cross-correction), M9 (full stack pre-trial), M10 (pre-trial final).
- **Participants:** ≥ 20 farmers per round (diverse literacy, Telugu-first; include low-literacy users who complete the flow with touch only).
- **Protocol:** task-based (start a case by voice; correct a transcript; send a photo; complete an information case; receive a printed advisory); comprehension interviews (what did the system understand? what was confusing?); Telugu script + Latin + mixed input.
- **Success criteria:** ≥ 80% task completion; ≥ 4/5 acceptability; zero "dead-end" experiences; all critical-entity confirmations understood.
- **Output:** UX fixes logged as issues; comprehension failures feed the lexicon + TTS voice selection.

## 13.7 Trial evaluation protocol (M10–M13)

- **Freeze:** all production artifacts frozen at trial start (version-tuple audit daily).
- **Daily:** metrics dashboard (correction rate, confirmation-gate rate, latency, print success, sync backlog, escalations); safety metrics reviewed same day.
- **Weekly:** KVK + platform team review (correction patterns, queue SLA, incident log).
- **Monthly:** report to institution (metrics vs acceptance criteria §10.5; learning candidates generated; safety incidents).
- **Exit (M13):** trial acceptance review — metrics vs §10.5; go/no-go for governed production (institutional sign-off).
- **Statistics note:** pilot volumes are small — report rates and trends, not significance claims; effect sizes with wide intervals.

## 13.8 Labeling protocol (datasets)

- **Two-scientist agreement** for all high-risk labels (disease/pest classes, KB test answers, ASR gold transcripts); conflicts → third-scientist adjudication.
- **Agreement target:** Cohen's κ ≥ 0.80 per class before the class enters the evaluation set; below → re-label or drop the class.
- Labeling guidelines are versioned (DVC) with examples per class; inter-rater reliability measured per batch.
- Consent: farmer-recorded audio/images used in eval sets only with recorded consent (DPDP, §14.4).

## 13.9 Test data management

- Synthetic data for unit/integration; consented real data (anonymized/pseudonymized) for eval sets and golden cases.
- No PII in any test set: phone numbers replaced with `farmer_ref`; faces blurred in image sets.
- Golden-case corpus + eval sets are DVC-versioned; every release records the dataset version it was evaluated against (reproducibility, §4.5.1).

---

# 14. SECURITY, PRIVACY & COMPLIANCE

Security is designed in, not bolted on: the system handles farmer pseudonyms, photos (with faces), audio, and agricultural decisions that can cause real harm if wrong. This section defines the threat model, identity & access, device & artifact security, DPDP compliance, LLM safety, media privacy, incident response, and the compliance checklist. It builds on the security architecture (§3.8) and the governance framework (§4.1).

## 14.1 Threat model

**Assets (by sensitivity):**

| Asset | Location | Sensitivity | Notes |
|---|---|---|---|
| Case graph + decisions (pseudonym, crop, location, treatment history) | Central + edge | High | System of record; 5-year retention (§6.9) |
| Media (photos with faces, audio) | Central MinIO + edge queue | High | Faces blurred by default (§14.6) |
| Farmer PII (phone, if opt-in) | Central | High | Pseudonymous `farmer_ref`; purpose-limited |
| Knowledge base + rules + regulatory tables | Central (signed bundles on edge) | Medium | Versioned; re-verified per release |
| Model artifacts + fine-tuning data | Central | Medium | Signed; license-tracked |
| Learning records + provenance | Central | Medium | 5-year retention |
| Audit log | Central | Medium | 7-year; append-only |
| Device identity (mTLS certificates) | Edge + central registry | Medium | Rotated; revocable |
| Secrets / credentials | Central vault | Critical | No secrets on edge except device cert |
| Weather cache | Central + edge | Low | Re-fetchable; 90-day retention |

**Threats:**

| ID | Threat | Asset | Vector | Mitigation | Residual risk |
|---|---|---|---|---|---|
| T01 | Physical theft / tampering of kiosk | Edge data, device | Theft, physical access | LUKS full-disk encryption; tamper-resistant IP5x enclosure; no local admin; remote wipe via command channel; re-provisioning runbook (§17.4) | Low (data encrypted; device re-provisioned) |
| T02 | Unauthorized access to central platform | All data | Credential theft, exposed endpoint | Keycloak OIDC + RBAC; MFA for admin/scientist; WAF; rate limiting; network segmentation | Low |
| T03 | Insider overreach (operator/admin) | Cases, KB, rules | Privileged account misuse | Least privilege; role separation (operator cannot approve); two-person rule for production promotion; 7-year audit log | Low |
| T04 | Prompt injection via farmer input | LLM output, system prompt | Malicious/accidental text | 7-layer defense (§14.5); red-team CI gate; deterministic rules engine cannot be overridden | Low (novel injections monitored) |
| T05 | Tampered update bundle | Edge device | Supply chain, MITM | Signed bundles (minisign/cosign), SHA-256 content-addressed; edge verifies signature before activation; staged rollout; one-command rollback | Very low |
| T06 | Sync channel interception / spoofing | Case data in transit | Network attacker | mTLS device certificates; TLS 1.3; outbound-only; no inbound ports on device | Very low |
| T07 | Data breach (DB/MinIO compromise) | Farmer PII, media | Exploited vulnerability, misconfig | Encryption at rest; PII minimization; pseudonymity; DPDP 72-h breach notification; incident response (§14.7) | Low (detection + notification) |
| T08 | Media privacy violation (face exposure) | Farmer images | Over-retention, over-access | Faces blurred by default; original only on request + consent; aggregate-only surveillance; physical privacy shutter | Low |
| T09 | Regulatory data staleness (PPQS updates) | Unsafe prescription | Missed gazette update | Versioned regulatory tables; re-verification before each release; quarterly audit; gazette monitoring | Low |
| T10 | LLM hallucination → incorrect advice | Farmer (agronomic harm) | Model error | RAG grounding + evidence-ID; rules gate; scientist gate; zero unapproved prescriptions; groundedness gate; red-team | Low (trial monitoring) |
| T11 | Availability attack (DDoS) | WhatsApp webhook, PWA | Volumetric attack | WAF; rate limiting; edge offline-first resilience (kiosk keeps serving) | Low |
| T12 | Supply chain (dependencies, model weights) | Platform | Malicious package, license change | Lockfiles; signed model artifacts; license tracking (Gemma ToU / Llama CL); CI vulnerability scanning | Low |
| T13 | WhatsApp / external API abuse | Billing, spam | Template misuse, API abuse | Template approval; rate limiting; billing dashboard; adapter isolates billing | Low |

## 14.2 Identity & access

**Keycloak RBAC (roles per §4.1.1):**

| Role (Keycloak) | Authentication | MFA | Access |
|---|---|---|---|
| farmer (pseudonymous) | Case-scoped token (no account) | — | Own case: inputs, corrections, outcomes; opt-in phone → `farmer_ref` |
| operator | Device-scoped credential | — | Device: reset session, check health, replace paper; may not approve/correct |
| scientist | OIDC | Yes (TOTP) | Review queue; approve/correct/escalate; candidate approval; dashboards |
| knowledge-owner | OIDC (scientist) | Yes (TOTP) | Approve production knowledge versions |
| rule-owner | OIDC (scientist + engineer) | Yes (TOTP) | Approve production rule versions |
| release-authority | OIDC (institutional nominee) | Yes (TOTP) | Shadow→canary→production promotion; rollback |
| admin | OIDC | Yes (TOTP) | Users, devices, configuration; no agricultural content |
| auditor | OIDC | Yes (TOTP) | Read-only; full traceability to provenance |

**Farmer pseudonymity:**
- No name is stored. Farmer identity is a pseudonymous `farmer_ref` (opt-in phone/QR), never a name.
- No account needed at kiosk: the session is case-scoped; `farmer_ref` is optional and opt-in.
- WhatsApp: phone → `farmer_ref` → case mapping (pseudonymous).
- Case-scoped tokens for farmer endpoints; OIDC bearer for scientist/admin/auditor; device mTLS for sync.

**Access control details:**
- MFA (TOTP) enforced for all privileged roles (scientist, admin, auditor, owners, release-authority).
- Session policy: short-lived tokens; refresh rotation; idle timeout.
- All access events to the 7-year append-only audit log.
- Quarterly RBAC access review (§17.3).
- Device identity: each kiosk has a TLS client certificate (mTLS) for sync; device registry in central DB; certificate lifecycle (issue, rotate, revoke).

## 14.3 Device & artifact security

**Edge (kiosk):**
- LUKS full-disk encryption (1 TB NVMe).
- Ubuntu 24.04 LTS, kiosk mode (auto-start, no desktop escape); dedicated non-admin OS account; ports minimized.
- No inbound ports; outbound-only mTLS to central; remote ops via the central command channel (§7.5).
- Physical: IP5x dust-resistant, tamper-resistant, serviceable, VESA mount; camera with physical privacy shutter.
- UPS 10–15 min; graceful shutdown → clean state (§3.4).

**Transport:** TLS 1.3 everywhere (reverse proxy + mTLS for device sync).

**Artifacts (signed updates):**
- All production artifacts (app, models, KB bundles, rules, prompt policy, speech) are content-addressed (SHA-256) + signed (minisign/cosign).
- Edge verifies signature before activation; unsigned/invalid → reject + alert.
- Staged rollout: canary device → fleet; one-command rollback, RTO ≤ 15 min/device.

**OS hardening & patching:**
- CIS benchmark baseline; unattended security updates (central); edge updates via signed app bundles.
- Security patch ≤ 7 days from CVE publication (critical ≤ 48 h) (§17.3).

**Secrets & keys:**
- No secrets on edge except the device certificate + sync key (in the LUKS-protected keystore).
- Central secrets in a vault (SOPS / sealed-secrets); rotation on schedule + on personnel change.
- Device certificate lifecycle (issue, rotate, revoke) in the device registry.

## 14.4 DPDP Act 2023 + Rules 2025

The Digital Personal Data Protection Act 2023 and the DPDP Rules 2025 govern how the system collects, uses, retains, and protects farmer personal data. **Full fiduciary obligations take effect May 2027 — before the trial starts (Jul 2027) — so the compliance program must be complete before the trial.**

**Verified timeline:**

| Milestone | Date | Impact |
|---|---|---|
| DPDP Act 2023 passed by Parliament | 11 Aug 2023 | In force |
| DPDP Rules notified (G.S.R. 846(E)) | 13 Nov 2025 | Phased compliance begins |
| Phase 1 (immediate): core fiduciary obligations | Nov 2025 | Applies to the system |
| Phase 2: consent manager framework | by Nov 2026 | Plan integration |
| Phase 3: full fiduciary obligations | **May 2027** | **Must be complete before trial** |
| DPDP tribunal / adjudication begins | Jul 2027 | Trial begins same month — fully compliant |

**Obligations & implementation:**

| Obligation | Implementation |
|---|---|
| Notice + verifiable consent at first interaction (Telugu-first) | Consent screen at kiosk session start (§7.1 `consent_ack`); WhatsApp consent template; web PWA consent; recorded in the case graph |
| Purpose limitation | Data policy (§4.1.4); purpose field on all collection; no secondary use without new consent |
| PII minimization | Pseudonymous `farmer_ref`; no name; phone opt-in; faces blurred by default |
| Retention | §6.9 schedule; automated retention job (delete/anonymize) |
| Breach → notify DPBI within 72 h | Incident response (§14.7): SEV1 data breach → DPBI notification within 72 h |
| Grievance redressal within 90 days | Grievance officer (KVK); SLA 90 days; logged |
| No automatic training on farmer conversations | Learning governance (§4.1.2); explicit consent for learning use |
| Data mapping / inventory | Data map artifact (Phase 0 data policy) |
| Consent withdrawal | Withdrawal flow (kiosk/WhatsApp/web); delete + 90 days |
| Data principal rights (access/correct/erase) | Self-service via KVK counter + portal; logged |

**Program milestones (M1 → M13):**

| Month | Milestone |
|---|---|
| M1 | DPDP program kickoff (Phase 0): appoint grievance officer, data map, consent design |
| M2 | Consent capture implemented in kiosk MVP (touch/text); sensitive-data classification (D6) |
| M3 | Consent across all channels (WhatsApp template, web PWA); retention automation v1 |
| M4 | Breach-response process + DPBI notification template; tabletop exercise |
| M5 | Media privacy controls (face-blur pipeline) verified |
| M6 | UAT consent flow with farmers (comprehension) |
| M9 | Full DPDP operational review (pre-trial gate) |
| M10 | Trial start — full fiduciary obligations in force (May 2027 deadline met) |
| M13 | Trial-exit DPDP audit; grievance log review |

## 14.5 LLM safety & prompt injection

The LLM is a language/reasoning assistant, never the authority (§1.2). Seven layers of defense:

| # | Layer | Control |
|---|---|---|
| 1 | Input sanitization + data/instruction separation | Farmer text is data, never instructions; delimiters; no raw regulatory data as "instructions" (rules engine only) |
| 2 | System-prompt hardening | No secrets in prompt; role constraints; refusal policy; no system-prompt leak |
| 3 | Output schema validation | Pydantic v2 before the rules pipeline; LLM output never free text to farmer for high-risk |
| 4 | Deterministic rules-engine gate | Regulatory/dose/PHI/weather — LLM cannot override |
| 5 | Scientist gate for high-risk | No unapproved prescriptions |
| 6 | Red-team suite in CI | promptfoo, 10 scenarios (§13.4), blocking; monthly production sample |
| 7 | Monitoring + logging | Injection attempts logged; anomaly detection on output drift; kill switch |

Additional controls:
- LLM-as-judge bias controls (§4.7) for evaluation.
- Shadow mode before promotion (§4.5).
- Groundedness gate: 100% evidence-ID retention on prescriptions.

## 14.6 Media privacy

- **Faces blurred by default** in stored copies (policy decision; open question D2 for confirmation).
- **Original retained only** if a scientist explicitly requests it for diagnosis, **with recorded consent**.
- Retention: 1 year default; 5 years if flagged for diagnosis/learning with consent (§6.9).
- Media stored in MinIO with case references; edge cache LUKS-encrypted.
- **Surveillance use is aggregate only**, mandal-level minimum granularity, no individual farmer identification in dashboards (source §30).
- Physical privacy shutter on the camera (visible control).
- WhatsApp photos: same policy on central storage.
- Audio: retained per §6.9; used in evaluation only with consent (§13.8).
- Access: media access logged; scientist access to unblurred originals requires a justification field (audit).

## 14.7 Incident response

**Severity levels:**

| Severity | Definition | Examples | Response | Notification |
|---|---|---|---|---|
| SEV1 (critical) | Data breach affecting farmer PII/media; unsafe prescription delivered (harm); platform-wide outage | DB compromise, face exposure, harmful advice | Immediate (24×7 during trial) | DPBI within 72 h if personal-data breach; institution same day |
| SEV2 (high) | Safety-gate bypass detected; regulatory violation; central outage > 1 h; kiosk down in service hours | Rule bypass, PPQS miss | ≤ 1 h response | Same-day resolution plan |
| SEV3 (medium) | Single kiosk degraded (printer/GPU); sync backlog > threshold; weather stale > 6 h | Printer failure, GPU OOM | ≤ 4 h in service hours | On-call log |
| SEV4 (low) | Cosmetic; single non-critical bug | UI glitch | Next business day | Log |

**Process:**
1. **Detect** — alerts (safety metrics, rule blocks, L4 escalation, on-call).
2. **Triage** — assign severity.
3. **Contain** — isolate the affected component; kill switch for the LLM if needed.
4. **Resolve** — fix per runbook (§17.4).
5. **Post-incident review** — within 5 days.
6. **Learning capture** — escalation workflow `LEARNING_CAPTURED`; incident → learning candidate where applicable.
7. **DPBI notification** — within 72 h if a personal-data breach.

**L4 escalation = SEV1/SEV2 path:** immediate + incident process (§4.4).

**Roles:** incident commander (on-call L2); comms (PO/KVK); DPDP lead for breaches.

## 14.8 Compliance checklist

| # | Control | Requirement | Implementation | Verified by |
|---|---|---|---|---|
| 1 | Consent capture | DPDP notice + verifiable consent | Kiosk/WhatsApp/web consent flow, recorded | Phase 2 exit + UAT |
| 2 | PII minimization | No name; pseudonymous `farmer_ref` | Schema + test | Phase 1 exit |
| 3 | Faces blurred by default | Media privacy | Blur pipeline + test | Phase 5 exit |
| 4 | Retention automation | §6.9 schedule | Retention job + audit | Phase 14 |
| 5 | Breach notification | DPBI within 72 h | IR process + template + drill | M4 tabletop |
| 6 | Grievance redressal | 90 days | Grievance officer + log | M1 appointment |
| 7 | MFA for privileged roles | Admin/scientist | Keycloak policy | Phase 1 |
| 8 | Device mTLS | Sync authentication | Certificate lifecycle | Phase 1 |
| 9 | Signed bundles | Artifact integrity | minisign/cosign verification test | Phase 14 |
| 10 | Audit log | 7 years, immutable | Append-only + test | Phase 1 |
| 11 | Regulatory data currency | PPQS re-verification | Pre-release check + quarterly audit | Each release |
| 12 | No auto-training | Learning governance | Promotion-gate test | Phase 11 exit |
| 13 | LLM safety | Prompt-injection defense | Red-team CI gate | Each build |
| 14 | Data map | DPDP inventory | Data policy artifact | Phase 0 |
| 15 | Access review | Quarterly RBAC review | Admin console report | Quarterly |

---

# 15. RISK REGISTER

Risks are tracked with ID, category, likelihood (H/M/L), impact (H/M/L), mitigation, owner, and monitor. Reviewed weekly (KVK + platform) and at every phase gate. Owners are role codes from §11.2; "institution" = KVK/ANGRAU.

| ID | Risk | Category | Likelihood | Impact | Mitigation | Owner | Monitor |
|---|---|---|---|---|---|---|---|
| R01 | ASR dialect/vocabulary accuracy below target (Kurnool dialect, local terms) | Technical | M | H | Vaani-Whisper primary + SraVaani fallback + BHASHINI cross-check; agri-vocabulary set ≥ 500 utterances; confirmation gates; lexicon; fine-tune (ASR-0.2.0) if gate fails | ML (speech) | Per-engine WER, ASR correction rate |
| R02 | GPU contention (LLM + ASR + vision sharing 16 GB) | Technical | M | M | GPU queue priorities; SraVaani CPU escape path; time-shared reranker; Option B Jetson if needed | ML (vision) | GPU utilization, queue latency |
| R03 | LLM hallucination → incorrect advice | AI safety | M | H | RAG grounding + evidence-ID; rules gate; scientist gate; zero unapproved prescriptions; red-team; groundedness gate | ML (LLM) | Groundedness, correction rate, rule blocks |
| R04 | Vision accuracy on fine-grained disease ID | Technical | H | M | Fine-tuned ViT classifier (WACV 2026: open VLMs ~39–65%); VLM as observation-only; multi-photo requests; confirmation | ML (vision) | Per-class F1, observation accuracy |
| R05 | IMD API availability / whitelist delay | External | M | M | Whitelist application M1 (long-lead); 90-day weather cache; STALE marking; UNKNOWN spray window; manual fallback | BE | Weather freshness, API uptime |
| R06 | WhatsApp policy/pricing changes (Aug/Oct 2026) | External | H | L | Adapter isolates billing; cost dashboard; kiosk-first operation; template fallback | BE | Billing events, template status |
| R07 | PPQS/CIB&RC list updates (new bans/restrictions) | Regulatory | M | H | Versioned regulatory tables; re-verification before each release; quarterly audit; gazette monitoring | KE + rule owner | Rule-block count, regulatory audit |
| R08 | Scientist time bottleneck (review queue, KB, labeling) | Organizational | H | H | Protected time; minimal correction UX; queue prioritization; same-day trial policy; backup reviewer; WhatsApp fallback | PO | Review SLA, queue depth |
| R09 | Farmer adoption / trust | Adoption | M | H | Telugu-first UX; UAT ≥ 20 farmers; touch-only path; printed advisory; KVK counter backup; transparency | UX + PO | Task completion, satisfaction, usage |
| R10 | Rural connectivity instability | Infrastructure | H | M | Offline-first (hard requirement); encrypted idempotent sync; 4G fallback; media queue | DO | Sync backlog, offline matrix |
| R11 | Field hardware failure (printer, display, power) | Infrastructure | M | M | UPS; spares kit; re-provisioning runbook; KVK counter coverage; MTBF tracking | HW | Device uptime, MTBF |
| R12 | DPDP timeline (full obligations May 2027 vs trial Jul 2027) | Compliance | M | H | Program starts M1; milestones M1→M13; pre-trial gate M9; grievance officer M1 | DP | Milestone tracking |
| R13 | KB coverage gaps (crops/diseases not in KB) | Content | M | M | KB v1 covers 8 regional crops; unanswered-question backlog; KnowledgeOps monthly; escalation to scientist | KE | Retrieval recall, knowledge age |
| R14 | Sync conflicts / data loss | Technical | L | H | Append-only + idempotency (conflicts structurally impossible for case data); media dedup by content hash; gap detection + repair | BE | Sync tests, gap alerts |
| R15 | Model license/ToU changes (Gemma ToU, Llama CL) | Legal | L | M | License tracking in registry; Apache-2.0 alternatives (Sarvam-M, Qwen); egress monitoring | PL | License review per release |
| R16 | Prompt injection / LLM misuse | AI safety | M | M | 7-layer defense (§14.5); red-team CI; monitoring; kill switch | SE | Red-team results, injection attempts |
| R17 | Skill gaps (Telugu ML, Flutter) | Organizational | M | M | Hiring M1; contractors with IP assignment; pairing; Telugu-fluent QA/UX | PL | Hiring status, handover notes |
| R18 | Scope creep ("district scale", extra channels) | Program | M | M | Explicit exit criteria; 18-month scope locked; change control via release framework | PL | Scope change log |
| R19 | Key-person dependency | Organizational | M | M | Handover notes; pairing on core services; runbooks (§17.4); documentation | PL | Bus-factor review quarterly |
| R20 | Trial contamination (unfrozen changes during trial) | Program | M | H | Change-freeze policy; version-tuple audit daily; staging-only changes; trial protocol | QA | Version-tuple audit

**Risk review cadence:** weekly during trial (M10–M13); bi-weekly otherwise. Every risk with likelihood H or impact H has a named owner and a monitor metric in the §16.3 catalog.

---

# 16. KPIS & SUCCESS METRICS

Metrics are the system's feedback loop: they drive trial acceptance, operational SLOs, and the learning pipeline. The full catalog is §16.3 (referenced from §3.10, §9.1.2, §9.1.8, §9.4.8, §9.5.4). All metrics are computed from the case graph, service telemetry, and evaluation runs — no manual reporting for daily metrics.

## 16.1 Trial success metrics (M10–M13)

| Metric | Target | Notes |
|---|---|---|
| Correction-rate trend | Decreasing month-over-month | Scientist corrections per reviewed case |
| First-contact resolution rate | Baseline → trending up | Resolved without escalation |
| **Zero unapproved prescriptions** | **0 (hard)** | No prescription printed/delivered without scientist approval |
| **Zero regulatory violations** | **0 (hard)** | No blocked intervention reaches output |
| Review SLA compliance | ≥ 95% (trial: same day) | Prescription → scientist decision |
| Outcome capture rate | ≥ 50% | Advice marked worked/partial/failed/worsened/unknown |
| Farmer satisfaction | ≥ 4/5 | Post-case survey (kiosk + WhatsApp) |
| Task completion (UAT) | ≥ 80% | Pre-trial UAT (§13.6) |

## 16.2 Operational KPIs

| KPI | Target |
|---|---|
| Kiosk availability (service hours) | ≥ 99% |
| Central availability | ≥ 99.5% |
| p95 question → information answer | < 8 s |
| Print success rate | ≥ 99% |
| Sync backlog (reconnect → complete) | < 1 h |
| Weather freshness | Forecast < 6 h, nowcast < 2 h |
| ASR latency p95 | Vaani-Whisper < 3 s; SraVaani < 1.5 s |
| Review SLA | ≤ 24 h (trial: same day), ≥ 95% compliance |

## 16.3 Metric catalog

One table, all metrics. Sources: case graph, service telemetry (OpenTelemetry), evaluation runs, dashboards. "Per release" = computed in the CI evaluation gate (§13.3); "Daily" = dashboard metric.

| Category | Metric | Definition | Source | Target | Frequency |
|---|---|---|---|---|---|
| AI quality | ASR confidence | Mean/p50/p95 transcript confidence | speech-service | Per-engine baseline | Per utterance |
| AI quality | ASR correction rate | Farmer corrections of transcripts | case graph | Trending down | Daily |
| AI quality | ASR entity accuracy | Correct crop/pest/product/location recognition | Agri-vocab set eval (§13.3) | Per speech version | Per release |
| AI quality | Per-engine WER | Word error rate on Kurnool agri-vocabulary set | Custom eval | Primary beats alternative by gate margin | Per release |
| AI quality | TTS MOS | Intelligibility + acceptability of Piper Telugu voice | Farmer MOS test | ≥ 4/5 | Per release |
| AI quality | Intent accuracy | Correct request classification | Golden cases | ≥ framework threshold | Per release |
| AI quality | Retrieval recall | Authoritative evidence retrieved | RAGAS (KB retrieval set) | Per KB/model release | Per release |
| AI quality | Groundedness | Generated claims supported by evidence | RAGAS + DeepEval | 100% evidence-ID on prescriptions | Per release |
| AI quality | Clarification rate | Cases requiring clarification | case graph | Baseline → stable | Daily |
| AI quality | Clarification quality | Critical missing data requested | Golden cases + UAT | Per release | Per release |
| AI quality | Telugu comprehension | Target-user understanding | UAT (§13.6) | ≥ 80% task completion | Per release + monthly |
| AI quality | Observation accuracy | Correct visual observations (lesion, discoloration, insect, distortion, wilting) | Image set eval | Per vision version | Per release |
| AI quality | Classifier F1 per class | Disease/pest classifier F1 per class | Image set eval | Per class | Per release |
| AI quality | Image quality failure rate | Photos rejected for quality | image-service | Trending down | Daily |
| Decision quality | First-contact resolution rate | Resolved without escalation | case graph | Trending up | Daily |
| Decision quality | Scientist correction rate | Scientist changes per reviewed case | case graph | Trending down | Daily |
| Decision quality | Correction type distribution | Distribution of the 10 delta types (§4.3.2) | decision_deltas | Failure-mode analysis | Weekly |
| Decision quality | Correction severity | Low/high-risk correction distribution | decision_deltas | High-risk share trending down | Weekly |
| Decision quality | Failed-advice rate | Advice marked failed | outcome-service | Trending down | Weekly |
| Decision quality | Repeat-failure rate | Same intervention fails again | outcome-service | Trending down | Weekly |
| Decision quality | Unresolved case rate | Cases not resolved | case graph | Trending down | Weekly |
| Decision quality | Rule-block count | Interventions blocked by rules | rules-service | Safety/regulatory monitoring | Daily |
| Decision quality | Rule compliance | No model output bypasses blocking rules | Rule suite + property tests | **0 violations (hard)** | Per release |
| Safety | Unapproved prescriptions | Prescriptions without scientist approval | Gate audit | **0 (hard)** | Daily |
| Safety | Regulatory violations | Blocked interventions reaching output | Rule audit | **0 (hard)** | Daily |
| Safety | L4 incident count | Safety/regulatory incidents | escalation-service | 0 | Daily |
| Safety | Injection attempts | Prompt-injection attempts detected | Monitoring | Logged + reviewed | Daily |
| Escalation | Escalation rate | Cases escalated (L2–L4) | escalation-service | Uncertainty monitoring | Daily |
| Escalation | Time-to-expert-response | Escalation → scientist action | escalation-service | ≤ SLA (§4.4) | Daily |
| Escalation | Review SLA compliance | Prescription → decision within SLA | review-service | ≥ 95% | Daily |
| Outcome | Outcome capture rate | Advice with recorded outcome | outcome-service | ≥ 50% | Weekly |
| Outcome | Outcome verification rate | Outcomes verified against expected observation | outcome-service | Trending up | Weekly |
| Outcome | Outcome distribution | worked/partial/failed/worsened/unknown | outcome-service | Monitoring | Weekly |
| Operational | Kiosk availability | Uptime in service hours | Device agent heartbeat | ≥ 99% | Daily |
| Operational | Central availability | Uptime | Synthetic probe | ≥ 99.5% | Daily |
| Operational | Information answer latency p95 | Question → first spoken response | OTel traces | < 8 s | Daily |
| Operational | Prescription latency | Question → printed prescription | OTel traces | Review SLA applies | Daily |
| Operational | Print success rate | Successful prints | Print job log | ≥ 99% | Daily |
| Operational | Sync backlog | Events pending sync | Sync telemetry | < 1 h | Daily |
| Operational | Weather freshness | Age of weather snapshot | weather-service | Forecast < 6 h, nowcast < 2 h | Daily |
| Operational | Device uptime | Device availability | Device agent | ≥ 99% | Daily |
| Operational | MTBF | Mean time between hardware failures | Device log | Trending up | Monthly |
| Knowledge/learning | Knowledge age | Age of KB entries | knowledge-service | Staleness detection | Weekly |
| Knowledge/learning | Candidate rule count | Rule candidates generated | learning-service | Learning pipeline workload | Weekly |
| Knowledge/learning | Candidate knowledge count | Knowledge candidates generated | learning-service | Learning pipeline workload | Weekly |
| Knowledge/learning | Promotion rate | Candidates → production | learning-service | Monitoring | Monthly |
| Knowledge/learning | Provenance completeness | Candidates with complete provenance (11 fields) | learning-service | 100% | Per release |
| Knowledge/learning | Lexicon size | Local-term mappings | lexicon | Growth | Monthly |
| Knowledge/learning | KB entry count | KB entries per crop | knowledge-service | Growth | Monthly |
| Knowledge/learning | Correction→production lag | Days from correction to production | learning-service | Trending down | Monthly |
| Modality — voice | Voice share of inputs | Fraction of inputs via voice | input-orchestrator | Monitoring | Daily |
| Modality — voice | ASR correction rate (voice) | Farmer transcript corrections | case graph | Trending down | Daily |
| Modality — touch | Touch completion rate | Cases completed with ≤ 1 free input | case graph | Monitoring | Daily |
| Modality — touch | Picker accuracy | Selection vs final interpretation | case graph | Monitoring | Weekly |
| Modality — touch | Quick-reply usage | WhatsApp quick-reply usage | WhatsApp adapter | Monitoring | Weekly |
| Modality — text | Text entity accuracy | Correct entity extraction from text | case graph | Monitoring | Weekly |
| Modality — text | Transliteration usage | Telugu Latin → script usage | text normalizer | Monitoring | Weekly |
| Modality — text | Text share of inputs | Fraction of inputs via text | input-orchestrator | Monitoring | Daily |
| Modality — picture | Image quality failure rate | Photos rejected for quality | image-service | Trending down | Daily |
| Modality — picture | Multi-photo request success rate | Requested missing views received | image-service | Monitoring | Weekly |
| Modality — picture | Picture share of inputs | Fraction of inputs via picture | input-orchestrator | Monitoring | Daily |
| Modality — cross | Mixed-case ratio | Cases using ≥ 2 modalities | case graph | Monitoring | Weekly |
| Modality — cross | Cross-modal contradiction rate | Contradictions across modalities | case graph | Monitoring | Weekly |
| Modality — cross | Per-modality FCR | First-contact resolution per modality | case graph | Monitoring | Weekly |
| Channel/segment | Channel-wise performance | FCR/correction rate per channel | case graph | Monitoring | Weekly |
| Channel/segment | Crop-wise performance | FCR/correction rate per crop | case graph | Monitoring | Weekly |
| Channel/segment | Geography-wise performance | FCR/correction rate per mandal | case graph | Monitoring | Monthly |
| Compliance | Consent capture rate | Sessions with recorded consent | case graph | 100% | Daily |
| Compliance | Grievance count/SLA | Grievances + resolution within 90 days | Grievance log | ≤ 90 days | Monthly |
| Compliance | Retention job success | Retention/deletion jobs completed | Retention job | 100% | Monthly |
| Compliance | Audit completeness | Audit log completeness | Audit log | 100% | Quarterly |

## 16.4 Surveillance analytics

- **Review signal only** — not enforcement, not individual scoring.
- **Aggregate only**, mandal-level minimum granularity.
- **No individual farmer identification** in dashboards (source §30).
- Pest/disease incidence trends, crop-wise, season-wise.
- Access: scientist/admin/auditor only; access logged.
- Data: case graph (pseudonymized), media (blurred).
- Use: KVK planning, demonstration planning, early warning (with IMD agromet).

## 16.5 Learning metrics

| Metric | Definition | Target |
|---|---|---|
| Candidate volume | Candidates per channel (knowledge/rule/training/lexicon) | Monitoring |
| Promotion rate | Candidate → production | Monitoring |
| Provenance completeness | Candidates with complete provenance (11 fields) | 100% |
| Lexicon growth | Term count; correction→lexicon lag | Growth; lag trending down |
| KB growth | Entry count per crop | Growth |
| Correction→production lag | Median days | Trending down |
| Pattern discovery | Patterns found (min support N ≥ 5, consistency ≥ 80%) | Zero blocking counterexamples |
| Fine-tuning | Runs, gate pass rate | Per gate |

## 16.6 Reporting cadence

| Report | Audience | Cadence | Content |
|---|---|---|---|
| Daily operations dashboard | On-call / KVK operator | Daily | Availability, latency, print, sync, alerts |
| Trial daily safety review | Scientists + platform | Daily (trial) | Safety metrics, corrections, escalations |
| Weekly KVK review | KVK + platform team | Weekly | Correction patterns, queue SLA, incidents |
| Monthly institutional report | ANGRAU / ICAR | Monthly | Metrics vs acceptance criteria, learning candidates, safety incidents |
| Per-release evaluation report | Release authority | Per release | RAGAS / DeepEval / red-team / benchmarks |
| Quarterly compliance report | DPDP lead / auditor | Quarterly | DPDP obligations, access review, retention audit |
| Annual audit | Institution | Annual | Full traceability sample, security audit, DR exercise |

---

# 17. OPERATIONAL MODEL

How the system is run day-to-day: SLOs, on-call, maintenance, runbooks, backup/DR, KnowledgeOps, and the ownership handover. This is what the Phase 15 operations handover (§10.2) delivers.

## 17.1 SLOs

| SLO | Target | Measurement | Error budget |
|---|---|---|---|
| Kiosk availability (service hours 08:00–18:00) | ≥ 99% | Device agent heartbeat | 1% |
| Central availability | ≥ 99.5% | Synthetic probe | 0.5% |
| Information answer latency p95 (question → first spoken response) | < 8 s | OTel traces | — |
| ASR latency p95 | Vaani-Whisper < 3 s; SraVaani < 1.5 s | OTel traces | — |
| Review SLA (prescription → scientist decision) | ≤ 24 h (trial: same day); compliance ≥ 95% | Review queue | — |
| Print success rate | ≥ 99% | Print job log | — |
| Sync backlog (reconnect → complete) | < 1 h | Sync telemetry | — |
| Weather freshness | Forecast < 6 h, nowcast < 2 h | weather-service | — |
| Rollback RTO | ≤ 15 min/device | Drill | — |
| **Zero unapproved prescriptions** | **0** | Gate audit | **Hard (no budget)** |
| **Zero regulatory violations** | **0** | Rule audit | **Hard (no budget)** |

**Error budget policy:** budget exhausted → change freeze (no non-critical releases) until recovered. Hard SLOs (zero unapproved prescriptions, zero regulatory violations) have no budget — any violation is an incident (§14.7).

## 17.2 On-call & escalation

- **L1: KVK operator** (on-site, service hours) — first response, runbook execution.
- **L2: Platform on-call** (BE/DO rotation) — ≤ 1 h response in service hours; extended 08:00–20:00 during trial.
- **L3: Vendor** (hardware/GPU/connectivity) — per contract.
- **Escalation path:** L1 → L2 → L3; SEV1/SEV2 → immediate page + incident commander.
- **Trial extended coverage:** 08:00–20:00 (M10–M13).
- **Rotation:** 2-week rotation, 4 on-call slots; handover notes.
- **Communication:** alerts via WhatsApp (ops group) + email; incident channel.

## 17.3 Maintenance cadence

| Item | Cadence | Notes |
|---|---|---|
| Security patches (OS/dependencies) | ≤ 7 days from CVE publication (critical ≤ 48 h) | CI vulnerability scanning; staged rollout |
| Minor platform releases | Monthly | KB + rules + app |
| KB release | Monthly | KnowledgeOps cadence (§17.6) |
| Rules release | Per regulatory update + quarterly audit | PPQS re-verification |
| Model release | Per evaluation gate | Shadow → canary → production |
| Restore drill | Quarterly | PITR + MinIO + edge re-provision |
| Full DR exercise | Annual | Central failover |
| Access review | Quarterly | RBAC |
| Compliance review | Quarterly | DPDP |
| Change freeze | Trial period (M10–M13) + 1 week before institutional reviews | Critical safety fixes only |

## 17.4 Runbooks

| # | Runbook | Trigger | Key steps |
|---|---|---|---|
| 1 | Printer failure | Paper-out / USB error / job failure | Check paper/USB; restart printer service; verify idempotent `print_id` (no duplicates); fallback delivery (QR + screen + WhatsApp); log |
| 2 | GPU OOM / LLM unavailable | OOM kill / queue timeout | Check GPU queue; evict low-priority; SraVaani CPU path for ASR; mark advisory degraded; restart Ollama if needed |
| 3 | Sync backlog | Backlog > threshold / gap detected | Check connectivity; verify idempotency; gap repair; monitor until clear |
| 4 | Weather stale | Age > 6 h (forecast) / 2 h (nowcast) | Verify IMD API + whitelist; manual snapshot entry; mark STALE; UNKNOWN spray window; operator alert |
| 5 | KB/rules update | Scheduled release | Verify signed bundle; canary device; monitor; fleet rollout; rollback if needed |
| 6 | Model rollback | Safety regression / SLO breach | One-command restore of previous version tuple; verify version; notify release authority |
| 7 | Device re-provision | Hardware failure / theft / corruption | Secure old device (wipe); image new device from signed bundle; register device certificate; sync; verify |
| 8 | DPDP breach | Suspected PII/media exposure | Contain; assess; DPBI within 72 h if personal data; notify institution; post-incident review; learning capture |
| 9 | UPS / power failure | Power loss / UPS low | Verify graceful shutdown; state consistency on restart; no case corruption; generator check |
| 10 | WhatsApp webhook down | Webhook failure / template rejection | Verify Meta status; re-verify token; check template status; kiosk + web continue (case continuity); billing check |

## 17.5 Backup / DR operations

- **RPO ≤ 5 min** (WAL PITR); **RTO ≤ 4 h** (central failover, manual at pilot).
- Edge re-provision < 1 day.
- Quarterly restore drill (PITR + MinIO + edge).
- Annual full DR exercise.
- Offsite copy of daily base backup.
- MinIO replication to secondary site.
- Backup monitoring: alert on backup failure.

## 17.6 KnowledgeOps operations

- **KB monthly cadence:** ingest → normalize → expert review → version → signed bundle → edge.
- **Monitoring:** retrieval recall, knowledge age, unanswered-question backlog.
- **Retirement:** expired/superseded entries (effective dates), archived not deleted.
- **Evidence ledger audit:** quarterly sample (provenance completeness).
- **Unanswered-question backlog:** weekly review, top gaps → KB priority.
- **Lexicon:** correction → lexicon candidate → review → release (lag tracked).
- **KB growth tracking:** entry count per crop.

## 17.7 Ops ownership & handover

- **M17: handover package signed by KVK + ANGRAU.**
- **Contents:** runbooks, SLOs, on-call rotation, training (operator + scientist), DPDP operational compliance check, final audit report, documentation.
- **Ownership:** KVK = day-to-day operations (operator, scientists); platform team = L2 support (contract/retained); ANGRAU = governance.
- **Transition:** shadow period (2 weeks), then KVK-led with platform on-call.
- **Decommissioning plan** for pilot hardware (data destruction per retention).

---

# 18. APPENDICES

## Appendix A: Research references

| Topic | Source | URL |
|---|---|---|
| DPDP Act 2023 + Rules 2025 (timeline, obligations) | dpdpa.com; seclore.com; lexology.com; PIB | https://www.dpdpa.com · https://www.seclore.com · https://www.lexology.com · https://pib.gov.in |
| WhatsApp Business Cloud API pricing/policy | Meta Business Help Center | https://business.facebook.com |
| IMD weather/agromet API | IMD | https://api.imd.gov.in |
| KVK Banavasi (institution, crops, coordinator) | KVK website | https://kvkbanavasi-angrau.org |
| Vaani-Whisper Telugu ASR (primary) | Hugging Face (ARTPARK-IISc) | https://huggingface.co/ARTPARK-IISc/whisper-large-v3-vaani-telugu |
| SraVaani-1.0 ASR (fast fallback) | Hugging Face (ARTPARK-IISc) | https://huggingface.co/ARTPARK-IISc/SraVaani-1.0 |
| SraVaani NeMo fine-tuning | GitHub (ARTPARK-Speech-Models) | https://github.com/ARTPARK-Speech-Models/SraVaani |
| Fine-grained crop disease classification (open VLM limits) | WACV 2026 HARVEST-Vision | (conference paper) |
| Sarvam-M 24B (central Telugu LLM) | Sarvam AI | https://sarvam.ai |
| Ollama (edge LLM runtime) | Ollama | https://ollama.com |
| pgvector (vector search) | pgvector | https://github.com/pgvector/pgvector |
| BGE-M3 + BGE-Reranker-v2-M3 (retrieval) | BAAI | https://huggingface.co/BAAI |
| Piper Telugu TTS | OHF-Voice | https://github.com/OHF-Voice/piper1-gpl |
| PPQS / CIB&RC regulatory lists | CIB&RC | (gazette) |
| Keycloak (identity) | Keycloak | https://www.keycloak.org |
| MLflow 3 + DVC 3 (MLOps) | MLflow / DVC | https://mlflow.org · https://dvc.org |
| RAGAS / DeepEval / promptfoo (evaluation) | — | https://docs.ragas.io · https://deepeval.com · https://www.promptfoo.dev |
| Gemma 3 12B / Llama 3.1 8B (edge LLM) | Google / Meta | https://ai.google.dev/gemma · https://ai.meta.com/llama |

## Appendix B: Glossary

| Term | Meaning |
|---|---|
| ASR | Automatic Speech Recognition |
| CST | Case-to-Solution Tree |
| PHI | Pre-Harvest Interval (pesticide) |
| PPE | Personal Protective Equipment |
| WER | Word Error Rate |
| CER | Character Error Rate |
| VAD | Voice Activity Detection |
| mTLS | Mutual TLS |
| RAG | Retrieval-Augmented Generation |
| VLM | Vision-Language Model |
| LoRA | Low-Rank Adaptation (fine-tuning) |
| shadow / canary | Deployment modes (hidden comparison / subset rollout) |
| ULID | Universally Unique Lexicographically Sortable Identifier |
| ESC/POS | Printer command protocol |
| DPDP | Digital Personal Data Protection (Act 2023) |
| DPBI | Data Protection Board of India |
| KVK | Krishi Vigyan Kendra |
| ANGRAU | Acharya N.G. Ranga Agricultural University |
| ICAR | Indian Council of Agricultural Research |
| FPO | Farmer Producer Organization |
| mandal | Administrative subdivision (Andhra Pradesh) |
| BHASHINI | Government Indian-language speech platform |
| Vaani | Telugu speech dataset (IISc) |
| SraVaani | FastConformer ASR model (ARTPARK-IISc) |
| PPQS | Pesticide (banned/restricted) list |
| CIB&RC | Central Insecticides Board & Registration Committee |
| IMD | India Meteorological Department |
| agromet | Agricultural meteorology |
| KALP | IMD agromet advisory program |
| SANKALP | IMD agromet advisory program |
| HNSW | Hierarchical Navigable Small World (vector index) |
| BM25 | Best Matching 25 (sparse retrieval) |
| ONNX | Open Neural Network Exchange |
| LUKS | Linux Unified Key Setup (disk encryption) |
| PITR | Point-In-Time Recovery |
| RPO / RTO | Recovery Point / Time Objective |
| SLO / SLA | Service Level Objective / Agreement |
| BSP | Business Solution Provider (WhatsApp) |
| WAF | Web Application Firewall |
| OIDC | OpenID Connect |
| MOS | Mean Opinion Score (speech quality) |
| NDCG | Normalized Discounted Cumulative Gain |
| κ | Cohen's kappa (inter-rater agreement) |
| fine-tune | Adapt a pre-trained model on domain data |
| holdout | Reserved evaluation data |
| drift | Change in model/data distribution over time |
| provenance | Origin/lineage of a learning artifact |
| delta | Decision delta (correction record) |
| golden case | Scripted end-to-end test case |
| red team | Adversarial safety testing |
| runbook | Operational procedure document |
| change freeze | Period where non-critical changes are blocked |
| version tuple | Model + knowledge + rules + prompt + speech + schema version |
| lexicon | Local terminology mapping dictionary |
| nowcast | Very short-range weather forecast |
| pseudonymity | Identity replaced by a pseudonym |
| kiosk mode | Locked single-app device mode |
| beamforming | Directional microphone array processing |
| wake word | Trigger phrase to activate voice |
| privacy shutter | Physical camera cover |
| NVMe | Non-Volatile Memory Express (storage) |
| K3s | Lightweight Kubernetes |
| MQTT | Message Queuing Telemetry Transport |
| QoS | Quality of Service (MQTT delivery level) |
| webhook | HTTP callback endpoint |
| idempotent | Operation safe to repeat |
| JSONB | PostgreSQL binary JSON type |
| GIN | Generalized Inverted Index (PostgreSQL) |
| cross-encoder | Reranker model scoring query-document pairs |
| reranker | Model reordering retrieval results |
| embedding | Vector representation of text/image |
| NeMo | NVIDIA NeMo (speech framework) |
| FastConformer | ASR architecture |
| TDT-CTC | Transducer + CTC hybrid decoder |
| Whisper | OpenAI ASR model family |
| ffmpeg | Media processing tool |
| Opus | Audio codec |
| UAT | User Acceptance Testing |
| RACI | Responsible / Accountable / Consulted / Informed |
| FTE | Full-Time Equivalent |
| BOM | Bill of Materials |
| DR | Disaster Recovery |
| MTBF | Mean Time Between Failures |
| on-call | Rotating operational responder |
| SDF | Sensitive Data Flow (classification, D6) |
| consent manager | DPDP Phase 2 framework role |
| fiduciary | DPDP data controller role |
| data principal | DPDP data subject (farmer) |

## Appendix C: KVK Banavasi context (verified)

- **Established:** 31 Oct 2010 by ICAR with ANGRAU.
- **Location:** Banavasi village, Yemmiganur mandal, Kurnool district, Andhra Pradesh.
- **Distances:** ~75 km from Kurnool HQ; 7 km from Yemmiganur; 21 km from Mantralayam; on the Kurnool–Adoni road.
- **Website:** kvkbanavasi-angrau.org.
- **Programme Coordinator:** Dr. K. Raghavendra Chowdary (kvk.banavasi@angrau.ac.in).
- **Crops (site-mentioned):** red gram, foxtail millet (6500 ha), browntop millet (1200 ha), cotton, medicinal crops.
- **Region:** scarce-rainfall zone.
- **Regional crops (KB v1 scope):** cotton, paddy, groundnut, maize, arhar (red gram), castor, foxtail/barnyard millet, chilli, horticulture.

## Appendix D: Open questions

| ID | Question | Owner | Due |
|---|---|---|---|
| D1 | Offline prescription policy — can prescriptions be printed offline (pending approval) or only information/advisory? | PO + institution | Phase 0 |
| D2 | Face-blur policy confirmation — confirm default blur + original on request + consent | PO + DP | Phase 0 |
| D3 | WhatsApp BSP choice — AiSensy/WATI or direct Meta? | BE + PO | Phase 0 (M1) |
| D4 | IMD whitelist status — confirm whitelist approval | BE | M1–M2 |
| D5 | Month-3 supervision threshold — what correction-rate/metric threshold triggers increased supervision in trial month 3? | PO + SC | M9 |
| D6 | Sensitive-data classification — confirm whether farmer phone/location is sensitive personal data under DPDP (affects consent + breach notification) | DP | M2 |
| D7 | GPU node owned vs rented — A100/4090 owned or cloud rental? | DO + PL | M9 |
| D8 | Kiosk site survey — power, network, mounting at KVK site | HW | M1–M2 |
| D9 | Second kiosk site — which site for the scale proof (M15+)? | PO + ANGRAU | M12 |
| D10 | Telugu QA eval set composition — crop/question-type distribution for the ≥ 300 questions | KE + SC | M3 |

## Appendix E: Document change log

| Version | Date | Change |
|---|---|---|
| v1.0 | 26 Sep 2026 | Initial complete roadmap §1–§18; user-specified ASR models (Vaani-Whisper primary, SraVaani fallback) + input modalities (voice/touch/text/picture) incorporated; WhatsApp billing verified/corrected; DPDP timeline verified |
