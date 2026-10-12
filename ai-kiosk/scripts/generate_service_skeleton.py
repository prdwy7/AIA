#!/usr/bin/env python3
"""Generate the 19 skeleton services (roadmap §8; docs/02-modules.md).

Each skeleton follows the core-api conventions:
- hatchling build, src layout, `[tool.uv.sources]` workspace refs
- `_version.py` (avoids circular imports from the package root)
- FastAPI app with GET /health + GET /ready
- one smoke test (TestClient as context manager so lifespan runs)
- README with the full module context from docs/02-modules.md

Usage: python scripts/generate_service_skeleton.py
Idempotent: overwrites generated files, never touches rich services.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVICES_DIR = ROOT / "services"

# name -> module context (docs/02-modules.md)
SERVICES: dict[str, dict] = {
    "input-orchestrator": {
        "module": "S4",
        "purpose": "single entry point for all inputs across all modalities and channels.",
        "responsibilities": (
            "routes audio → speech-service, images → image-service, text → text normalizer, "
            "touch events → case-service directly. Owns session state. Enforces input quality "
            "gates. Creates immutable `Input` nodes and triggers interpretation. Enforces "
            "do-not-repeat memory at input time (e.g., already-received image views)."
        ),
        "tech": "Python/FastAPI; session state in Redis (central) / local Redis (edge); Pydantic v2 schemas.",
        "interfaces": "S5, S6, S7, channel adapters (inbound), lexicon (shared library).",
        "dependencies": "S5, S6, S7, Redis, `canonical-schema`, `agri-rules` (lexicon).",
        "scaling": "stateless compute; horizontal replicas behind the API gateway; session state externalized.",
        "built_in": "Phase 1.",
        "invariants": (
            "every input becomes an immutable `Input` node with modality metadata; mixed input "
            "within one case is always allowed; modality failure never dead-ends the case."
        ),
    },
    "case-service": {
        "module": "S7",
        "purpose": "owns the Case-to-Solution Tree — the canonical case service.",
        "responsibilities": (
            "append-only `case_node` writes; lifecycle state machine (roadmap §4.2) with "
            "transition guards; contradiction detection (across modalities); do-not-repeat "
            "memory; case continuity (short code, QR payload, cross-channel mapping); tree "
            "retrieval."
        ),
        "tech": (
            "Python/FastAPI; PostgreSQL (system of record); ULID IDs; DB-level append-only "
            "enforcement (triggers reject UPDATE/DELETE except status transitions)."
        ),
        "interfaces": "all core services; channel adapters (via S4); S8 (case embeddings); S15/S16.",
        "dependencies": "`canonical-schema`, PostgreSQL, MinIO (media refs).",
        "scaling": (
            "stateless API; Postgres partitioned by `case_id` range; read replicas at district "
            "scale. Hot path is small (node append + state transition)."
        ),
        "built_in": "Phase 1 (schema + skeleton) → Phase 3 (full tree semantics).",
        "invariants": (
            "the ONLY service that mutates case state (append-only; status transitions only); "
            "original farmer input and original system interpretation are immutable; every "
            "question has a recorded decision purpose; a case never silently changes "
            "crop/stage/problem — contradictions force a clarification branch; max 3 questions "
            "per branch by default."
        ),
    },
    "rules-service": {
        "module": "S9",
        "purpose": "deterministic policy package (API front for the `agri-rules` package).",
        "responsibilities": (
            "regulatory checks (banned/refused/restricted → BLOCK/REVIEW/CONDITION), "
            "crop/target, formulation, dose range, application method, weather window "
            "(GREEN/CAUTION/BLOCKED/UNKNOWN), PHI/PPE/environment, confidence gates, "
            "clarification policy. Pure functions over typed context; every rule has "
            "`test_cases[]`; counterexample search for rule candidates."
        ),
        "tech": (
            "Python policy package (`agri-rules`) — no external rule engine (Drools/OPA "
            "evaluated and rejected: Java/external-runtime overhead, weaker test ergonomics "
            "for agronomic logic); versioned as a signed artifact (RULE version in the "
            "version tuple)."
        ),
        "interfaces": "S11, S12, S17 (context input), S14 (counterexample search).",
        "dependencies": "`agri-rules` package, `regulatory_products` table, weather snapshots.",
        "scaling": "in-process library (no network hop); zero scaling concerns. Test suite runs in CI on every build.",
        "built_in": "WS-RULES (W1–W2); counterexample search in Phase 11.",
        "invariants": (
            "deterministic — the LLM cannot override; 100% of blocking rules covered by tests; "
            "property test: no blocked intervention can reach printable state; gaps surface as "
            "REVIEW, never silent pass."
        ),
    },
    "llm-service": {
        "module": "S10",
        "purpose": "local LLM inference management.",
        "responsibilities": (
            "Ollama runtime; structured output generation (JSON schema enforced before "
            "pipeline entry); prompt-policy versioning (PROMPT_POLICY_VERSION); "
            "shadow-model runner (candidate model answers live cases hidden, Phase 14); "
            "token/latency/VRAM telemetry; model hot-swap."
        ),
        "tech": (
            "Python; Ollama 0.34.x (Gemma 3 12B Q5_K_M primary, Llama 3.1 8B light); "
            "llama.cpp fallback; Pydantic v2 output validation; OpenTelemetry spans per call."
        ),
        "interfaces": "S11, S6 (vision observations), S26 (shadow orchestration), S20 (GPU state).",
        "dependencies": "models MODEL-0.1.0 / MODEL-0.1.1, Ollama.",
        "scaling": (
            "GPU queue with priority (prescription drafting > observations > shadow); OOM "
            "handling (evict to SraVaani/CPU path, queue); one GPU per kiosk at pilot."
        ),
        "built_in": "WS-AI (W2); shadow runner in Phase 14.",
        "invariants": (
            "LLM output must validate against the Pydantic schema before entering the "
            "rules/prescription pipeline; farmer text is data, never instructions; regulatory "
            "data is never injected into the LLM context as instructions."
        ),
    },
    "advisory-service": {
        "module": "S11",
        "purpose": "composes the grounded answer.",
        "responsibilities": (
            "retrieval evidence + rules evaluation + LLM draft → advisory/prescription draft "
            "with evidence-ID retention end-to-end; risk-tier assignment "
            "(information/diagnosis/advisory/prescription); verification-gate orchestration "
            "(Phase 6); confirmation-gate decisions (θ_confirm = 0.80, θ_auto = 0.85)."
        ),
        "tech": "Python/FastAPI; Pydantic v2 decision schemas (roadmap §6.1.1 `decision` payload).",
        "interfaces": "S8, S9, S10, S7, S12, S13.",
        "dependencies": "`canonical-schema`, S8/S9/S10.",
        "scaling": "stateless; CPU-bound orchestration (GPU work delegated to S10/S6).",
        "built_in": "WS-AI (W2) → Phase 6 (verification engine).",
        "invariants": (
            "evidence IDs retained end-to-end on every high-risk output; an apparently obvious "
            "solution still passes its risk tier's verification gates; gate outcomes recorded "
            "on the decision node (`rules_evaluated[]`)."
        ),
    },
    "prescription-service": {
        "module": "S12",
        "purpose": "controlled output.",
        "responsibilities": (
            "locked prescription objects — created only from approved decisions; records full "
            "version tuple; print job management (idempotent `print_id`, no duplicates on "
            "printer failure); QR generation (prescription_id + verification URL); public "
            "verification endpoint (QR scan → status, content, versions, scientist, expiry)."
        ),
        "tech": "Python/FastAPI; `qrcode`; ESC/POS print job format; MinIO (printed artifact archive).",
        "interfaces": "S11/S13 (input), print hardware (edge), MinIO, public verification API.",
        "dependencies": "`canonical-schema`, MinIO, printer (edge).",
        "scaling": "stateless; print queue on edge with retry + idempotency.",
        "built_in": "Phase 1 (print MVP in kiosk MVP) → full lock/verify in WS-AI (W2).",
        "invariants": (
            "zero unapproved prescriptions (hard); printer failure never duplicates "
            "(idempotent `print_id`); blocked interventions cannot reach printable state."
        ),
    },
    "review-service": {
        "module": "S13",
        "purpose": "the scientist gate.",
        "responsibilities": (
            "scientist review queue: approve/correct/escalate; automatic full context snapshot "
            "(case, language, input, crop, problem, location, weather, soil, previous "
            "management, knowledge, rules, AI, scientist, output, audit); decision-delta "
            "creation; correction classification trigger; review SLA tracking (L2 ≤ 24 h; "
            "trial: same day)."
        ),
        "tech": (
            "Python/FastAPI; snapshot builder (read-only aggregation over case graph); "
            "Pydantic v2 delta schemas."
        ),
        "interfaces": "S7, S14, S16, S21 (scientist-portal), S2 (review notifications).",
        "dependencies": "`canonical-schema`, S7.",
        "scaling": "stateless; queue is Postgres-backed.",
        "built_in": "WS-PORTAL (W2, basic approve/correct/escalate) → Phase 8 (multimodal feedback, full snapshot).",
        "invariants": (
            "scientist changes **only the wrong fields**; original AI decision is never "
            "overwritten; every correction carries an evidence status (EVIDENCE_BACKED / "
            "LOCALLY_VALIDATED / EXPERT_PREFERENCE)."
        ),
    },
    "learning-service": {
        "module": "S14",
        "purpose": "governed learning.",
        "responsibilities": (
            "correction classifier (10 delta types, roadmap §4.3.2); candidate generation per "
            "channel (knowledge/rule/training/language/case memory); provenance ledger (all 11 "
            "fields, §4.3.3); learning sandbox orchestration (data quality → regression → "
            "safety → counterexample → holdout); pattern discovery (group validated "
            "corrections by crop/stage/problem/region/season; min support N≥5, consistency "
            "≥80%); candidate review workflow."
        ),
        "tech": "Python; batch + event-driven (workers on Redis); MLflow/DVC integration for training candidates.",
        "interfaces": "S13, S15, S26, S18, S9, S22 (candidate queues).",
        "dependencies": "`canonical-schema`, S13 (deltas), S15 (outcomes), MLflow/DVC.",
        "scaling": "batch workers; pattern discovery is a scheduled job (weekly).",
        "built_in": "Phase 11.",
        "invariants": (
            "no automatic production change — candidate promotion requires explicit approval + "
            "validation report; case memory, knowledge, rules and training data remain "
            "separate; EXPERT_PREFERENCE corrections never auto-promote; all 11 provenance "
            "fields non-null or explicitly N/A."
        ),
    },
    "outcome-service": {
        "module": "S15",
        "purpose": "closed loop — advice delivered ≠ problem solved.",
        "responsibilities": (
            "follow-up scheduling from approved advisory protocols (not fixed intervals); "
            "outcome capture (worked/partial/failed/worsened/unknown) across channels (kiosk "
            "return visit, WhatsApp, extension worker, scientist portal); expected-observation "
            "tracking; failed-solution protocol (stop automatic repetition → reassess → "
            "request new evidence → compare original vs current case → check alternative "
            "hypotheses → escalate if triggers met); failure learning records."
        ),
        "tech": "Python/FastAPI; scheduler (Redis-backed cron); channel adapter webhooks for delivery.",
        "interfaces": "S7, S16, channel adapters (S1/S2/S3), S14.",
        "dependencies": "`canonical-schema`, S7, S16.",
        "scaling": "stateless + scheduler; follow-up volume is small at pilot (dozens/day).",
        "built_in": "Phase 9.",
        "invariants": (
            "failed interventions do NOT automatically trigger another intervention (test: "
            "failed case produces reassessment + evidence request, never an auto-re-prescription); "
            "\"cannot determine\" is a first-class outcome (unknown); every applicable "
            "intervention has a follow-up."
        ),
    },
    "escalation-service": {
        "module": "S16",
        "purpose": "humans with complete handoff; the farmer never experiences a dead end.",
        "responsibilities": (
            "escalation engine L0–L4 (roadmap §4.4) with evidence- and policy-driven triggers "
            "(repeated contradictory information; image cannot distinguish alternatives; "
            "treatment failed; severity increasing; suspected regulatory issue; novel symptom; "
            "possible harmful recommendation; scientist disagreement; missing critical "
            "information); assignment; status workflow OPEN → ASSIGNED → INVESTIGATING → "
            "RESOLVED → LEARNING_CAPTURED; compact human-handoff packet (summary, media, "
            "interpretation, contradictions, hypotheses, evidence, previous treatments, "
            "weather, AI recommendation, reason); farmer-facing transparency (case ID, "
            "status, next steps); SLA tracking and alerts."
        ),
        "tech": "Python/FastAPI; packet builder (read-only aggregation); MQTT `alerts/safety` for L4 (QoS 2).",
        "interfaces": "S7, S13, channel adapters, S22, observability (alerts).",
        "dependencies": "`canonical-schema`, S7, EMQX.",
        "scaling": "stateless; low volume, high criticality.",
        "built_in": "Phase 10.",
        "invariants": (
            "SLAs — L2 ≤ 24 h (trial: same day), L3 ≤ 48 h, L4 immediate + incident process; "
            "every escalation has an ID + status; farmer receives next-steps message on every "
            "escalation."
        ),
    },
    "weather-service": {
        "module": "S17",
        "purpose": "weather context for rules.",
        "responsibilities": (
            "IMD ingestion (central worker, 15–60 min poll: cityforecast/cityforecastloc, "
            "current weather, district/subdivision warnings, rainfall, AWS/ARG, Agromet "
            "Advisory); timestamp + location validation; unit normalization; "
            "`weather_snapshots` table; staleness marking (STALE after 6 h forecast / 2 h "
            "nowcast windows); spray-window evaluation input for S9; edge cache distribution "
            "via sync manifests."
        ),
        "tech": "Python worker; HTTPS (IP-whitelisted, attribution); Postgres; manifest publisher.",
        "interfaces": "S9, S19 (down), S11 (context), S22 (staleness alerts).",
        "dependencies": "IMD API (IP whitelist), `weather_snapshots` table.",
        "scaling": "single idempotent worker; edge keeps last-known snapshot and marks STALE — never silently infers.",
        "built_in": "WS-RULES (W1–W2, needed for weather-window rules).",
        "invariants": "stale weather → spray-window rule returns UNKNOWN (never silently infers); attribution displayed per IMD terms.",
    },
    "knowledge-service": {
        "module": "S18",
        "purpose": "governed knowledge.",
        "responsibilities": (
            "KB lifecycle: ingestion (PDFs/manuals → structured records + passages via "
            "pypdf/unstructured/marker), normalization, expert review workflow, versioning "
            "(KB N+1 with effective dates + supersession links), test cases per entry, edge "
            "bundle publishing (signed), evidence ledger management, re-index/re-embed "
            "worker, retirement/monitoring (age, unanswered questions, retrieval recall)."
        ),
        "tech": "Python; ingestion workers; MinIO (bundles); pgvector re-index; minisign signatures.",
        "interfaces": "S22 (review UI), S8 (index), S19 (bundles), S14 (candidates), evidence ledger.",
        "dependencies": "MinIO, pgvector, `kb_entries`/`kb_passages` tables.",
        "scaling": "batch workers; KB size at pilot ~10⁴–10⁵ passages.",
        "built_in": "WS-KB (W1–W2: KB v1 for Kurnool crops); versioning/bundles in Phase 11/14.",
        "invariants": (
            "source authority hierarchy (roadmap §4.6.1) enforced at ingestion; every KB entry "
            "ships with test questions; KB entries carry effective dates and supersession "
            "links; retired entries archived, not deleted."
        ),
    },
    "mlops-service": {
        "module": "S26",
        "purpose": "the release pipeline (roadmap §4.5).",
        "responsibilities": (
            "MLflow 3 registry (models, experiments) + DVC 3 dataset versioning; evaluation "
            "runners (RAGAS, DeepEval, promptfoo, lm-evaluation-harness) as CI jobs and "
            "scheduled production sampling; shadow-mode orchestration (candidate model on "
            "live cases, hidden output, comparison vs production + scientist decisions; exit: "
            "no safety regression, correction rate not worse, groundedness ≥ baseline); "
            "canary orchestration (device/case subsets); signed bundle build "
            "(model/KB/rules/prompt/speech); rollback (previous version retained ≥ 12 months, "
            "one-command restore, RTO ≤ 15 min/device); drift + correction-rate monitoring."
        ),
        "tech": "Python; MLflow 3; DVC 3; GPU node (on-demand) for fine-tuning (Unsloth/axolotl + PEFT/LoRA).",
        "interfaces": "MLflow/DVC stores (MinIO + Postgres), CI/CD, S22, S10 (shadow), version_registry.",
        "dependencies": "MLflow, DVC, MinIO, GPU node.",
        "scaling": "batch/async; GPU node is on-demand (owned or rented).",
        "built_in": "Phase 14 (foundation W3, hardening W5).",
        "invariants": (
            "no candidate can publish without validation + approval; previous production "
            "version restorable (drill, RTO ≤ 15 min); lockfiles are law; model artifacts "
            "content-addressed (SHA-256) + signed."
        ),
    },
    "sync-agent": {
        "module": "S19",
        "purpose": "encrypted, idempotent, resumable synchronization (edge + central peer).",
        "responsibilities": (
            "up — append-only events (inputs, decisions, corrections, outcomes, telemetry, "
            "print jobs) batched with sequence numbers; down — signed versioned manifests "
            "(knowledge, rules, models, prompt policy, lexicon, weather baseline) → fetch "
            "from MinIO → verify signature → activate. Gap detection and repair; media queue "
            "(chunked, resumable uploads)."
        ),
        "tech": (
            "Python (edge) + FastAPI endpoints (central); MQTT (EMQX) for manifest/command "
            "signaling; HTTPS for bulk transfer; minisign/cosign signature verification; "
            "LUKS-encrypted local queue."
        ),
        "interfaces": "EMQX topics (roadmap §7.5), core-api `/v1/sync/*`, MinIO, S20 (activation hooks).",
        "dependencies": "EMQX, MinIO, S20.",
        "scaling": (
            "per-device instance with backpressure; central peer is stateless workers. "
            "Idempotency by `event_id` makes retries safe."
        ),
        "built_in": "core sync in WS-OFFLINE (W3); media sync in Phase 12.",
        "invariants": (
            "idempotent by event ID (retries safe); append-only (conflicts structurally "
            "impossible for case data); media dedup by content hash; unsigned/invalid bundles "
            "rejected + alert."
        ),
    },
    "device-agent": {
        "module": "S20",
        "purpose": "device health and lifecycle (edge daemon).",
        "responsibilities": (
            "CPU/GPU/memory/disk/temperature, printer status (paper, errors), network status "
            "(Ethernet/Wi-Fi/4G), UPS state, graceful shutdown on power loss, watchdog for "
            "kiosk-ui and core-api, signed update verification and staged activation, "
            "telemetry batching."
        ),
        "tech": "Python daemon (systemd), `nvidia-smi`/`tegrastats` for GPU, MQTT telemetry publisher with local buffering.",
        "interfaces": "MQTT `kiosk/{device_id}/telemetry|ack`, S22 (via central), S19 (update activation).",
        "dependencies": "EMQX, hardware sensors.",
        "scaling": "per-device; no scaling concerns. Fleet view in admin console.",
        "built_in": "basic in Phase 1 (W1); full in WS-OFFLINE (W3).",
        "invariants": (
            "no inbound ports on the device; no secrets on edge except device cert + sync key "
            "(LUKS-protected keystore); power loss → graceful shutdown → clean state."
        ),
    },
    "kiosk-adapter": {
        "module": "S1",
        "purpose": "local bridge for the farmer-facing kiosk application (Flutter app lives in `kiosk/`).",
        "responsibilities": (
            "voice capture (mic array → 16 kHz WAV), touch guided flow (pickers, quick "
            "replies, confirmation gates), text input (Telugu script + Latin keyboard), "
            "camera capture with framing guidance, TTS playback, print UI, session lifecycle "
            "(start/timeout/reset), offline queue visibility. All intelligence calls go to "
            "the local core-api over localhost."
        ),
        "tech": (
            "Flutter 3.x (Linux target), kiosk mode (auto-start, no desktop escape); plugins: "
            "`camera`, `record`/`audio`, `esc_pos_printer`, `usb_serial`, `local_auth` "
            "(operator PIN). This service is the local HTTP bridge the Flutter app talks to."
        ),
        "interfaces": (
            "core-api (localhost HTTP), thermal printer (USB/serial ESC/POS), device-agent "
            "(health queries), hardware sensors (temperature, UPS)."
        ),
        "dependencies": "S4, S5 (TTS playback), S12 (print), S20.",
        "scaling": (
            "one instance per device; no horizontal scaling — reliability engineering "
            "instead (watchdog auto-restart, session resume, print idempotency)."
        ),
        "built_in": "Phase 1 (MVP: touch+text+print, basic voice) → extended in Phases 2, 4, 5 (camera, cross-correction UX, media sets).",
        "invariants": (
            "every touch action is a typed `Input` node with `modality=touch`, confidence 1.0; "
            "no dead ends — every screen offers \"talk to an expert\", \"print what I have\", "
            "\"start over\"; do-not-repeat memory enforced in UI."
        ),
    },
    "whatsapp-adapter": {
        "module": "S2",
        "purpose": "WhatsApp Business Cloud API adapter.",
        "responsibilities": (
            "webhook verification + inbound (text/voice note/photo/multiple photos) → "
            "`case_id` mapping (phone → farmer_ref → active case); media download to MinIO; "
            "outbound rendering (text cards, quick replies, list messages, media); template "
            "management (India approval ~2–4 weeks; utility templates for follow-ups outside "
            "the 24-h window); per-message billing tracking (per-message since Jul 2025; "
            "free service tier from Oct 2026); queue + retry with backoff."
        ),
        "tech": "Python/FastAPI; Meta Graph SDK; webhook signature verification; Redis outbound queue.",
        "interfaces": "Meta Cloud API, case-service (via S4), MinIO, speech-service (voice notes), image-service (photos).",
        "dependencies": "S4, S5, S6, S23, MinIO, Redis.",
        "scaling": "stateless, 2 replicas; webhook is at-least-once → idempotent handlers.",
        "built_in": "Phase 2.",
        "invariants": (
            "no business logic in the adapter; billing category tracked per message; case "
            "continuity (kiosk → WhatsApp → kiosk)."
        ),
    },
    "web-adapter": {
        "module": "S3",
        "purpose": "farmer-facing web/mobile PWA backend.",
        "responsibilities": (
            "chat (text/voice optional), photo upload, case lookup by QR/short code, outcome "
            "reporting, follow-up responses. Pseudonymous (case-scoped tokens; no account "
            "required)."
        ),
        "tech": "React 18 + TypeScript PWA (Vite, Tailwind) + FastAPI backend.",
        "interfaces": "case-service (via S4), MinIO (uploads), Keycloak (optional login for returning farmers).",
        "dependencies": "S4, S23, MinIO.",
        "scaling": "stateless; static assets on CDN.",
        "built_in": "Phase 2.",
        "invariants": "same canonical case schema as kiosk/WhatsApp (Phase 2 exit: automated schema-parity test).",
    },
    "analytics": {
        "module": "S24",
        "purpose": "dashboards on the system of record.",
        "responsibilities": (
            "Metabase dashboards on the central Postgres: service operations (queries/day, "
            "response time, print success, escalations); crop intelligence (crop/stage "
            "distribution); pest surveillance (incidence by geography/time — review signal "
            "only, never autonomous outbreak declaration); AI quality (correction rate/"
            "types); safety (blocked interventions, regulatory conflicts); knowledge "
            "(unanswered questions, stale records); language (ASR confidence, corrected "
            "entities); learning (accepted corrections, candidate rules, model versions); "
            "device (uptime, errors, temperature, sync backlog)."
        ),
        "tech": "Metabase (OSS) on PostgreSQL; scheduled aggregate tables (nightly) to keep dashboards fast.",
        "interfaces": "Postgres (read replica).",
        "dependencies": "PostgreSQL, Metabase.",
        "scaling": "read replica; aggregate tables.",
        "built_in": "W3 (operations + safety) → W4 (trial dashboards) → W5 (surveillance + learning).",
        "invariants": (
            "surveillance is aggregate only, mandal-level minimum granularity, no individual "
            "farmer identification; access: scientist/admin/auditor only, logged."
        ),
    },
}

PYPROJECT = """\
[project]
name = "{name}"
version = "0.1.0"
description = "AI Kiosk {name} — {purpose} (docs/02 {module})"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.116",
    "uvicorn[standard]>=0.34",
    "pydantic>=2.9",
    "httpx>=0.28",
    "canonical-schema",
]

[project.optional-dependencies]
dev = ["pytest>=8.3", "httpx>=0.28"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/{pkg}"]

[tool.uv.sources]
canonical-schema = {{ workspace = true }}
"""

INIT = '''\
"""{name} — {purpose}"""

from {pkg}._version import __version__

__all__ = ["__version__"]
'''

VERSION = '__version__ = "0.1.0"\n'

MAIN = '''\
"""FastAPI application for {name} ({module}).

Skeleton service.
Built in: {built_in}
Full module context: README.md (from docs/02-modules.md §{module}).
Conventions: RFC 7807 problem+json errors, `/v1` URL prefix, `/health` +
`/ready` on every service.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from canonical_schema import HealthResponse, ReadyResponse
from fastapi import FastAPI, Request

from {pkg}._version import __version__

SERVICE_NAME = "{name}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.started_at = time.monotonic()
    # TODO: wire real dependencies (DB, Redis, MinIO, ...) as the service is built out.
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=f"AI Kiosk — {{SERVICE_NAME}}", version=__version__, lifespan=lifespan)

    @app.get("/health", response_model=HealthResponse)
    def health(request: Request) -> HealthResponse:
        """Liveness."""
        return HealthResponse(
            status="ok",
            service=SERVICE_NAME,
            version=__version__,
            uptime_s=round(time.monotonic() - request.app.state.started_at, 3),
        )

    @app.get("/ready", response_model=ReadyResponse)
    def ready(request: Request) -> ReadyResponse:
        """Readiness — TODO: add real dependency checks as the service is built out."""
        return ReadyResponse(ready=True, dependencies={{}})

    return app


app = create_app()
'''

TEST = '''\
"""{name} skeleton smoke tests."""

from fastapi.testclient import TestClient
from {pkg}.main import create_app


def test_health():
    with TestClient(create_app()) as c:
        r = c.get("/health")
        assert r.status_code == 200
        assert r.json()["service"] == "{name}"


def test_ready():
    with TestClient(create_app()) as c:
        r = c.get("/ready")
        assert r.status_code == 200
        assert r.json()["ready"] is True
'''

README = """\
# {name} ({module})

> **Skeleton service** — built in {built_in}. Full spec: `docs/02-modules.md` §{module}
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

{purpose}

## Responsibilities

{responsibilities}

## Tech

{tech}

## Interfaces

{interfaces}

## Dependencies

{dependencies}

## Scaling

{scaling}

## Built in

{built_in}

## Key invariants

{invariants}

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/{name}/
├── pyproject.toml
├── README.md
├── src/{pkg}/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_{pkg}.py
```
"""


def _fill(text: str, width: int) -> str:
    """Wrap prose for docstring lines (keeps generated sources ≤ line-length 100)."""
    return textwrap.fill(text, width=width, break_long_words=False, break_on_hyphens=False)


def main() -> None:
    for name, m in SERVICES.items():
        pkg = name.replace("-", "_")
        base = SERVICES_DIR / name
        src = base / "src" / pkg
        tests = base / "tests"
        src.mkdir(parents=True, exist_ok=True)
        tests.mkdir(parents=True, exist_ok=True)

        (base / "pyproject.toml").write_text(
            PYPROJECT.format(name=name, pkg=pkg, purpose=m["purpose"], module=m["module"]),
            encoding="utf-8",
        )
        (base / "README.md").write_text(
            README.format(name=name, pkg=pkg, **m), encoding="utf-8"
        )
        (src / "__init__.py").write_text(
            INIT.format(name=name, pkg=pkg, purpose=_fill(m["purpose"], 80)), encoding="utf-8"
        )
        (src / "_version.py").write_text(VERSION, encoding="utf-8")
        (src / "main.py").write_text(
            MAIN.format(
                name=name, pkg=pkg, module=m["module"], built_in=_fill(m["built_in"], 88)
            ),
            encoding="utf-8",
        )
        (tests / f"test_{pkg}.py").write_text(TEST.format(name=name, pkg=pkg), encoding="utf-8")
        print(f"generated services/{name}/")
    print(f"done: {len(SERVICES)} skeletons")


if __name__ == "__main__":
    main()
