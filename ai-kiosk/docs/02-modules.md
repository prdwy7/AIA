# 02 — Modules (S1–S26): Context for Every Module

> Roadmap §3.3 + §8. Each module entry: purpose, responsibilities, tech, interfaces,
> dependencies, scaling, build phase, key invariants. Services are deliberately small
> and single-purpose; **S7 (case-service) is the only service that owns case state.**

## S1 — channel-adapter-kiosk (Edge)

- **Purpose:** the farmer-facing kiosk application.
- **Responsibilities:** voice capture (mic array → 16 kHz WAV), touch guided flow (pickers, quick replies, confirmation gates), text input (Telugu script + Latin keyboard), camera capture with framing guidance, TTS playback, print UI, session lifecycle (start/timeout/reset), offline queue visibility.
- **Tech:** Flutter 3.x (Linux target), kiosk mode (auto-start, no desktop escape); plugins: `camera`, `record`/`audio`, `esc_pos_printer`, `usb_serial`, `local_auth` (operator PIN). All intelligence calls go to the local core-api over localhost.
- **Interfaces:** core-api (localhost HTTP), thermal printer (USB/serial ESC/POS), device-agent (health queries), hardware sensors (temperature, UPS).
- **Dependencies:** S4, S5 (TTS playback), S12 (print), S20.
- **Scaling:** one instance per device; no horizontal scaling — reliability engineering instead (watchdog auto-restart, session resume, print idempotency).
- **Built in:** Phase 1 (MVP: touch+text+print, basic voice) → extended in Phases 2, 4, 5 (camera, cross-correction UX, media sets).
- **Invariants:** every touch action is a typed `Input` node with `modality=touch`, confidence 1.0; no dead ends — every screen offers "talk to an expert", "print what I have", "start over"; do-not-repeat memory enforced in UI.
- **Repo:** `kiosk/` (Flutter app) + `services/kiosk-adapter/` (local bridge skeleton).

## S2 — channel-adapter-whatsapp (Central)

- **Purpose:** WhatsApp Business Cloud API adapter.
- **Responsibilities:** webhook verification + inbound (text/voice note/photo/multiple photos) → `case_id` mapping (phone → farmer_ref → active case); media download to MinIO; outbound rendering (text cards, quick replies, list messages, media); template management (India approval ~2–4 weeks; utility templates for follow-ups outside the 24-h window); per-message billing tracking (per-message since Jul 2025; free service tier from Oct 2026); queue + retry with backoff.
- **Tech:** Python/FastAPI; Meta Graph SDK; webhook signature verification; Redis outbound queue.
- **Interfaces:** Meta Cloud API, case-service (via S4), MinIO, speech-service (voice notes), image-service (photos).
- **Dependencies:** S4, S5, S6, S23, MinIO, Redis.
- **Scaling:** stateless, 2 replicas; webhook is at-least-once → idempotent handlers.
- **Built in:** Phase 2.
- **Invariants:** no business logic in the adapter; billing category tracked per message; case continuity (kiosk → WhatsApp → kiosk).

## S3 — channel-adapter-web (Central)

- **Purpose:** farmer-facing web/mobile PWA.
- **Responsibilities:** chat (text/voice optional), photo upload, case lookup by QR/short code, outcome reporting, follow-up responses. Pseudonymous (case-scoped tokens; no account required).
- **Tech:** React 18 + TypeScript PWA (Vite, Tailwind) + FastAPI backend.
- **Interfaces:** case-service (via S4), MinIO (uploads), Keycloak (optional login for returning farmers).
- **Dependencies:** S4, S23, MinIO.
- **Scaling:** stateless; static assets on CDN.
- **Built in:** Phase 2.
- **Invariants:** same canonical case schema as kiosk/WhatsApp (Phase 2 exit: automated schema-parity test).

## S4 — input-orchestrator (Core)

- **Purpose:** single entry point for all inputs across all modalities and channels.
- **Responsibilities:** routes audio → speech-service, images → image-service, text → text normalizer, touch events → case-service directly. Owns session state. Enforces input quality gates. Creates immutable `Input` nodes and triggers interpretation. Enforces do-not-repeat memory at input time (e.g., already-received image views).
- **Tech:** Python/FastAPI; session state in Redis (central) / local Redis (edge); Pydantic v2 schemas.
- **Interfaces:** S5, S6, S7, channel adapters (inbound), lexicon (shared library).
- **Dependencies:** S5, S6, S7, Redis, `canonical-schema`, `agri-rules` (lexicon).
- **Scaling:** stateless compute; horizontal replicas behind the API gateway; session state externalized.
- **Built in:** Phase 1.
- **Invariants:** every input becomes an immutable `Input` node with modality metadata; mixed input within one case is always allowed; modality failure never dead-ends the case.

## S5 — speech-service (Core)

- **Purpose:** full voice pipeline (roadmap §9.1).
- **Responsibilities:** VAD (silero-vad), ffmpeg normalization (16 kHz mono WAV), ASR engine selection and fallback chain (**Vaani-Whisper primary → SraVaani fast → BHASHINI online cross-check**), agricultural vocabulary normalization, entity candidate extraction, TTS synthesis (Piper → BHASHINI → text-only fallback). Records engine/model/confidence on every `Input` node.
- **Tech:** Python; faster-whisper (int8) for Whisper family; ONNX Runtime for SraVaani; Piper (piper1-gpl) for TTS; ffmpeg; silero-vad. GPU-aware job queue (ASR yields to LLM inference when VRAM is contended → SraVaani on CPU/ONNX path).
- **Interfaces:** S4, MinIO (audio objects), lexicon table, BHASHINI API (online), S7 (via S4).
- **Dependencies:** models ASR-0.1.0 / ASR-0.1.1 / TTS-0.1.0, ffmpeg, silero-vad.
- **Scaling:** concurrency-limited GPU queue; per-engine latency SLOs (Vaani-Whisper < 3 s, SraVaani < 1.5 s p95); horizontal replicas share the GPU pool via queue.
- **Built in:** basic chain in Phase 1 (W1 kiosk MVP); full fallback + cross-check in Phase 4; scientist voice feedback in Phase 8.
- **Invariants:** engine used is recorded on the `Input` node (`asr.engine`); confidence < 0.60 AND online → BHASHINI cross-check; disagreement on a critical entity → confirmation gate showing both candidates; TTS text is generated from the **locked output object**, never raw LLM text.
- **Repo:** `services/speech-service/` (rich implementation: `engines/`, `chain.py`).

## S6 — image-service (Core)

- **Purpose:** image evidence pipeline (roadmap §9.4).
- **Responsibilities:** quality checks (blur/brightness/size/crop detection) with concrete retry instructions; structured visual observations via Gemma 3 vision (states OBSERVED/POSSIBLE/UNCERTAIN/CONTRADICTORY/NOT_VISIBLE); fine-tuned ViT disease/pest classifier; media-set management (views: whole plant, leaf, stem, fruit, pest close-up, field context); missing-view requests; face-blurring for stored media.
- **Tech:** Python; OpenCV/Pillow for deterministic quality checks; Ollama (Gemma 3 12B vision) for observations; PyTorch/ONNX ViT classifier; MinIO for media.
- **Interfaces:** S4, MinIO, S7 (observation nodes), lexicon (crop/pest taxonomy).
- **Dependencies:** models VISION-0.1.0 / CLASS-0.1.0, Ollama, MinIO.
- **Scaling:** GPU job queue (batched); classifier runs on CPU/ONNX for low latency; observation extraction is the GPU-bound step.
- **Built in:** Phase 5.
- **Invariants:** a weak visual signal is never converted into a high-confidence diagnosis merely because an image exists; faces blurred by default in stored copies; already-received views are never re-requested.
- **Repo:** `services/image-service/` (rich implementation: `quality.py`, `observations.py`, `classifier.py`, `media_set.py`).

## S7 — case-service (Core) — the canonical case service

- **Purpose:** owns the Case-to-Solution Tree.
- **Responsibilities:** append-only `case_node` writes; lifecycle state machine (roadmap §4.2) with transition guards; contradiction detection (across modalities); do-not-repeat memory; case continuity (short code, QR payload, cross-channel mapping); tree retrieval.
- **Tech:** Python/FastAPI; PostgreSQL (system of record); ULID IDs; DB-level append-only enforcement (triggers reject UPDATE/DELETE except status transitions).
- **Interfaces:** all core services; channel adapters (via S4); S8 (case embeddings); S15/S16.
- **Dependencies:** `canonical-schema`, PostgreSQL, MinIO (media refs).
- **Scaling:** stateless API; Postgres partitioned by `case_id` range; read replicas at district scale. Hot path is small (node append + state transition).
- **Built in:** Phase 1 (schema + skeleton) → Phase 3 (full tree semantics).
- **Invariants:** the ONLY service that mutates case state (append-only; status transitions only); original farmer input and original system interpretation are immutable; every question has a recorded decision purpose; a case never silently changes crop/stage/problem — contradictions force a clarification branch; max 3 questions per branch by default.

## S8 — retrieval-service (Core)

- **Purpose:** hybrid evidence retrieval.
- **Responsibilities:** structured filters first (crop/stage/geography/validity), then hybrid search — SQL/exact + keyword (Postgres FTS/BM25) + vector (pgvector, BGE-M3 dense + sparse) — then reranking (BGE-Reranker-v2-M3) and evidence ranking by authority + freshness + relevance. Also serves similar-case search (case embeddings) for S7/Phase 7.
- **Tech:** Python; PostgreSQL 17 + pgvector 0.8.2 (HNSW); BGE-M3 (edge + central); BGE-Reranker-v2-M3 (GPU).
- **Interfaces:** S11, S7, S18 (index maintenance), similar-case index.
- **Dependencies:** models EMB-0.1.0 / RERANK-0.1.0, pgvector.
- **Scaling:** single Postgres with HNSW is sufficient for pilot (KB ~10⁴–10⁵ passages); read replica + index tuning at district scale. Embedding generation is batch (KB re-index worker), not on the hot path.
- **Built in:** WS-AI (W2), consumed by Phases 3, 6, 7.
- **Invariants:** every returned evidence item carries method + score + authority level; high-impact recommendations are traceable to evidence-ledger entries.
- **Repo:** `services/retrieval-service/` (rich implementation: `hybrid.py`, `rank.py`, `embed.py`).

## S9 — rules-service (Core)

- **Purpose:** deterministic policy package.
- **Responsibilities:** regulatory checks (banned/refused/restricted → BLOCK/REVIEW/CONDITION), crop/target, formulation, dose range, application method, weather window (GREEN/CAUTION/BLOCKED/UNKNOWN), PHI/PPE/environment, confidence gates, clarification policy. Pure functions over typed context; every rule has `test_cases[]`; counterexample search for rule candidates.
- **Tech:** Python policy package (`agri-rules`) — no external rule engine (Drools/OPA evaluated and rejected: Java/external-runtime overhead, weaker test ergonomics for agronomic logic); versioned as a signed artifact (RULE version in the version tuple).
- **Interfaces:** S11, S12, S17 (context input), S14 (counterexample search).
- **Dependencies:** `agri-rules` package, `regulatory_products` table, weather snapshots.
- **Scaling:** in-process library (no network hop); zero scaling concerns. Test suite runs in CI on every build.
- **Built in:** WS-RULES (W1–W2); counterexample search in Phase 11.
- **Invariants:** deterministic — the LLM cannot override; 100% of blocking rules covered by tests; property test: no blocked intervention can reach printable state; gaps surface as REVIEW, never silent pass.
- **Repo:** `packages/agri-rules/` (rich implementation: `engine.py`, `inventory.py`, `regulatory.py`).

## S10 — llm-service (Core)

- **Purpose:** local LLM inference management.
- **Responsibilities:** Ollama runtime; structured output generation (JSON schema enforced before pipeline entry); prompt-policy versioning (PROMPT_POLICY_VERSION); shadow-model runner (candidate model answers live cases hidden, Phase 14); token/latency/VRAM telemetry; model hot-swap.
- **Tech:** Python; Ollama 0.34.x (Gemma 3 12B Q5_K_M primary, Llama 3.1 8B light); llama.cpp fallback; Pydantic v2 output validation; OpenTelemetry spans per call.
- **Interfaces:** S11, S6 (vision observations), S26 (shadow orchestration), S20 (GPU state).
- **Dependencies:** models MODEL-0.1.0 / MODEL-0.1.1, Ollama.
- **Scaling:** GPU queue with priority (prescription drafting > observations > shadow); OOM handling (evict to SraVaani/CPU path, queue); one GPU per kiosk at pilot.
- **Built in:** WS-AI (W2); shadow runner in Phase 14.
- **Invariants:** LLM output must validate against the Pydantic schema before entering the rules/prescription pipeline; farmer text is data, never instructions; regulatory data is never injected into the LLM context as instructions.

## S11 — advisory-service (Core)

- **Purpose:** composes the grounded answer.
- **Responsibilities:** retrieval evidence + rules evaluation + LLM draft → advisory/prescription draft with evidence-ID retention end-to-end; risk-tier assignment (information/diagnosis/advisory/prescription); verification-gate orchestration (Phase 6); confirmation-gate decisions (θ_confirm = 0.80, θ_auto = 0.85).
- **Tech:** Python/FastAPI; Pydantic v2 decision schemas (roadmap §6.1.1 `decision` payload).
- **Interfaces:** S8, S9, S10, S7, S12, S13.
- **Dependencies:** `canonical-schema`, S8/S9/S10.
- **Scaling:** stateless; CPU-bound orchestration (GPU work delegated to S10/S6).
- **Built in:** WS-AI (W2) → Phase 6 (verification engine).
- **Invariants:** evidence IDs retained end-to-end on every high-risk output; an apparently obvious solution still passes its risk tier's verification gates; gate outcomes recorded on the decision node (`rules_evaluated[]`).

## S12 — prescription-service (Core)

- **Purpose:** controlled output.
- **Responsibilities:** locked prescription objects — created only from approved decisions; records full version tuple; print job management (idempotent `print_id`, no duplicates on printer failure); QR generation (prescription_id + verification URL); public verification endpoint (QR scan → status, content, versions, scientist, expiry).
- **Tech:** Python/FastAPI; `qrcode`; ESC/POS print job format; MinIO (printed artifact archive).
- **Interfaces:** S11/S13 (input), print hardware (edge), MinIO, public verification API.
- **Dependencies:** `canonical-schema`, MinIO, printer (edge).
- **Scaling:** stateless; print queue on edge with retry + idempotency.
- **Built in:** Phase 1 (print MVP in kiosk MVP) → full lock/verify in WS-AI (W2).
- **Invariants:** zero unapproved prescriptions (hard); printer failure never duplicates (idempotent `print_id`); blocked interventions cannot reach printable state.

## S13 — review-service (Core)

- **Purpose:** the scientist gate.
- **Responsibilities:** scientist review queue: approve/correct/escalate; automatic full context snapshot (case, language, input, crop, problem, location, weather, soil, previous management, knowledge, rules, AI, scientist, output, audit); decision-delta creation; correction classification trigger; review SLA tracking (L2 ≤ 24 h; trial: same day).
- **Tech:** Python/FastAPI; snapshot builder (read-only aggregation over case graph); Pydantic v2 delta schemas.
- **Interfaces:** S7, S14, S16, S21 (scientist-portal), S2 (review notifications).
- **Dependencies:** `canonical-schema`, S7.
- **Scaling:** stateless; queue is Postgres-backed.
- **Built in:** WS-PORTAL (W2, basic approve/correct/escalate) → Phase 8 (multimodal feedback, full snapshot).
- **Invariants:** scientist changes **only the wrong fields**; original AI decision is never overwritten; every correction carries an evidence status (EVIDENCE_BACKED / LOCALLY_VALIDATED / EXPERT_PREFERENCE).

## S14 — learning-service (Core)

- **Purpose:** governed learning.
- **Responsibilities:** correction classifier (10 delta types, roadmap §4.3.2); candidate generation per channel (knowledge/rule/training/language/case memory); provenance ledger (all 11 fields, §4.3.3); learning sandbox orchestration (data quality → regression → safety → counterexample → holdout); pattern discovery (group validated corrections by crop/stage/problem/region/season; min support N≥5, consistency ≥80%); candidate review workflow.
- **Tech:** Python; batch + event-driven (workers on Redis); MLflow/DVC integration for training candidates.
- **Interfaces:** S13, S15, S26, S18, S9, S22 (candidate queues).
- **Dependencies:** `canonical-schema`, S13 (deltas), S15 (outcomes), MLflow/DVC.
- **Scaling:** batch workers; pattern discovery is a scheduled job (weekly).
- **Built in:** Phase 11.
- **Invariants:** no automatic production change — candidate promotion requires explicit approval + validation report; case memory, knowledge, rules and training data remain separate; EXPERT_PREFERENCE corrections never auto-promote; all 11 provenance fields non-null or explicitly N/A.

## S15 — outcome-service (Core)

- **Purpose:** closed loop — advice delivered ≠ problem solved.
- **Responsibilities:** follow-up scheduling from approved advisory protocols (not fixed intervals); outcome capture (worked/partial/failed/worsened/unknown) across channels (kiosk return visit, WhatsApp, extension worker, scientist portal); expected-observation tracking; failed-solution protocol (stop automatic repetition → reassess → request new evidence → compare original vs current case → check alternative hypotheses → escalate if triggers met); failure learning records.
- **Tech:** Python/FastAPI; scheduler (Redis-backed cron); channel adapter webhooks for delivery.
- **Interfaces:** S7, S16, channel adapters (S1/S2/S3), S14.
- **Dependencies:** `canonical-schema`, S7, S16.
- **Scaling:** stateless + scheduler; follow-up volume is small at pilot (dozens/day).
- **Built in:** Phase 9.
- **Invariants:** failed interventions do NOT automatically trigger another intervention (test: failed case produces reassessment + evidence request, never an auto-re-prescription); "cannot determine" is a first-class outcome (unknown); every applicable intervention has a follow-up.

## S16 — escalation-service (Core)

- **Purpose:** humans with complete handoff; the farmer never experiences a dead end.
- **Responsibilities:** escalation engine L0–L4 (roadmap §4.4) with evidence- and policy-driven triggers (repeated contradictory information; image cannot distinguish alternatives; treatment failed; severity increasing; suspected regulatory issue; novel symptom; possible harmful recommendation; scientist disagreement; missing critical information); assignment; status workflow `OPEN → ASSIGNED → INVESTIGATING → RESOLVED → LEARNING_CAPTURED`; compact human-handoff packet (summary, media, interpretation, contradictions, hypotheses, evidence, previous treatments, weather, AI recommendation, reason); farmer-facing transparency (case ID, status, next steps); SLA tracking and alerts.
- **Tech:** Python/FastAPI; packet builder (read-only aggregation); MQTT `alerts/safety` for L4 (QoS 2).
- **Interfaces:** S7, S13, channel adapters, S22, observability (alerts).
- **Dependencies:** `canonical-schema`, S7, EMQX.
- **Scaling:** stateless; low volume, high criticality.
- **Built in:** Phase 10.
- **Invariants:** SLAs — L2 ≤ 24 h (trial: same day), L3 ≤ 48 h, L4 immediate + incident process; every escalation has an ID + status; farmer receives next-steps message on every escalation.

## S17 — weather-service (Core)

- **Purpose:** weather context for rules.
- **Responsibilities:** IMD ingestion (central worker, 15–60 min poll: cityforecast/cityforecastloc, current weather, district/subdivision warnings, rainfall, AWS/ARG, Agromet Advisory); timestamp + location validation; unit normalization; `weather_snapshots` table; staleness marking (STALE after 6 h forecast / 2 h nowcast windows); spray-window evaluation input for S9; edge cache distribution via sync manifests.
- **Tech:** Python worker; HTTPS (IP-whitelisted, attribution); Postgres; manifest publisher.
- **Interfaces:** S9, S19 (down), S11 (context), S22 (staleness alerts).
- **Dependencies:** IMD API (IP whitelist), `weather_snapshots` table.
- **Scaling:** single idempotent worker; edge keeps last-known snapshot and marks STALE — never silently infers.
- **Built in:** WS-RULES (W1–W2, needed for weather-window rules).
- **Invariants:** stale weather → spray-window rule returns UNKNOWN (never silently infers); attribution displayed per IMD terms.

## S18 — knowledge-service (Core)

- **Purpose:** governed knowledge.
- **Responsibilities:** KB lifecycle: ingestion (PDFs/manuals → structured records + passages via pypdf/unstructured/marker), normalization, expert review workflow, versioning (KB N+1 with effective dates + supersession links), test cases per entry, edge bundle publishing (signed), evidence ledger management, re-index/re-embed worker, retirement/monitoring (age, unanswered questions, retrieval recall).
- **Tech:** Python; ingestion workers; MinIO (bundles); pgvector re-index; minisign signatures.
- **Interfaces:** S22 (review UI), S8 (index), S19 (bundles), S14 (candidates), evidence ledger.
- **Dependencies:** MinIO, pgvector, `kb_entries`/`kb_passages` tables.
- **Scaling:** batch workers; KB size at pilot ~10⁴–10⁵ passages.
- **Built in:** WS-KB (W1–W2: KB v1 for Kurnool crops); versioning/bundles in Phase 11/14.
- **Invariants:** source authority hierarchy (roadmap §4.6.1) enforced at ingestion; every KB entry ships with test questions; KB entries carry effective dates and supersession links; retired entries archived, not deleted.

## S19 — sync-agent (Edge + central peer)

- **Purpose:** encrypted, idempotent, resumable synchronization.
- **Responsibilities:** up — append-only events (inputs, decisions, corrections, outcomes, telemetry, print jobs) batched with sequence numbers; down — signed versioned manifests (knowledge, rules, models, prompt policy, lexicon, weather baseline) → fetch from MinIO → verify signature → activate. Gap detection and repair; media queue (chunked, resumable uploads).
- **Tech:** Python (edge) + FastAPI endpoints (central); MQTT (EMQX) for manifest/command signaling; HTTPS for bulk transfer; minisign/cosign signature verification; LUKS-encrypted local queue.
- **Interfaces:** EMQX topics (roadmap §7.5), core-api `/v1/sync/*`, MinIO, S20 (activation hooks).
- **Dependencies:** EMQX, MinIO, S20.
- **Scaling:** per-device instance with backpressure; central peer is stateless workers. Idempotency by `event_id` makes retries safe.
- **Built in:** core sync in WS-OFFLINE (W3); media sync in Phase 12.
- **Invariants:** idempotent by event ID (retries safe); append-only (conflicts structurally impossible for case data); media dedup by content hash; unsigned/invalid bundles rejected + alert.

## S20 — device-agent (Edge)

- **Purpose:** device health and lifecycle.
- **Responsibilities:** CPU/GPU/memory/disk/temperature, printer status (paper, errors), network status (Ethernet/Wi-Fi/4G), UPS state, graceful shutdown on power loss, watchdog for kiosk-ui and core-api, signed update verification and staged activation, telemetry batching.
- **Tech:** Python daemon (systemd), `nvidia-smi`/`tegrastats` for GPU, MQTT telemetry publisher with local buffering.
- **Interfaces:** MQTT `kiosk/{device_id}/telemetry|ack`, S22 (via central), S19 (update activation).
- **Dependencies:** EMQX, hardware sensors.
- **Scaling:** per-device; no scaling concerns. Fleet view in admin console.
- **Built in:** basic in Phase 1 (W1); full in WS-OFFLINE (W3).
- **Invariants:** no inbound ports on the device; no secrets on edge except device cert + sync key (LUKS-protected keystore); power loss → graceful shutdown → clean state.

## S21 — scientist-portal (Central UI)

- **Purpose:** the scientist's workbench.
- **Responsibilities:** review queue (prescriptions + uncertain cases); minimal-field correction UX (approve/correct/escalate; only wrong fields editable); multimodal feedback (text, voice → ASR → structured correction, image, annotated image); automatic context display (read-only snapshot); candidate approval (knowledge/rule/training/language); escalation queue with SLA; dashboards (AI quality, safety, learning).
- **Tech:** React 18 + TypeScript PWA; Keycloak OIDC; WebSocket/SSE for queue updates.
- **Interfaces:** S13, S14, S16, S7 (tree view), S5 (voice feedback).
- **Dependencies:** S13, S14, S16, S23.
- **Scaling:** stateless; small user base (dozens of scientists at district scale).
- **Built in:** WS-PORTAL (W2) → Phase 8 (multimodal).
- **Invariants:** MFA (TOTP) required; context snapshot is read-only; UAT with ≥ 3 KVK scientists (Phase 8 exit).
- **Repo:** `ui/scientist-portal/`.

## S22 — admin-console (Central UI)

- **Purpose:** platform administration.
- **Responsibilities:** device fleet management (status, health, active version tuple, sync state); release management (shadow→canary→production promotion, rollback); users/roles; audit views; KB/rules review workflows; weather staleness alerts; candidate queues.
- **Tech:** React 18 + TypeScript PWA; Keycloak OIDC (admin/auditor roles).
- **Interfaces:** version_registry, devices, Keycloak, S26, S18, S14.
- **Dependencies:** S23, S26, S18, S14.
- **Scaling:** stateless; small user base.
- **Built in:** basic in Phase 1 (W1); full in W3–W5.
- **Invariants:** admin may not approve agricultural content (role separation); two-person rule for production promotion; fleet shows active version tuple per device.
- **Repo:** `ui/admin-console/`.

## S23 — identity (Keycloak) (Central)

- **Purpose:** OIDC authentication/authorization.
- **Responsibilities:** roles: `farmer` (pseudonymous, no account at kiosk — case-scoped tokens), `operator`, `scientist`, `admin`, `auditor`; device identity: TLS client certificates (mTLS) for kiosk sync; device registry; consent records linkage (DPDP).
- **Tech:** Keycloak 26.x on Postgres; certificate issuance via internal CA (or Keycloak client certs); role mapping from institutional directories.
- **Interfaces:** all central services (bearer tokens), sync (mTLS), S22.
- **Dependencies:** PostgreSQL.
- **Scaling:** 2 replicas + Postgres; standard Keycloak HA.
- **Built in:** Phase 1 (W1).
- **Invariants:** MFA (TOTP) for all privileged roles; farmer never stores a name — pseudonymous `farmer_ref` only; quarterly RBAC access review.
- **Repo:** `infra/keycloak/` (realm config) — no service code.

## S24 — analytics (Central)

- **Purpose:** dashboards on the system of record.
- **Responsibilities:** Metabase dashboards on the central Postgres: service operations (queries/day, response time, print success, escalations); crop intelligence (crop/stage distribution); pest surveillance (incidence by geography/time — review signal only, never autonomous outbreak declaration); AI quality (correction rate/types); safety (blocked interventions, regulatory conflicts); knowledge (unanswered questions, stale records); language (ASR confidence, corrected entities); learning (accepted corrections, candidate rules, model versions); device (uptime, errors, temperature, sync backlog).
- **Tech:** Metabase (OSS) on PostgreSQL; scheduled aggregate tables (nightly) to keep dashboards fast.
- **Interfaces:** Postgres (read replica).
- **Dependencies:** PostgreSQL, Metabase.
- **Scaling:** read replica; aggregate tables.
- **Built in:** W3 (operations + safety) → W4 (trial dashboards) → W5 (surveillance + learning).
- **Invariants:** surveillance is aggregate only, mandal-level minimum granularity, no individual farmer identification; access: scientist/admin/auditor only, logged.

## S25 — observability (Cross-cutting)

- **Purpose:** full reproducibility of any production answer.
- **Responsibilities:** OpenTelemetry SDK in every service: traces (question → ASR → retrieval → rules → LLM → gate → output, with input hashes + version tuple per span), metrics, structured logs. Prometheus + Grafana + Loki on central; edge ships telemetry via MQTT with local buffering. Alerting (safety, staleness, sync backlog, GPU OOM, printer failure).
- **Tech:** OpenTelemetry Python SDK; Prometheus 2.x; Grafana 11.x; Loki 3.x; alertmanager.
- **Interfaces:** all services; MQTT (edge telemetry); S22 (alert views).
- **Dependencies:** Prometheus/Grafana/Loki, EMQX.
- **Scaling:** standard; edge buffering handles connectivity gaps.
- **Built in:** skeleton in Phase 1 (W1); full pipeline in W2.
- **Invariants:** every decision-bearing response includes `version_tuple` and `trace_id`; security logs separated from farmer analytics.
- **Repo:** `infra/observability/` (Prometheus/Grafana/Loki config) — no service code.

## S26 — mlops-service (Central)

- **Purpose:** the release pipeline (roadmap §4.5).
- **Responsibilities:** MLflow 3 registry (models, experiments) + DVC 3 dataset versioning; evaluation runners (RAGAS, DeepEval, promptfoo, lm-evaluation-harness) as CI jobs and scheduled production sampling; shadow-mode orchestration (candidate model on live cases, hidden output, comparison vs production + scientist decisions; exit: no safety regression, correction rate not worse, groundedness ≥ baseline); canary orchestration (device/case subsets); signed bundle build (model/KB/rules/prompt/speech); rollback (previous version retained ≥ 12 months, one-command restore, RTO ≤ 15 min/device); drift + correction-rate monitoring.
- **Tech:** Python; MLflow 3; DVC 3; GPU node (on-demand) for fine-tuning (Unsloth/axolotl + PEFT/LoRA).
- **Interfaces:** MLflow/DVC stores (MinIO + Postgres), CI/CD, S22, S10 (shadow), version_registry.
- **Dependencies:** MLflow, DVC, MinIO, GPU node.
- **Scaling:** batch/async; GPU node is on-demand (owned or rented).
- **Built in:** Phase 14 (foundation W3, hardening W5).
- **Invariants:** no candidate can publish without validation + approval; previous production version restorable (drill, RTO ≤ 15 min); lockfiles are law; model artifacts content-addressed (SHA-256) + signed.

## Build order summary (roadmap §8.5)

| Phase | Services delivered |
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
