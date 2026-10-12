"""API request/response models (roadmap §7; docs/04-api-contracts.md).

All endpoints are typed (Pydantic v2). LLM output is schema-validated
**before** entering the rules/prescription pipeline.

Conventions (roadmap §7.7):
- Errors: RFC 7807 `problem+json` with domain error codes.
- Idempotency: `Idempotency-Key` header on all mutating endpoints.
- Pagination: cursor-based (`?cursor=&limit=`).
- Every decision-bearing response includes `version_tuple` + `trace_id`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .common import BilingualText, VersionTuple
from .enums import (
    AsrEngine,
    CaseStatus,
    Channel,
    EscalationLevel,
    Intent,
    Language,
    Modality,
    OutcomeResult,
)

# ---------------------------------------------------------------------------
# Errors (RFC 7807)
# ---------------------------------------------------------------------------

DomainErrorCode = Literal[
    "RULE_BLOCKED",
    "CONFIRMATION_REQUIRED",
    "WEATHER_STALE",
    "APPROVAL_REQUIRED",
    "SYNC_GAP",
    "MEDIA_UNUSABLE",
    "VERSION_MISMATCH",
    "CONSENT_REQUIRED",
    "SLA_BREACH",
]


class ProblemDetail(BaseModel):
    """RFC 7807 problem+json with domain error codes."""

    model_config = ConfigDict(extra="allow")

    type: str = "about:blank"
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    error_code: DomainErrorCode | None = None


# ---------------------------------------------------------------------------
# Health & observability (all services)
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "down"] = "ok"
    service: str
    version: str
    uptime_s: float = Field(ge=0)


class ReadyResponse(BaseModel):
    ready: bool
    dependencies: dict[str, bool] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Session & input
# ---------------------------------------------------------------------------


class CreateSessionRequest(BaseModel):
    channel: Channel
    kiosk_id: str | None = None
    language: Language = Language.TE
    consent_ack: bool = Field(description="DPDP consent acknowledged")


class CreateSessionResponse(BaseModel):
    session_id: str
    case_id: str
    short_code: str


class TranscribeRequest(BaseModel):
    audio: str = Field(description="base64 or URL")
    language: Language = Language.TE
    engine_hint: Literal["auto"] | AsrEngine = "auto"


class TranscribeResponse(BaseModel):
    transcript: str
    confidence: float = Field(ge=0.0, le=1.0)
    engine_used: AsrEngine
    duration_ms: int = Field(ge=0)
    entity_candidates: list[str] = Field(default_factory=list)


class IntentParseRequest(BaseModel):
    text: str
    case_id: str


class IntentParseResponse(BaseModel):
    intent: Intent
    entities: dict = Field(default_factory=dict)
    ambiguity: dict | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class CreateCaseRequest(BaseModel):
    channel: Channel
    location: dict | None = None
    language: Language = Language.TE
    farmer_ref: str | None = None
    kiosk_id: str | None = None
    consent_ack: bool = True


class CreateCaseResponse(BaseModel):
    case_id: str
    short_code: str
    qr_payload: str


class AddInputRequest(BaseModel):
    modality: Modality
    payload: str | None = Field(default=None, description="Text/touch raw value")
    media_ref: str | None = Field(default=None, description="Media ULID for audio/image")
    asr_result: dict | None = None


class AddInputResponse(BaseModel):
    input_node_id: str
    quality: dict | None = None
    next_state: CaseStatus


class StoreInterpretationRequest(BaseModel):
    transcript: str | None = None
    entities: dict = Field(default_factory=dict)
    ambiguity: dict | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class StoreInterpretationResponse(BaseModel):
    interpretation_node_id: str


class AddCorrectionRequest(BaseModel):
    input_id: str
    corrected_entities: dict | None = None
    corrected_interpretation: str | None = None
    corrected_by: Literal["farmer", "scientist", "system-confirmed"]
    reason: str | None = None


class AddCorrectionResponse(BaseModel):
    correction_node_id: str
    confidence_after: float | None = Field(default=None, ge=0.0, le=1.0)


class AddQuestionRequest(BaseModel):
    purpose: dict = Field(description="{resolves: [hypothesis_ids], distinguishes: [A, B]}")
    options: list[str] = Field(default_factory=list)


class AddQuestionResponse(BaseModel):
    question_node_id: str
    text: BilingualText
    options: list[str] = Field(default_factory=list)


class AddAnswerRequest(BaseModel):
    question_node_id: str
    value: str
    modality: Modality


class AddAnswerResponse(BaseModel):
    answer_node_id: str
    next_state: CaseStatus


class GetTreeResponse(BaseModel):
    nodes: list[dict] = Field(default_factory=list)
    state: CaseStatus
    hypotheses: list[dict] = Field(default_factory=list)
    pending_questions: list[dict] = Field(default_factory=list)


class SimilarCasesRequest(BaseModel):
    top_k: int = Field(default=5, ge=1, le=20)
    filters: dict = Field(default_factory=dict, description="{crop, stage, region, season}")


class SimilarCaseResult(BaseModel):
    case_id: str
    similarity: float = Field(ge=0.0, le=1.0)
    differences: list[str] = Field(default_factory=list)
    outcome: OutcomeResult | None = None
    is_negative_evidence: bool = False


class SimilarCasesResponse(BaseModel):
    cases: list[SimilarCaseResult] = Field(default_factory=list)


class RecordOutcomeRequest(BaseModel):
    intervention_id: str
    result: OutcomeResult
    farmer_report: str | None = None
    media: list[str] = Field(default_factory=list)
    timing: dict | None = None


class RecordOutcomeResponse(BaseModel):
    outcome_id: str
    next_state: CaseStatus
    escalation_id: str | None = None


class EscalateRequest(BaseModel):
    level: EscalationLevel
    trigger: dict = Field(description="{type, evidence_refs[]}")


class EscalateResponse(BaseModel):
    escalation_id: str
    packet_ref: str
    farmer_message: BilingualText


class MediaAnalyzeRequest(BaseModel):
    media_ref: str
    case_id: str
    requested_views: list[str] = Field(default_factory=list)


class MediaAnalyzeResponse(BaseModel):
    quality: dict
    observations: list[dict] = Field(default_factory=list)
    candidate_hypotheses: list[dict] = Field(default_factory=list)
    missing_views: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Retrieval, rules, advisory
# ---------------------------------------------------------------------------


class RetrievalSearchRequest(BaseModel):
    query: str
    filters: dict = Field(default_factory=dict, description="{crop, stage, region, validity}")
    top_k: int = Field(default=10, ge=1, le=50)


class RetrievalEvidence(BaseModel):
    evidence_id: str
    claim: str
    method: str
    score: float | None = None
    rank: int | None = None
    authority_level: int = Field(ge=1, le=7)


class RetrievalSearchResponse(BaseModel):
    evidence: list[RetrievalEvidence] = Field(default_factory=list)
    version_tuple: VersionTuple


class RulesEvaluateRequest(BaseModel):
    decision_draft: dict
    context: dict = Field(default_factory=dict, description="case/weather/soil context")


class RuleResultItem(BaseModel):
    rule_id: str
    result: str
    details: str | None = None


class RulesEvaluateResponse(BaseModel):
    results: list[RuleResultItem] = Field(default_factory=list)
    blocked: bool
    requires_review: bool
    requires_confirmation: bool


class AdvisoryDraftRequest(BaseModel):
    case_id: str
    intent: Intent


class AdvisoryDraftResponse(BaseModel):
    draft: dict
    evidence_ids: list[str] = Field(default_factory=list)
    risk_tier: str
    version_tuple: VersionTuple
    trace_id: str


class CreatePrescriptionRequest(BaseModel):
    decision_node_id: str
    case_id: str
    scientist_id: str
    content: dict


class CreatePrescriptionResponse(BaseModel):
    prescription_id: str
    status: str
    version_tuple: VersionTuple
    qr_payload: str


class VerifyPrescriptionResponse(BaseModel):
    prescription_id: str
    status: str
    content: dict
    versions: dict
    scientist: str | None = None
    expiry: datetime | None = None


class PrintRequest(BaseModel):
    prescription_id: str
    print_id: str = Field(description="Idempotency key — no duplicate on failure")


class PrintResponse(BaseModel):
    print_id: str
    status: Literal["printed", "queued", "failed"]
    fallback: list[str] = Field(
        default_factory=list, description="QR + screen + WhatsApp when printer fails"
    )


# ---------------------------------------------------------------------------
# Review & learning
# ---------------------------------------------------------------------------


class ReviewRequest(BaseModel):
    decision_node_id: str
    scientist_id: str
    action: Literal["approve", "correct", "reject", "escalate"]
    changed_fields: list[dict] = Field(
        default_factory=list, description="Scientist changes only the wrong fields"
    )
    reason: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)


class ReviewResponse(BaseModel):
    decision_delta_id: str | None = None
    context_snapshot_ref: str
    version_tuple: VersionTuple


class PersistCorrectionRequest(BaseModel):
    decision_node_id: str
    case_id: str
    scientist_id: str
    changed_fields: list[dict] = Field(default_factory=list)
    correction_type: str
    reason: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    evidence_status: str = "EXPERT_PREFERENCE"


class PersistCorrectionResponse(BaseModel):
    delta_id: str
    context_snapshot_ref: str
    learning_channel: str


class ScientistFeedbackRequest(BaseModel):
    decision_node_id: str
    scientist_id: str
    modality: Modality
    action: Literal["approve", "correct", "reject", "escalate"]
    transcript: str | None = Field(default=None, description="For voice feedback (ASR output)")
    media_refs: list[str] = Field(default_factory=list)
    changed_fields: list[dict] = Field(default_factory=list)
    reason: str | None = None


class ScientistFeedbackResponse(BaseModel):
    delta_id: str
    context_snapshot_ref: str


class CreateCandidateRequest(BaseModel):
    channel: str
    source_refs: list[str] = Field(default_factory=list)
    payload: dict
    provenance: dict = Field(description="11-field provenance (all non-null or N/A)")


class CreateCandidateResponse(BaseModel):
    candidate_id: str
    status: str


class GetCandidatesResponse(BaseModel):
    candidates: list[dict] = Field(default_factory=list)
    cursor: str | None = None


class ProvenanceResponse(BaseModel):
    candidate_id: str
    provenance: dict


class ReleaseRequest(BaseModel):
    artifact_class: str
    version: str
    target_status: Literal["shadow", "canary", "production"]
    release_authority_id: str


class ReleaseResponse(BaseModel):
    release_id: str
    status: str
    bundle_ref: str | None = None


# ---------------------------------------------------------------------------
# Sync & device
# ---------------------------------------------------------------------------


class SyncPushRequest(BaseModel):
    device_id: str
    events: list[dict] = Field(default_factory=list, description="Batched sync_events")


class SyncPushResponse(BaseModel):
    acks: list[dict] = Field(default_factory=list)
    gaps: list[dict] = Field(default_factory=list, description="Detected sequence gaps")


class SyncManifestResponse(BaseModel):
    manifest_id: str
    artifacts: list[dict] = Field(default_factory=list)


class DeviceHealthRequest(BaseModel):
    device_id: str
    telemetry: dict


class DeviceHealthResponse(BaseModel):
    accepted: bool


class ScheduleFollowupRequest(BaseModel):
    case_id: str
    intervention_id: str
    protocol_ref: str
    channel: Channel | None = None


class ScheduleFollowupResponse(BaseModel):
    followup_id: str
    due_at: datetime


class EscalationsResponse(BaseModel):
    escalations: list[dict] = Field(default_factory=list)
    cursor: str | None = None
