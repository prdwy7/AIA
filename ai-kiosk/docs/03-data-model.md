# 03 — Data Model

> Roadmap §6. Canonical, versioned schemas. All IDs are **ULIDs** (sortable, unique
> across edge+central). All timestamps are **UTC** with `Asia/Kolkata` display. All
> text fields store the original language; normalized fields are separate.
> **Nothing is ever overwritten** — corrections and reinterpretations append new
> rows/nodes.
>
> Machine-readable form: `packages/canonical-schema/` (Pydantic v2). DDL:
> `db/migrations/0001–0006`.

## 1. Case graph (Case-to-Solution Tree)

```text
case
 ├─ case_id (ULID) · short_code (e.g., "BNV-4F7K2") · qr_payload
 ├─ channel (kiosk | whatsapp | web | operator) · channel_ref (e.g., WhatsApp message thread ID)
 ├─ farmer_ref (nullable, pseudonymous) · consent_ref
 ├─ kiosk_id (nullable) · location {state, district, mandal, village, lat, lon, accuracy}
 ├─ language (te | en | te-en) · created_at · updated_at · status (lifecycle state, roadmap §4.2)
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

### 1.1 Node payloads (key types)

| Node type | Payload fields |
|---|---|
| **input** | `modality (voice \| touch \| text \| picture \| mixed)` · `raw_ref` (media ID for audio/image; raw string for text/touch) · `asr {model_id, version, confidence, duration_ms, engine: vaani-whisper \| sravaani \| bhashini}` (voice) · `quality {usable: bool, reasons[]}` (picture/audio) |
| **interpretation** | `transcript` (original, immutable) · `normalized_query` · `entities {crop, variety, stage, problem, product, dose, location, ...}` each `{value, confidence, source}` · `ambiguity {candidates[], explanation}` · `uncertainty_record {confidence, why, what_would_resolve}` |
| **correction** (InterpretationCorrection) | `input_id` · `original_interpretation_ref` · `corrected_interpretation` · `corrected_by (farmer \| scientist \| system-confirmed)` · `correction_reason` · `confidence_before` · `confidence_after` · `evidence_refs[]` |
| **observation** (image-derived) | `media_id` · `observation_type (lesion \| discoloration \| insect_presence \| distortion \| wilting \| other)` · `state (OBSERVED \| POSSIBLE \| UNCERTAIN \| CONTRADICTORY \| NOT_VISIBLE)` · `classifier {model_id, class, probability}` (nullable) · `vlm_notes` (structured, from Gemma 3 vision) |
| **hypothesis** | `problem_id` (from KB taxonomy) · `confidence` · `supporting_refs[]` · `contradicting_refs[]` · `missing_evidence[]` · `status (active \| confirmed \| rejected)` |
| **question** | `text (Telugu + English)` · `modality (voice \| touch \| text)` · `decision_purpose {resolves: hypothesis_ids, distinguishes: [A, B]}` · `options[]` (for touch: quick-reply buttons) · `asked_at` · `answered_at` (nullable) |
| **answer** | `question_node_id` · `value` · `modality` · `raw_ref` (nullable) · `confidence` |
| **evidence** | `evidence_ledger_id` · `retrieval {method: sql\|keyword\|vector\|hybrid, score, rank}` · `relevance_note` |
| **contradiction** | `field (crop \| stage \| problem \| ...)` · `existing_value` · `new_value` · `detected_by` · `resolution (clarified \| resolved_by_farmers_answer \| unresolved)` |
| **decision** | `intent (information \| diagnosis \| advisory \| prescription)` · `diagnoses[] {problem_id, confidence}` · `selected_diagnosis` · `interventions[] {product_id, formulation, dose, method, timing, phi_days, ppe[]}` · `warnings[]` · `evidence_refs[]` · `rules_evaluated[] {rule_id, result: pass\|block\|review, details}` · `confidence` · `model_version` · `knowledge_version` · `rule_version` · `prompt_policy_version` · `status (draft \| approved \| corrected \| rejected \| locked)` |
| **intervention** (delivered action) | `decision_node_id` · `delivered_at` · `delivery {voice, screen, print_id, qr_id, whatsapp_msg_id}` · `expected_observation` · `followup_due_at` (from protocol) · `status (delivered \| pending_approval \| blocked)` |
| **outcome** | `intervention_id` · `reported_at` · `reported_by (farmer \| worker \| scientist)` · `result (worked \| partial \| failed \| worsened \| unknown)` · `farmer_report` (text/voice ref) · `supporting_media[]` · `timing {days_after, weather_context_ref}` · `verified_by` (nullable) · `failure_class` (nullable, enum) · `escalation_id` (nullable) · `learning_status (pending \| captured \| rejected)` · `expected_result` |
| **escalation** | `level (L1..L4)` · `trigger {type, evidence_refs[]}` · `status (OPEN \| ASSIGNED \| INVESTIGATING \| RESOLVED \| LEARNING_CAPTURED)` · `assigned_to` · `assigned_at` · `resolved_at` · `resolution_note` · `packet_ref` (compact case packet for scientist) |
| **scientist_feedback** | `decision_node_id` · `scientist_id` · `modality (text \| voice \| image \| annotated_image \| structured)` · `action (approve \| correct \| reject \| escalate)` · `changed_fields[] {field, original_value, corrected_value}` · `reason` · `evidence_refs[]` · `reference_media[]` · `evidence_status (EVIDENCE_BACKED \| LOCALLY_VALIDATED \| EXPERT_PREFERENCE)` |

## 2. Decision delta (learning object)

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

**Invariant:** the original AI decision is never overwritten; original + corrected
states are both retained for learning and audit.

## 3. Evidence ledger

```text
evidence_ledger
 ├─ evidence_id · claim (normalized statement)
 ├─ source {type (law | institutional | kvc_sa | weather | research | local_validated | secondary),
 │          name, url/ref, version, published_date, retrieved_date}
 ├─ authority_level (1..7, roadmap §4.6.1) · effective_from · effective_to (nullable)
 ├─ superseded_by (nullable) · confidence (0..1)
 ├─ scope {crops[], regions[], seasons[]}
 └─ verified_by (scientist_id) · verified_at
```

## 4. Knowledge base (structured + passages)

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

## 5. Rules

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

Machine-readable form + engine: `packages/agri-rules/`.

## 6. Learning records & registry

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

**Provenance (11 fields, every learning signal must answer):** who provided it? ·
what did they observe? · when? · through which channel? · what evidence did they
provide? · what did the AI originally say? · what was corrected? · was it
independently verified? · did the farmer outcome support the correction? · was it
approved for learning? · which production version used it?

## 7. Device & sync

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

## 8. PostgreSQL table map (central)

| Table | Purpose | Key indexes | Migration |
|---|---|---|---|
| `cases` | Case headers | short_code, farmer_ref, status, created_at | 0002 |
| `case_nodes` | CST append-only nodes | (case_id, node_type), (case_id, created_at), GIN(payload) | 0002 |
| `media` | Audio/image metadata + MinIO refs | case_id, media_type | 0002 |
| `decisions` | Decision objects (denormalized from nodes for query) | case_id, status, version_tuple | 0002 |
| `decision_deltas` | Learning objects | correction_type, approval_status, learning_channel | 0002 |
| `evidence_ledger` | Claims → sources | authority_level, effective_from, GIN(scope) | 0002 |
| `kb_entries` / `kb_passages` | Knowledge + vectors | HNSW(embedding_dense), (entry_id), GIN(metadata) | 0003 |
| `rules` | Rule definitions | rule_class, status, GIN(scope) | 0003 |
| `learning_candidates` | Candidate artifacts | channel, status | 0004 |
| `version_registry` | Artifact versions | (artifact_class, version), status | 0004 |
| `prescriptions` | Locked prescriptions | prescription_id, case_id, status | 0004 |
| `outcomes` | Outcome records | case_id, result, reported_at | 0004 |
| `escalations` | Escalation workflow | status, level, assigned_to | 0004 |
| `followups` | Scheduled follow-ups | followup_due_at, status | 0004 |
| `devices` / `sync_events` / `sync_manifests` | Device fleet + sync | device_id, seq, ack_status | 0005 |
| `users` / `roles` (Keycloak-synced) | Identity | role | 0005 |
| `audit_log` | Append-only audit (who/what/when/version) | entity_type, entity_id, created_at | 0005 |
| `weather_snapshots` | Cached IMD data | (station_id, date), staleness | 0006 |
| `regulatory_products` | PPQS/CIB&RC parsed lists | active_ingredient, status (banned/refused/restricted/permitted) | 0003 |
| `lexicon` | Local terminology mappings | term, crop, region, status | 0003 |
| `similar_case_index` | Case embeddings for similarity | HNSW(embedding) | 0006 |

**Append-only enforcement:** DB triggers on `case_nodes` (and `audit_log`,
`sync_events`) reject UPDATE/DELETE except status transitions
(`active → superseded | rejected`).

## 9. Data retention & privacy

| Data class | Retention | Notes |
|---|---|---|
| Case graph + decisions | 5 years (institutional policy) | Agricultural record value; supports surveillance analytics |
| Media (photos/audio) | 1 year default; 5 years if flagged for diagnosis/learning with consent | Faces blurred by default in stored copies (policy decision) |
| Farmer PII (phone, if opt-in) | Until consent withdrawal + 90 days | DPDP Act 2023; purpose-limited |
| Learning records | 5 years | Provenance requirement |
| Audit log | 7 years | Institutional + regulatory |
| Weather cache | 90 days | Re-fetchable |
