# canonical-schema

Canonical multimodal case schema (CST) — Pydantic v2 models for the AI Kiosk v2
case graph, knowledge, rules, learning, devices and API contracts.

**Purpose:** one canonical representation for text/voice/picture so that every
modality is represented identically (Phase 1 exit criterion). This package is
the single source of truth for all service payloads and the DDL in
`db/migrations/0001–0006`.

**Responsibilities:**
- Case graph: `Case`, `CaseNode` + 15 typed node payloads (discriminated union on `node_type`)
- Decisions: `DecisionDelta` (learning object), `Prescription`
- Knowledge: `KBEntry`, `KBPassage`, `EvidenceLedger`, `LexiconEntry`
- Rules: `Rule`, `RuleTestCase`, `RegulatoryProduct` (engine: `packages/agri-rules/`)
- Learning: `LearningCandidate` + 11-field `Provenance`
- Versioning: `VersionRegistryEntry`, `VersionTuple`
- Devices/sync: `Device`, `SyncEvent`, `SyncManifest`
- Weather: `WeatherSnapshot` (STALE → spray window UNKNOWN)
- Audit: `AuditEntry` (append-only, 7-year retention)
- API contracts: all request/response models from roadmap §7 (`api.py`)

**Tech:** Python 3.12, Pydantic v2, python-ulid. No I/O — pure data models.

**Interfaces:** imported by every service (`core-api`, `case-service`,
`speech-service`, `retrieval-service`, `image-service`, adapters, sync).
OpenAPI is generated from `api.py` models.

**Dependencies:** `pydantic>=2.9`, `python-ulid>=2.7`.

**Scaling:** stateless library; versioned in the version registry
(`schema` artifact class). Frozen at M3 (schema v1.0); later changes go
through the release framework.

**Built-in phase:** Phase 1 (M1–M3).

**Key invariants:**
- ULID IDs everywhere; UTC timestamps; Telugu-first `{te, en}` text.
- Append-only: `CaseNode.transition_status()` is the only legal mutation
  (`active → superseded | rejected`); DB triggers enforce the same.
- `VersionTuple` (model, knowledge, rules, prompt_policy, speech, schema) is
  required on every decision/prescription.
- Voice/touch/text/picture are first-class `Modality` values; touch confidence
  is 1.0 by construction (set by the orchestrator, not the model).
- Provenance: all 11 fields non-null or explicitly "N/A".

**Spec:** [docs/03-data-model.md](../../docs/03-data-model.md),
[docs/04-api-contracts.md](../../docs/04-api-contracts.md), roadmap §6–§7.
