# 00 — Project Context

> Source of truth: `../AI_Kiosk_v2_Project_Roadmap.md` (v1.0, 26 Sep 2026) and
> `../AI_Kiosk_v2_Multimodal_Case_to_Solution.md` (v2.0). This document is the
> orientation layer for everyone working in this repository.

## 1. What we are building

A **governed, offline-first, multimodal agricultural decision-support platform** for
**KVK Banavasi** (ICAR Krishi Vigyan Kendra, hosted by ANGRAU), Yemmiganur Mandal,
Kurnool district, Andhra Pradesh.

A farmer interacts through **four first-class input modalities — voice, touch, text,
and picture** — on a kiosk (and later WhatsApp/web). The system builds a persistent
**Case-to-Solution Tree (CST)**:

1. Interprets the input (ASR / text normalization / image observations).
2. Cross-checks understanding with the farmer (confirmation gates).
3. Maintains competing hypotheses with evidence for/against.
4. Asks targeted verification questions (each with a decision purpose).
5. Retrieves authoritative evidence (hybrid retrieval over the KB).
6. Applies **deterministic** regulatory / agronomic / weather rules.
7. Drafts a grounded answer with a local LLM (schema-validated).
8. Routes high-risk outputs through a **scientist gate** before any prescription is
   printed or delivered.
9. Tracks outcomes (worked / partial / failed / worsened / unknown); failures trigger
   reassessment and escalation — **never automatic re-prescription**.
10. Converts scientist corrections into **decision deltas** with the full context
    auto-attached, classified into governed learning channels (knowledge / rules /
    training data / case memory / language).

## 2. Institutional context

| Item | Value |
|---|---|
| Institution | KVK Banavasi (est. 31 Oct 2010), ICAR / ANGRAU |
| Location | Banavasi village, Yemmiganur Mandal, Kurnool district, AP (~75 km from Kurnool, Kurnool–Adoni road) |
| Coordinator | Dr. K. Raghavendra Chowdary (kvk.banavasi@angrau.ac.in) |
| Language | Telugu-first (Kurnool is Telugu-speaking); English secondary; local/dialectal vocabulary → governed lexicon |
| Connectivity | Rural, intermittent → **offline-first is a hard requirement** |
| KB v1 crops | Cotton, paddy, groundnut, maize, arhar (red gram), castor, foxtail/barnyard millet, chilli, horticulture |
| Region | Scarce-rainfall zone |

## 3. Problem statement (P1–P10)

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

## 4. Users & personas

| Persona | Needs | Primary channels |
|---|---|---|
| **Farmer** (diverse literacy, Telugu-speaking) | Fast, simple, voice-friendly answers; printed prescription; no repeated questions | Kiosk (voice/touch/text/picture), WhatsApp |
| **KVK Scientist** (final authority during trial) | Minimal-effort correction; full context auto-attached; review queue; voice/text/image feedback | Scientist portal (web), WhatsApp |
| **Kiosk Operator** | Device health, printer status, session reset, basic troubleshooting | Kiosk admin screen |
| **Platform Administrator** | Device management, knowledge/rule/model releases, user roles | Admin console |
| **Auditor** | Read-only trace of any prescription to versions, evidence, approvals | Audit console |
| **Institutional reviewer** (KVK/ANGRAU/ICAR) | Trial metrics, safety incidents, learning outcomes | Dashboards + reports |

## 5. Output classes & risk tiers

| Class | Example | Control |
|---|---|---|
| **Information** (low risk) | Explain a pest lifecycle | Grounded evidence; may answer directly |
| **Diagnosis support** (medium risk) | Possible pest/disease candidates | Evidence + confidence + minimal cross-check + ≥ 1 targeted question |
| **Advisory** (medium-high risk) | Management options | Knowledge + rules + confirmation gate |
| **Prescription** (high risk) | Specific product/formulation/dose/timing/PHI/PPE | Full safety pipeline + regulatory check + weather check + **scientist approval** + locked output + print/QR |

**v2 rule:** an apparently obvious solution is still a hypothesis until its required
verification gates are satisfied.

## 6. Non-negotiable design principles

| # | Principle |
|---|---|
| 1 | **The LLM is not the authority.** LLM = language/reasoning assistant. KB = evidence. Rules engine = safety gate. Scientist = authority. Prescription service = controlled output. |
| 2 | **No uncontrolled self-modification.** Corrections are learning signals, not instructions to rewrite production. All production changes pass validation + approval + versioning. |
| 3 | **Deterministic safety.** Regulatory, dose, PHI/PPE and weather-window constraints live in a testable rules engine — never only in model weights. |
| 4 | **Reproducibility.** Every prescription traces to the exact version tuple (model + knowledge + rules + prompt policy + speech + schema). |
| 5 | **Clarification over forced certainty.** Ambiguity produces confirmation questions and competing hypotheses, never silent guesses. |
| 6 | **Offline-first.** Core service (information, basic AI, rules, printing) works without network; sync is encrypted, idempotent, resumable. |
| 7 | **Channel-agnostic intelligence.** Kiosk, WhatsApp, web and operator channels are adapters into one canonical case service; a case can move between channels without losing context. |
| 8 | **Outcome-aware learning.** The system learns from the full case lifecycle — meaning, misunderstanding, evidence, decision, correction, action, outcome, escalation — not only from corrections. |
| 9 | **Privacy by design.** Minimal PII, consent-aware collection (DPDP Act 2023), no automatic use of farmer conversations for training. |

## 7. Input modalities (first-class)

| Modality | Kiosk | WhatsApp | Web/Mobile | Scientist portal |
|---|---|---|---|---|
| **Voice** | Telugu/English ASR via mic array; TTS answers | Voice notes (ASR) | Voice input (optional) | Voice feedback → structured correction |
| **Touch** | Large-button guided flow, crop/stage/pest pickers, confirmation gates | Tap-to-select quick replies | Touch/click UI | Approve / Correct / Escalate buttons |
| **Text** | On-screen keyboard (Telugu + Latin), local-term dictionary | Text messages | Chat text | Text notes, structured fields |
| **Picture** | Camera capture (whole plant, leaf, pest close-up, field context) | Photo upload (multiple) | Photo upload | Reference/annotated images |

All four modalities map to the **same canonical case object** (`case_id`), so a farmer
can start by voice at the kiosk, send a photo on WhatsApp, and have the scientist
review the complete tree on the web portal.

**Modality principles** (roadmap §9): convergence on one `Input` node type; free
mixing within a case; modality-aware confidence (touch = 1.0, ASR/text = model
confidence, picture = per-observation states); every modality has a fallback — never
a dead end; modality recorded end-to-end in `case_node.source`.

## 8. Delivery at a glance

| Item | Value |
|---|---|
| Total duration | **18 months** (5 waves, 16 phases: 0–15) |
| Supervised trial | 3 months (Wave 4, M10–M13), scientist reviews every prescription |
| Peak team | 14–16 FTE |
| Production target | 1 kiosk (KVK Banavasi) → district-scale architecture ready |
| Core stack | Python 3.12 / FastAPI · PostgreSQL 17 + pgvector 0.8.2 · Ollama 0.34.x (Gemma 3 12B / Llama 3.1 8B) · Vaani-Whisper + SraVaani + Piper (Telugu) · BGE-M3 retrieval · Flutter kiosk · Keycloak 26 · EMQX 5 · OpenTelemetry · Docker / K3s |
| Key external dependencies | IMD weather API (IP whitelist), PPQS/CIB&RC regulatory data, BHASHINI speech APIs (online mode), WhatsApp Business Cloud API (Meta/BSP) |

| Wave | Months | Phases | Theme |
|---|---|---|---|
| **W1 — Foundation** | M1–M3 | 0, 1 (+ KB/rules/kiosk MVP workstreams) | Governance, canonical schema, platform skeleton, kiosk MVP (touch+text+print), KB v1, rules v1 |
| **W2 — Intelligence** | M3–M8 | 2–8 (+ AI/RAG, voice) | Channels, CST, cross-correction, image pipeline, verification, similar cases, scientist multimodal feedback |
| **W3 — Closed loop** | M7–M10 | 9–12, 14-foundation | Outcome/follow-up, escalation, learning sandbox, offline media sync, MLOps foundation |
| **W4 — Trial** | M10–M13 | 13 | Three-month scientist-supervised trial (frozen versions) |
| **W5 — Production & scale** | M13–M18 | 14-hardening, 15 | MLOps/KnowledgeOps hardening, multi-kiosk, multi-channel scale |

## 9. Repository map

```
ai-kiosk/
├── docs/                  # THIS DOCUMENTATION SET (00–09)
├── packages/
│   ├── canonical-schema/  # Pydantic v2 models for the entire case graph (Phase 1 core)
│   └── agri-rules/        # Deterministic rules engine (regulatory/PHI/PPE/weather gates)
├── services/              # 26 services (S1–S26) — see docs/02-modules.md
├── ui/
│   ├── scientist-portal/  # React 18 + TypeScript PWA (S21)
│   └── admin-console/     # React 18 + TypeScript PWA (S22)
├── kiosk/                 # Flutter kiosk app (S1) — voice/touch/text/picture/print
├── db/migrations/         # PostgreSQL 17 + pgvector DDL (0001–0006)
├── models/                # ML model registry: pins, licenses, cards, gates
├── evals/                 # Golden cases, agri-vocab ASR set spec, RAGAS/DeepEval/promptfoo
├── infra/                 # Docker, compose (dev central + edge), Caddy, K3s, Terraform
├── ci/workflows/          # GitHub Actions: CI, eval gate, release
└── scripts/               # bootstrap, migrations, eval gate, service-skeleton generator
```

## 10. How to read this documentation set

| Doc | Content |
|---|---|
| [00-project-context.md](00-project-context.md) | This file: what/why/who, modality table, delivery overview |
| [01-architecture.md](01-architecture.md) | C4 context + logical architecture, edge/central deployment, data flow, modality pipeline, security architecture, observability |
| [02-modules.md](02-modules.md) | **Context for every module S1–S26**: purpose, responsibilities, tech, interfaces, dependencies, scaling, build phase, invariants |
| [03-data-model.md](03-data-model.md) | Case graph, node payloads, decision delta, evidence ledger, KB, rules, learning, versioning, device/sync, table map, retention |
| [04-api-contracts.md](04-api-contracts.md) | All HTTP endpoints, MQTT topics, webhooks, conventions |
| [05-models.md](05-models.md) | **List of models**: ML catalog, selection gates, model cards, evaluation sets, version tuple |
| [06-tools.md](06-tools.md) | **Tool dependency registry**: versions, licenses, alternatives, pinning policy, dependency graph |
| [07-security-privacy.md](07-security-privacy.md) | Threat model, identity/access, device & artifact security, DPDP, LLM safety, media privacy, incident response, compliance checklist |
| [08-operations.md](08-operations.md) | Testing & evaluation strategy, red-team suite, offline matrix, KPIs/metric catalog, SLOs, on-call, runbooks, backup/DR, KnowledgeOps |
| [09-roadmap.md](09-roadmap.md) | Waves/phases/milestones, Gantt, acceptance criteria, team & roles, hardware, risk register, open questions |

## 11. Conventions used across this repository

- **IDs:** ULIDs (sortable, unique across edge + central).
- **Timestamps:** stored UTC, displayed `Asia/Kolkata`.
- **Text fields:** original language preserved; normalized fields separate. Bilingual
  content is `{te, en}` (Telugu-first).
- **Append-only:** nothing is overwritten; corrections and reinterpretations append
  new rows/nodes.
- **Typed everywhere:** Pydantic v2 at every API boundary; LLM output is
  schema-validated before entering the pipeline.
- **Cross-references** like "(roadmap §6.5)" point into
  `../AI_Kiosk_v2_Project_Roadmap.md`.
