# 09 — Roadmap, Team, Hardware, Risks

> Part of the AI Kiosk v2 documentation set. See [00-project-context.md](00-project-context.md), [01-architecture.md](01-architecture.md), [02-modules.md](02-modules.md), [08-operations.md](08-operations.md).
> Source: roadmap §10 (phases), §11 (team), §12 (hardware), §15 (risks), §18.D (open questions).

## 1. Roadmap structure

- **Duration:** 18 months (M1 = Oct 2026 … M18 = Mar 2028), 5 waves, 16 phases (0–15).
- **Phase spine:** the 16 phases are the v2 revised implementation roadmap. The v1 workstreams (knowledge base, rules, kiosk MVP, AI/RAG, scientist portal, offline core) run **in parallel as workstreams (WS-\*)** inside the waves.
- **Phase gates:** a phase is complete only when its exit criteria are met **and verified** (automated test report + stakeholder sign-off recorded in the version registry). No phase starts before its dependencies' exit criteria are met (Gantt overlaps are planned, not speculative).
- **Change control:** after M3 (schema freeze) and during the trial (M10–M13), changes to production artifacts go through the release framework (roadmap §4.5) — the trial runs on frozen versions.

### Waves

| Wave | Months | Phases | Theme |
|---|---|---|---|
| W1 — Foundation | M1–M3 | 0, 1 (+ WS-KB, WS-RULES, WS-KIOSK) | Governance, canonical schema, platform skeleton, kiosk MVP (touch+text+print), KB v1, rules v1 |
| W2 — Intelligence | M3–M8 | 2, 3, 4, 5, 6, 7, 8 (+ WS-AI, WS-VOICE, WS-PORTAL) | Channels, Case-to-Solution Tree, cross-correction, image pipeline, verification, similar cases, scientist multimodal feedback |
| W3 — Closed loop | M7–M10 | 9, 10, 11, 12, 14-foundation (+ WS-OFFLINE) | Outcome/follow-up, escalation, learning sandbox, offline media sync, MLOps foundation |
| W4 — Trial | M10–M13 | 13 | Three-month scientist-supervised trial |
| W5 — Production & scale | M13–M18 | 14-hardening, 15 | MLOps/KnowledgeOps hardening, multi-kiosk, multi-channel scale, ops handover |

### Parallel workstreams

| Workstream | Waves | Content |
|---|---|---|
| WS-KB — Knowledge base | W1–W2 | KB v1 for Kurnool crops (cotton, paddy, groundnut, maize, arhar, castor, foxtail/barnyard millet, chilli + horticulture): ingestion, expert review, structured records + passages, test cases, evidence ledger, versioning |
| WS-RULES — Rules engine | W1–W2 | PPQS/CIB&RC regulatory data (banned/refused/restricted, effective 31 Mar 2024 + gazette updates), dose/PHI/PPE rules, application method, weather-window rules (IMD), confidence gates, clarification policy |
| WS-KIOSK — Kiosk MVP | W1 | Touch + text + print + basic voice: information workflow end-to-end (v1 Phase 4 exit) |
| WS-AI — AI/RAG | W2 | Local LLM (Gemma 3 12B) + hybrid retrieval (BGE-M3 + reranker): grounded structured answers (v1 Phase 5 exit) |
| WS-VOICE — Voice | W2 | Full voice pipeline: Vaani-Whisper + SraVaani fallback, Piper TTS, confirmation gates, latency SLOs |
| WS-PORTAL — Scientist portal | W2 | Approve/correct/escalate with minimal input (v1 Phase 6 exit) |
| WS-OFFLINE — Offline core | W3 | Local execution + encrypted sync: core service works without network (v1 Phase 8 exit)

## 2. Phase details (0–15)

### Phase 0 — Governance, safety, escalation policy

- **Objective:** establish the authority, safety, data, source and escalation policies that everything else builds on; start long-lead external dependencies.
- **Key tasks:**
  - Draft and sign the governance specification (roles, authority, approval matrix, roadmap §4.1).
  - Safety policy: risk tiers, blocking-rules inventory, prohibited-output list, PHI/PPE defaults, weather-window policy.
  - Data policy: consent design, retention schedule, PII minimization, DPDP mapping, media handling (face-blur decision).
  - Source policy: authoritative source hierarchy (roadmap §4.6.1).
  - Escalation policy: L0–L4 triggers, SLAs, institutional response owners.
  - Trial protocol: supervision level per month, metrics, exit criteria, institutional approval gates.
  - **DPDP compliance program kickoff:** grievance officer, consent capture design, breach-response process, retention automation (full fiduciary obligations effective May 2027 — must be complete before trial, roadmap §14.4).
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
  - Case graph schema (CST) per [03-data-model.md](03-data-model.md): case, case_node (all node types), media, decisions, decision_deltas, evidence_ledger, kb_entries/passages, rules, learning_candidates, version_registry, prescriptions, devices/sync, weather_snapshots, regulatory_products, lexicon.
  - Pydantic v2 models + OpenAPI; ULID IDs; append-only invariants enforced by DB triggers.
  - input-orchestrator (S4) + case-service (S7) skeleton; version registry + version-tuple recording.
  - Platform skeleton: monorepo, CI/CD (GitHub Actions), Docker, K3s central cluster, PostgreSQL 17 + pgvector, Keycloak, OpenTelemetry, MinIO, Redis, EMQX, Caddy.
  - Kiosk device procurement (hardware lead time — order in M1, §5.1 below).
  - **Evaluation sets kickoff (KVK-curated):** Telugu agri-vocabulary ASR set (≥ 500 utterances), KB retrieval set, disease/pest image set (labeling plan), Telugu QA set.
  - Kiosk MVP build (WS-KIOSK): touch guided flow + text + print + basic voice (information workflow).
  - KB v1 ingestion start (WS-KB); rules v1 start (WS-RULES: regulatory data parsing first).
- **Deliverables:** schema v1.0 (frozen at M3); core-api skeleton; CI/CD green; central platform live; kiosk hardware ordered; evaluation-set plan + labeling guidelines; kiosk MVP demo (information workflow).
- **Exit criteria:** (a) text/voice/picture representable identically — automated test builds the same case from each modality; (b) complete workflow representable structurally (v1 Phase 1 exit); (c) kiosk MVP: information workflow works end-to-end (touch+text+print, v1 Phase 4 exit).
- **Duration:** M1–M3.
- **Dependencies:** Phase 0 (data policy, consent design); hardware lead time.
- **Key risks:** schema churn (mitigation: freeze at M3; later changes via release framework); hardware delay (mitigation: order M1, spec-locked BOM §5.1).

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
  - CST state machine implementation (roadmap §4.2.2) with transition guards + invariant tests.
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
- **Key risks:** ASR accuracy on local dialect below threshold — mitigation: SraVaani fallback, BHASHINI cross-check, confirmation gates, lexicon growth loop; if still below threshold at M7, domain fine-tune of IndicWav2Vec/SraVaani (NeMo) is the pre-approved next step (ASR-0.2.0, roadmap §5.3).

### Phase 5 — Image evidence pipeline

- **Objective:** photos become governed evidence: quality checks + structured observations + classifier, without forcing a diagnosis.
- **Key tasks:**
  - Image quality check (deterministic + model) with concrete retry instructions (source §38.1).
  - Gemma 3 vision structured observations (OBSERVED/POSSIBLE/UNCERTAIN/CONTRADICTORY/NOT_VISIBLE) via Ollama.
  - ViT/ConvNeXt classifier: KVK dataset v1 (top 10–15 diseases/pests; ≥ 500 images/class; two-scientist labeling + adjudication), training on GPU node, ONNX export for edge.
  - Media-set management + explicit missing-view requests (source §38.3).
  - Image → hypothesis integration (conflict → clarification branch, source §38.2).
  - Face-blurring pipeline for stored media (roadmap §9.4.6).
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

### Phase 8 — Scientist multimodal feedback

- **Objective:** scientists can approve/correct/escalate using voice, text, image or structured fields — and every feedback becomes a structured decision delta with the full context auto-attached.
- **Key tasks:**
  - Review queue (scientist portal + WhatsApp notifications): prescriptions + uncertain cases, SLA-tracked (≤ 24 h; trial: same day).
  - Minimal-field correction UX (source §7): scientist changes **only the wrong fields**; system auto-attaches the complete context snapshot (case, language, input, crop, problem, location, weather, soil, previous management, knowledge, rules, AI, scientist, output, audit).
  - Decision-delta creation + classification (10 types, roadmap §4.3.2) + evidence status (EVIDENCE_BACKED / LOCALLY_VALIDATED / EXPERT_PREFERENCE).
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
  - EscalationEngine L0–L4 (roadmap §4.4) with evidence- and policy-driven triggers (repeated contradictory information; image cannot distinguish alternatives; treatment failed; severity increasing; suspected regulatory issue; novel symptom; possible harmful recommendation; scientist disagreement; missing critical information).
  - Assignment + status workflow `OPEN → ASSIGNED → INVESTIGATING → RESOLVED → LEARNING_CAPTURED`.
  - Compact human-handoff packet (source §49): case summary, media, interpretation, contradictions, hypotheses, evidence, previous treatments, weather, AI recommendation, reason for escalation.
  - Farmer-facing transparency: case ID + status + concrete next steps (send another photo, voice explanation, wait for expert, visit center).
  - SLA tracking + alerts (L2 ≤ 24 h; L3 ≤ 48 h per institutional policy; L4 immediate + incident process, roadmap §14.7).
- **Deliverables:** escalation-service v1; handoff packet template; SLA dashboard; L4 incident runbook.
- **Exit criteria:** failed/uncertain/high-risk cases reach humans (automated test on the full trigger matrix); every escalation has an ID + status (test); farmer receives next-steps message on every escalation (test).
- **Duration:** M8–M10.
- **Dependencies:** Phase 9 (failure triggers); Phase 8 (scientist queue).
- **Key risks:** SLA breach during trial (mitigation: same-day review policy month 1, queue alerts, backup reviewer); L4 under-reporting (mitigation: rule-block + safety metrics feed the L4 trigger automatically, not just human judgment).

### Phase 11 — Learning sandbox

- **Objective:** corrections + outcomes become governed candidates — knowledge, rule, training or language — with full provenance; nothing reaches production unvalidated.
- **Key tasks:**
  - Correction classifier (10 delta types) + routing to learning channels (roadmap §4.3.1).
  - Candidate generation: knowledge candidates (with source verification), rule candidates (IF/THEN + scope), training examples (error classes appropriate for model learning), lexicon mappings.
  - Provenance ledger: all 11 fields (roadmap §4.3.3) non-null or explicitly N/A — enforced at ingestion.
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
  - Trial exit review: metrics vs acceptance criteria (§3 below); go/no-go for governed production.
- **Deliverables:** trial dataset (cases, corrections, outcomes — DVC-versioned); baseline metrics report; monthly trial reports (×3); trial exit report with institutional recommendation.
- **Exit criteria:** baseline + outcome dataset established (volume + quality thresholds per trial protocol); trial acceptance criteria met or gaps documented with remediation plan; institutional go/no-go recorded.
- **Duration:** M10–M13 (3 months).
- **Dependencies:** Phases 0–12 complete; DPDP program complete (full fiduciary obligations effective May 2027 — trial starts Jul 2027, compliant by design).
- **Key risks:** trial contamination (version changes during trial) — mitigation: freeze + change-freeze policy + version-tuple audit; scientist bottleneck — mitigation: review SLA, queue prioritization, backup reviewer; low farmer participation — mitigation: KVK outreach, operator assistance, WhatsApp channel; **three months is a trial duration, not automatic authorization for unsupervised prescriptions** (source §6) — any oversight reduction requires measured performance + institutional approval.

### Phase 14 — MLOps / KnowledgeOps

- **Objective:** candidates are testable, versioned and rollbackable — the full release pipeline (roadmap §4.5) is operational and proven.
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
  - Operations handover: runbooks (roadmap §17.4), operator + scientist training, SLOs, on-call rotation, DPDP operational compliance check.
  - Final documentation + audit (prescription → version-tuple traceability sample; learning provenance sample; security audit).
- **Deliverables:** second kiosk (or district-ready package); scale test report; channel parity report; operations handover package; final audit report.
- **Exit criteria:** same intelligence across kiosk/WhatsApp/web (automated parity test); repeatable multi-kiosk deployment (v1 Phase 11 exit — second device provisioned + synced + serving in < 1 day); audit sample: 100% of sampled prescriptions trace to model/KB/rule versions.
- **Duration:** M15–M18.
- **Dependencies:** Phase 14 (release pipeline); Phase 13 exit (institutional go-ahead).
- **Key risks:** scope creep ("district scale" = architecture ready + 2nd kiosk, not N kiosks — mitigation: explicit exit criteria); operational ownership ambiguity (mitigation: handover package signed by KVK + ANGRAU in M17).

## 3. Gantt (M1–M18)

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

## 4. Milestones

| ID | End of | Milestone | Verified by |
|---|---|---|---|
| MS1 | M1 | Governance approved; team assembled; central platform skeleton live; IMD/WhatsApp requests submitted | Phase 0 exit sign-off |
| MS2 | M3 | Kiosk MVP demo (touch+text+print, information workflow); schema v1 frozen; KB v1 + rules v1 frozen for benchmark; hardware ordered | Phase 1 exit + WS-KB/WS-RULES/WS-KIOSK gates |
| MS3 | M5 | Three channels → same case service; cross-channel continuation demo; CST operational | Phase 2 + Phase 3 (partial) exit |
| MS4 | M8 | Full v2 intelligence stack (cross-correction, image pipeline, verification, similar cases, scientist multimodal feedback); **trial readiness review (go/no-go)** | Phases 4–8 exit + red-team suite green |
| MS5 | M10 | Closed loop complete (outcome, escalation, learning sandbox, offline media sync) + MLOps foundation; **trial start** | Phases 9–12 exit + trial protocol sign-off |
| MS6 | M13 | Trial complete: baseline + outcome dataset; monthly reports; **institutional go/no-go for governed production** | Phase 13 exit + trial acceptance criteria (§5 below) |
| MS7 | M16 | MLOps/KnowledgeOps hardened; first governed release cycle complete (KB + rule); rollback drill passed | Phase 14 exit |
| MS8 | M18 | Multi-channel scale; second kiosk (or district-ready package); operations handover signed; final audit | Phase 15 exit |

## 5. Acceptance criteria traceability (source §54)

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

## 6. Team & roles

### 6.1 Staffing model

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

### 6.2 Role definitions

| Role | Peak FTE | Active | Core responsibilities | Key skills |
|---|---|---|---|---|
| **Project Lead** | 1 | M1–M18 | Delivery & phase gates; risk register (§8 below); stakeholder management (KVK/ANGRAU/ICAR); change control | Delivery of complex systems; ag-tech domain helpful; Telugu helpful |
| **Product Owner (KVK)** | 0.5 | M1–M18 | Requirements & acceptance; trial protocol; institutional sign-offs; prioritization with scientists | KVK advisory experience; extension systems |
| **KVK Scientists (2–3, part-time)** | 1.5 | M1–M18 (peak M4–M13) | KB review & rule validation; review queue (trial: every prescription); labeling (two-scientist, roadmap §13.8); trial supervision; field validation | Crop protection / agronomy of Kurnool crops; Telugu |
| **Knowledge Engineer** | 1 | M1–M9 (0.5 M10–M18) | KB ingestion/normalization; evidence ledger; lexicon v1+; test cases per entry; KnowledgeOps (roadmap §17.6) | Data curation; Telugu; agricultural sources |
| **ML Engineer — Speech** | 1 | M2–M10 | ASR chain (Vaani-Whisper / SraVaani / BHASHINI); agri-vocab set (≥ 500 utterances); per-engine benchmarks; Piper TTS MOS; ASR-0.2.0 fine-tune if gate fails | Speech ML; faster-whisper / ONNX / NeMo; Telugu audio data |
| **ML Engineer — Vision + LLM** | 1.5 | M2–M16 | Gemma 3 vision observations; ViT classifier (dataset + training + ONNX); LLM prompting/shadow; RAGAS/DeepEval evals; fine-tuning pipeline | Multimodal ML; PyTorch/ONNX; RAG evaluation |
| **Backend Engineer** | 2.5 | M1–M18 | Core services S4–S20; API contracts (roadmap §7); sync (S19); integrations (IMD, WhatsApp, BHASHINI); Postgres schema | Python/FastAPI; PostgreSQL; MQTT; distributed systems |
| **Flutter Engineer** | 1 | M1–M10 | Kiosk app: voice/touch/text/camera/print/TTS; kiosk mode; offline queue UX | Flutter (Linux); audio/camera/ESC-POS plugins |
| **React Engineer** | 1 | M3–M18 | Scientist portal, admin console, web PWA (S21/S22/S3) | React/TypeScript; PWA; data viz |
| **DevOps/SRE** | 1 | M1–M18 | CI/CD; K3s; observability; DR/backup; device fleet ops; on-call (roadmap §17.2) | Docker/K3s; Terraform; Prometheus/Grafana; Linux |
| **Data Engineer** | 1 | M1–M9 (0.5 M10–M13) | Data model (roadmap §6); ingestion pipelines; DVC datasets; analytics aggregates; retention automation | SQL; pipelines; DVC; data quality |
| **QA/Evaluation Engineer** | 1 | M1–M18 | Test pyramid (roadmap §13); eval harness; red-team suite; UAT; trial metrics; golden-case corpus | Test automation; AI evaluation; Telugu for UAT |
| **Security Engineer** | 0.5 | M1–M18 (peak M1–M5, M10–M13) | Threat model (roadmap §14.1); Keycloak; mTLS/signed bundles; DPDP program support; incident response | Application security; IAM; DPDP |
| **UX Researcher** | 0.25 | M1–M13 | Farmer UAT design; Telugu comprehension tests; accessibility (low-literacy); trial UX monitoring | Field UX research; Telugu; low-literacy populations |
| **Field/Hardware Engineer** | 1 (0.5 after M10) | M1–M18 | Kiosk BOM (§5.1 below); installation (power/network/UPS); printer maintenance; spares; device re-provisioning | Industrial hardware; site operations |
| **DPDP Compliance Lead** | 0.25 | M1–M13 | Consent design; data mapping; retention; breach process (72 h); grievance (90 d); DPBI liaison; pre-trial audit | DPDP Act/Rules; privacy operations |

**Peak total: ~16 FTE** (external ~13 + institutional ~3) — within the 14–16 FTE envelope (roadmap §1.4). The 3rd backend and the 2nd ML-vision seat are temporary (M4–M8, classifier + channel crunch).

### 6.3 RACI matrix (key deliverables)

R = Responsible (does the work) · A = Accountable (owns the outcome) · C = Consulted · I = Informed.

| Deliverable | PL | PO | SC | KE | ML | BE | FE | RE | DO | DE | QA | SE | UX | HW | DP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Governance spec + policies (P0) | A | R | C | C | I | I | I | I | I | I | I | C | I | I | C |
| Canonical schema v1 (roadmap §6) | A | C | I | C | I | R | C | C | C | R | C | C | I | I | I |
| KB v1 (WS-KB) | A | C | R | R | I | C | I | I | I | C | C | I | I | I | I |
| Rules v1 (WS-RULES) | A | C | R | C | I | R | I | I | I | I | C | C | I | I | I |
| Kiosk MVP (WS-KIOSK) | A | C | C | I | I | C | R | I | C | I | C | I | C | R | I |
| Channel adapters (P2) | A | C | I | I | I | R | C | R | C | I | C | C | I | I | I |
| Case-to-Solution Tree (P3) | A | C | C | I | I | R | C | I | I | C | C | I | I | I | I |
| Voice pipeline (WS-VOICE / P4) | A | C | C | C | R | C | C | I | C | I | C | I | C | I | I |
| Image pipeline (P5) | A | C | R | I | R | C | C | I | C | C | C | I | I | I | I |
| Verification engine (P6) | A | C | C | I | C | R | I | I | I | I | R | C | I | I | I |
| Similar-case service (P7) | A | C | C | I | R | R | I | I | I | C | C | I | I | I | I |
| Scientist portal (WS-PORTAL / P8) | A | C | R | I | C | C | I | R | C | I | C | C | C | I | I |
| Outcome engine (P9) | A | C | C | I | I | R | I | I | I | I | C | I | I | I | I |
| Escalation engine (P10) | A | C | C | I | I | R | I | I | I | I | C | I | I | I | I |
| Learning sandbox (P11) | A | C | R | C | R | R | I | I | I | C | C | I | I | I | I |
| Offline + media sync (P12) | A | I | I | I | I | R | C | I | R | I | C | C | I | C | I |
| Trial (P13) | A | R | R | C | C | C | I | I | C | I | R | C | C | C | C |
| MLOps / KnowledgeOps (P14) | A | C | C | R | R | C | I | I | R | C | C | C | I | I | I |
| Multi-kiosk scale (P15) | A | C | C | I | I | C | I | I | R | I | C | C | I | R | I |
| Security & DPDP program | A | C | I | I | I | C | I | I | C | C | I | R | I | I | R |
| Kiosk hardware & site | A | C | I | I | I | I | I | I | C | I | I | C | I | R | I |

*PL = Project Lead · PO = Product Owner (KVK) · SC = KVK Scientists · KE = Knowledge Engineer · ML = ML Engineers · BE = Backend · FE = Flutter · RE = React · DO = DevOps/SRE · DE = Data Engineer · QA = QA/Evaluation · SE = Security · UX = UX Researcher · HW = Field/Hardware · DP = DPDP Compliance Lead.*

### 6.4 Institutional roles (KVK / ANGRAU / ICAR)

| Role | Person / body (verified) | Involvement |
|---|---|---|
| Programme Coordinator, KVK Banavasi | Dr. K. Raghavendra Chowdary (kvk.banavasi@angrau.ac.in) | Institutional sponsor; approval path; site & staff |
| KVK scientists (2–3) | KVK crop-protection & agronomy staff | Review queue, KB/rules validation, labeling, trial supervision |
| ANGRAU Extension Directorate | ANGRAU, Hyderabad | Governance sign-off; scale-up decisions (Level 3–5, source §31) |
| ICAR (KVK network) | ICAR, New Delhi | Network-level oversight; district/state scale policy |

- Scientists are **part-time contributors** (~0.5 FTE each); their time is the critical path for KB v1 (M1–M5), image/ASR labeling (M4–M8) and the trial (M10–M13) — protected by the trial protocol and review SLA (roadmap §17.1).
- A **single approval path via ANGRAU** is used for institutional sign-offs (Phase 0 risk mitigation, §2 above).

### 6.5 Staffing risks & notes

- **Key-person risk (R19):** every role keeps handover notes; ML and backend roles pair on core services; runbooks (roadmap §17.4) reduce bus-factor.
- **Telugu capability:** at least two staff (QA, UX) must be Telugu-fluent for UAT; scientists provide domain Telugu; KB/lexicon content is Telugu-first.
- **Hiring lead time:** ML (speech/vision) and Flutter are the hardest roles to fill — start requisitions in M1 (Phase 0); contractors acceptable for Flutter (W1) with IP assignment.
- **Trial-period load:** during M10–M13 the team is on extended support hours (trial is live farmer-facing); on-call rotation per roadmap §17.2.
- **No pricing/financial estimates** per source document — FTE counts are planning units only.

## 7. Hardware & infrastructure

### 7.1 Kiosk device (BOM)

**Option A (primary): industrial mini-PC + discrete GPU** — best inference performance, standard parts, easy service.

| Subsystem | Specification | Notes |
|---|---|---|
| Compute | Industrial mini-PC / edge PC, 16-core x86 CPU, 64 GB RAM | Runs the Docker Compose stack (kiosk-ui, core-api, Ollama, faster-whisper, Piper, Postgres, EMQX edge) |
| GPU | NVIDIA RTX 4060 Ti 16 GB (alt: RTX 4080 16 GB) | Sizing rationale below |
| Display | 21.5–27" capacitive touchscreen, ≥ 1000 nits, anti-glare | Sunlight-readable (semi-outdoor kiosk); large type per roadmap §4.9 |
| Microphone | 4-mic directional array, beamforming + echo cancellation | 16 kHz capture; echo cancellation during TTS playback (roadmap §9.1.5) |
| Speaker | ≥ 20 W, high clarity | TTS output |
| Camera | 1080p with **physical privacy shutter** | Guided framing overlay (roadmap §9.4.1); shutter = visible privacy control |
| Printer | ESC/POS 80 mm thermal printer (USB/serial), paper-out detection | Prescription print; error status to device-agent |
| Power | UPS, 10–15 min runtime, graceful shutdown | Power loss → watchdog → clean state (roadmap §3.4) |
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

Worst-case concurrent (LLM drafting + ASR + embeddings): ~13.5 GB → **16 GB VRAM is comfortable** with headroom for KV cache and batched vision observations. The GPU queue (roadmap §8.2 S10) prioritizes prescription drafting > observations > ASR; ASR always has the CPU/ONNX escape path (SraVaani) so the farmer is never blocked on GPU contention (roadmap §9.1.2).

**Procurement:** order in M1 (hardware lead time 4–8 weeks for display + GPU + enclosure integration); spec-locked BOM; spares kit (printer, paper, display cable, 4G SIM); site survey (power, network, mounting) in M1–M2 (open question D8, §9 below).

### 7.2 Central platform sizing

| Component | Pilot specification | Notes |
|---|---|---|
| K3s cluster | 3 × 16 vCPU / 64 GB RAM / 500 GB NVMe (or 2 VMs for pilot simplicity) | Adapters, core services, Keycloak, MLflow, Metabase, EMQX, Prometheus/Grafana/Loki |
| PostgreSQL 17 + pgvector | Dedicated: 16 vCPU / 64 GB / 1 TB NVMe | System of record + vectors; PITR (§7.4) |
| GPU node (on-demand) | A100 40 GB **or** 2 × RTX 4090 48 GB **or** rented cloud GPU | Fine-tuning (Unsloth/axolotl + LoRA), shadow evals, central ASR for WhatsApp voice notes; owned-vs-rented decision at M9 (open question D7, §9 below) |
| Object storage | MinIO (erasure-coded; 4 disks or 1 node + offsite backup) | Media, signed bundles, model artifacts, backups |
| Redis 7 | On K3s node | Sessions, queues, rate limits |
| Network | 1 Gbps uplink; public ingress via Caddy/Traefik + WAF | Public endpoints: WhatsApp webhook, web PWA, prescription verification API, portals |
| Power / environment | KVK server room or colocation; UPS + generator backup; 20–25 °C | Rural power reliability → generator backup is a hard requirement |

### 7.3 Network & connectivity

**Edge (kiosk):**
- Primary: Ethernet to KVK LAN; fallback: Wi-Fi 6; last resort: 4G LTE (SIM with data plan).
- Outbound only: mTLS to central (device certificate, roadmap §3.8); telemetry buffered locally when offline (MQTT QoS 1).
- No inbound ports on the device (remote ops via the central command channel, roadmap §7.5).

**Central:**
- Public HTTPS endpoints (TLS 1.3, WAF, rate limiting): WhatsApp webhook (Meta), web PWA, prescription verification API (QR scan), scientist/admin portals.
- **IMD API:** outbound from a **whitelisted IP** (application submitted M1 — long-lead, roadmap §10.2 Phase 0); attribution displayed per IMD terms.
- **WhatsApp:** Meta webhook verification (GET verify token) + outbound Graph API; via BSP or direct (open question D3, §9 below).
- Internal: EMQX MQTT (device sync/telemetry), service-to-service via K3s services.

### 7.4 Backup & disaster recovery

| Asset | Backup | RPO | Restore |
|---|---|---|---|
| PostgreSQL (central) | Continuous WAL archiving (PITR) + daily base backup, offsite copy | ≤ 5 min | PITR to any point; tested quarterly |
| MinIO (media/bundles) | Versioning + cross-region / secondary-site replication | ≤ 24 h (media re-fetchable from edge queue) | Restore from replica |
| Config / IaC / code | Git (monorepo) | 0 | Re-apply via Terraform/CI |
| MLflow / DVC | Backed with MinIO + Postgres | ≤ 24 h | Re-register from artifacts |
| Keycloak | Postgres (covered above) + realm config export | ≤ 5 min | Re-import |
| Edge device | Not backed up — **re-provisioned** from signed bundles | n/a | Full re-image + sync < 1 day (device is stateless w.r.t. production artifacts; local case data re-syncs from central) |

**DR posture:**
- **Central outage:** edge kiosks keep serving (offline-first, roadmap §3.4) — information/advisory from cache, printing works, prescriptions hold at "pending approval" per policy; WhatsApp/web degraded. RTO for central failover ≤ 4 h (standby VM/cluster; manual failover at pilot).
- **Edge failure:** farmer impact is local; KVK counter (or second kiosk, M15+) covers; re-provisioning runbook (roadmap §17.4).
- **Restore drills:** quarterly (Postgres PITR + MinIO + one edge re-provision); annual full DR exercise.

### 7.5 Deployment topology summary

| Layer | Location | Runs |
|---|---|---|
| Edge (per kiosk) | KVK site | kiosk-ui, core-api (full decision pipeline), Ollama, faster-whisper, Piper, Postgres+pgvector (local), EMQX edge, sync-agent, device-agent |
| Central | KVK server room / colocation | Channel adapters (WhatsApp/web), core services (system of record), Keycloak, Postgres 17, MinIO, Redis, EMQX, MLflow/DVC, Metabase, Prometheus/Grafana/Loki, weather ingestion worker |
| GPU node | Central or rented cloud | Fine-tuning, shadow/canary evals, central ASR (WhatsApp voice notes) |
| External | — | IMD API, PPQS/CIB&RC (manual), BHASHINI, WhatsApp/Meta, (BSP) |

## 8. Risk register

Risks are tracked with ID, category, likelihood (H/M/L), impact (H/M/L), mitigation, owner, and monitor. Reviewed weekly (KVK + platform) and at every phase gate. Owners are role codes from §6.2; "institution" = KVK/ANGRAU.

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
| R16 | Prompt injection / LLM misuse | AI safety | M | M | 7-layer defense (roadmap §14.5); red-team CI; monitoring; kill switch | SE | Red-team results, injection attempts |
| R17 | Skill gaps (Telugu ML, Flutter) | Organizational | M | M | Hiring M1; contractors with IP assignment; pairing; Telugu-fluent QA/UX | PL | Hiring status, handover notes |
| R18 | Scope creep ("district scale", extra channels) | Program | M | M | Explicit exit criteria; 18-month scope locked; change control via release framework | PL | Scope change log |
| R19 | Key-person dependency | Organizational | M | M | Handover notes; pairing on core services; runbooks (roadmap §17.4); documentation | PL | Bus-factor review quarterly |
| R20 | Trial contamination (unfrozen changes during trial) | Program | M | H | Change-freeze policy; version-tuple audit daily; staging-only changes; trial protocol | QA | Version-tuple audit |

**Risk review cadence:** weekly during trial (M10–M13); bi-weekly otherwise. Every risk with likelihood H or impact H has a named owner and a monitor metric in the KPI catalog (roadmap §16.3, see [08-operations.md](08-operations.md)).

## 9. Open questions

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
