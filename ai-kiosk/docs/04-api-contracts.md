# 04 — API Contracts

> Roadmap §7. All endpoints are typed (Pydantic v2 request/response). LLM output is
> schema-validated **before** entering the rules/prescription pipeline.
> Auth: OIDC bearer (Keycloak) for scientist/admin/auditor; device mTLS for sync;
> farmer endpoints are pseudonymous (case-scoped tokens).
>
> Request/response models: `packages/canonical-schema/src/canonical_schema/api.py`.

## 1. Core session & input (v1 + v2)

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

## 2. Retrieval, rules, advisory (v1)

| Method & path | Purpose | Notes |
|---|---|---|
| `POST /v1/retrieval/search` | Hybrid evidence retrieval | filters {crop, stage, region, validity}; returns ranked evidence with method+score+authority |
| `POST /v1/rules/evaluate` | Deterministic validation | input: decision draft + context; output: per-rule results (pass/block/review/warn) |
| `POST /v1/advisory/draft` | Grounded advisory draft | LLM draft with evidence IDs; schema-validated; risk tier assigned |
| `POST /v1/prescriptions` | Create locked prescription | Only from approved decision; records version tuple |
| `GET /v1/prescriptions/{id}` | Verify prescription | Public verification (QR scan): status, content, versions, scientist, expiry |
| `POST /v1/print` | Print approved artifact | Idempotent (print_id); printer status checked; no duplicate on failure |

## 3. Review & learning (v1 + v2)

| Method & path | Purpose | Notes |
|---|---|---|
| `POST /v1/review` | Approve/correct/escalate | Scientist changes only wrong fields; system auto-attaches full context snapshot |
| `POST /v1/corrections` | Persist decision delta | Creates decision_delta + context snapshot; classifies correction type |
| `POST /v1/scientist/feedback` | Voice/text/image/annotated/structured feedback (v2) | ASR for voice; media attach; same delta pipeline |
| `POST /v1/learning/candidates` | Create candidate learning artifact | From approved deltas/outcomes |
| `GET /v1/learning/candidates` | Scientist review queue | Filter by channel/status |
| `GET /v1/learning/provenance/{id}` | Trace learning signal to source case (v2) | Full 11-field provenance |
| `POST /v1/releases` | Approve release (shadow→canary→production) | Release authority role; triggers signed bundle build |

## 4. Sync & device (v1)

| Method & path | Purpose | Notes |
|---|---|---|
| `POST /v1/sync/push` | Upload queued events | Batch, idempotent by event_id; returns acks + gaps |
| `GET /v1/sync/manifest` | Get current versions for device | Returns artifacts newer than device's active tuple |
| `GET /v1/device/health` | Device health report | Telemetry batch (also via MQTT) |
| `POST /v1/followups` | Schedule outcome follow-up (v2) | Protocol-based window; channel selection |
| `GET /v1/escalations` | Scientist escalation queue (v2) | Level, SLA age, packet |

## 5. MQTT topics (device ↔ central)

| Topic | Direction | Payload | QoS |
|---|---|---|---|
| `kiosk/{device_id}/telemetry` | edge → central | health, temp, disk, printer, sync backlog | 1 |
| `kiosk/{device_id}/events` | edge → central | batched sync_events (mirror of `/v1/sync/push`) | 1 |
| `kiosk/{device_id}/manifest` | central → edge | sync_manifest (versions to fetch) | 1 |
| `kiosk/{device_id}/command` | central → edge | {reboot, fetch_bundle, reset_session, update_app} | 1 |
| `kiosk/{device_id}/ack` | edge → central | manifest applied / command result | 1 |
| `alerts/safety` | edge → central | L4 incident (immediate) | 2 |

## 6. Webhooks (inbound)

| Source | Endpoint | Handling |
|---|---|---|
| WhatsApp Cloud API | `POST /webhooks/whatsapp` | Verify token (GET); parse text/audio/image messages → `case_id` mapping (phone → farmer_ref → active case); media download to MinIO |
| IMD (polling, not webhook) | `weather-service` worker | 15–60 min poll → `weather_snapshots` → edge cache update via manifest |

## 7. Conventions

- **Errors:** RFC 7807 `problem+json`; domain error codes (`RULE_BLOCKED`, `CONFIRMATION_REQUIRED`, `WEATHER_STALE`, `APPROVAL_REQUIRED`, `SYNC_GAP`, ...).
- **Idempotency:** `Idempotency-Key` header on all mutating endpoints; sync events idempotent by `event_id`.
- **Pagination:** cursor-based (`?cursor=&limit=`).
- **Versioning:** URL prefix `/v1`; breaking changes → `/v2` with 6-month overlap.
- **Traceability:** every response for a decision-bearing call includes `version_tuple` and `trace_id` (OpenTelemetry).

## 8. Health & observability endpoints (all services)

| Method & path | Purpose |
|---|---|
| `GET /health` | Liveness: `{status: "ok", service, version, uptime_s}` |
| `GET /ready` | Readiness: dependencies (DB, Redis, MinIO, Ollama) checked |
| `GET /metrics` | Prometheus text format (where exposed) |
