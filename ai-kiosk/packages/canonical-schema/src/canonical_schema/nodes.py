"""Case-to-Solution Tree (CST) nodes (roadmap §6.1).

`case_node` is an **append-only** tree: no UPDATE except status transitions
(`active -> superseded | rejected`), enforced by DB triggers (migration 0002)
and mirrored here by the `CaseNode.transition_status()` helper.

The payload is a discriminated union over `node_type` — every node type has a
typed payload (JSONB in Postgres).
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .common import (
    Ambiguity,
    AsrResult,
    BilingualText,
    Entities,
    QualityCheck,
    UncertaintyRecord,
    new_ulid,
)
from .enums import (
    CaseStatus,
    Channel,
    ContradictionResolution,
    DecisionStatus,
    EscalationLevel,
    EscalationStatus,
    EvidenceStatus,
    HypothesisStatus,
    Intent,
    InterventionStatus,
    Modality,
    NodeStatus,
    NodeType,
    ObservationState,
    ObservationType,
    OutcomeResult,
    PrescriptionStatus,
    RetrievalMethod,
    RuleResult,
    ScientistAction,
)

# ---------------------------------------------------------------------------
# Payload models (one per node type)
# ---------------------------------------------------------------------------


class InputPayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    node_type: Literal[NodeType.INPUT] = NodeType.INPUT
    modality: Modality
    raw_ref: str | None = Field(
        default=None, description="Media ULID for audio/image; raw string for text/touch"
    )
    asr: AsrResult | None = Field(
        default=None,
        validate_default=True,
        description="Present when modality == voice",
    )
    quality: QualityCheck | None = Field(
        default=None, description="Present for picture/audio inputs"
    )

    @field_validator("asr")
    @classmethod
    def _asr_requires_voice(cls, v: AsrResult | None, info) -> AsrResult | None:
        modality = info.data.get("modality")
        if modality == Modality.VOICE and v is None:
            raise ValueError("voice input requires an asr result")
        return v


class InterpretationPayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    node_type: Literal[NodeType.INTERPRETATION] = NodeType.INTERPRETATION
    transcript: str | None = Field(default=None, description="Original — immutable")
    normalized_query: str | None = None
    entities: Entities = Field(default_factory=Entities)
    ambiguity: Ambiguity | None = None
    uncertainty_record: UncertaintyRecord | None = None


class CorrectionPayload(BaseModel):
    """InterpretationCorrection (source §37.2). Original interpretation is never
    overwritten — the correction references it."""

    model_config = ConfigDict(frozen=True)

    node_type: Literal[NodeType.CORRECTION] = NodeType.CORRECTION
    input_id: str
    original_interpretation_ref: str
    corrected_interpretation: str
    corrected_by: Literal["farmer", "scientist", "system-confirmed"]
    correction_reason: str | None = None
    confidence_before: float | None = Field(default=None, ge=0.0, le=1.0)
    confidence_after: float | None = Field(default=None, ge=0.0, le=1.0)
    evidence_refs: list[str] = Field(default_factory=list)


class ClassifierResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    model_id: str
    class_name: str
    probability: float = Field(ge=0.0, le=1.0)


class ObservationPayload(BaseModel):
    """Image-derived observation (roadmap §9.4.4). Observations never force a
    diagnosis — weak-signal images yield UNCERTAIN/NOT_VISIBLE."""

    model_config = ConfigDict(frozen=True)

    node_type: Literal[NodeType.OBSERVATION] = NodeType.OBSERVATION
    media_id: str
    observation_type: ObservationType
    state: ObservationState
    classifier: ClassifierResult | None = None
    vlm_notes: str | None = Field(default=None, description="Structured notes from Gemma 3 vision")


class HypothesisPayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    node_type: Literal[NodeType.HYPOTHESIS] = NodeType.HYPOTHESIS
    problem_id: str = Field(description="From KB taxonomy")
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_refs: list[str] = Field(default_factory=list)
    contradicting_refs: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    status: HypothesisStatus = HypothesisStatus.ACTIVE


class DecisionPurpose(BaseModel):
    """Why a question is asked (roadmap §4.2.2)."""

    model_config = ConfigDict(frozen=True)

    resolves: list[str] = Field(default_factory=list, description="Hypothesis node IDs")
    distinguishes: list[str] = Field(default_factory=list, description="e.g. [A, B]")


class QuestionPayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    node_type: Literal[NodeType.QUESTION] = NodeType.QUESTION
    text: BilingualText
    modality: Modality
    decision_purpose: DecisionPurpose
    options: list[str] = Field(default_factory=list, description="Touch quick-reply buttons")
    asked_at: datetime
    answered_at: datetime | None = None


class AnswerPayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    node_type: Literal[NodeType.ANSWER] = NodeType.ANSWER
    question_node_id: str
    value: str
    modality: Modality
    raw_ref: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class RetrievalInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    method: RetrievalMethod
    score: float | None = None
    rank: int | None = None


class EvidencePayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    node_type: Literal[NodeType.EVIDENCE] = NodeType.EVIDENCE
    evidence_ledger_id: str
    retrieval: RetrievalInfo | None = None
    relevance_note: str | None = None


class ContradictionPayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    node_type: Literal[NodeType.CONTRADICTION] = NodeType.CONTRADICTION
    field: str = Field(description="crop | stage | problem | ...")
    existing_value: str
    new_value: str
    detected_by: str = Field(description="e.g. system:contradiction-detector")
    resolution: ContradictionResolution = ContradictionResolution.UNRESOLVED


class Diagnosis(BaseModel):
    model_config = ConfigDict(frozen=True)

    problem_id: str
    confidence: float = Field(ge=0.0, le=1.0)


class InterventionDraft(BaseModel):
    """An intervention proposed by the decision (roadmap §6.1)."""

    model_config = ConfigDict(frozen=True)

    product_id: str
    formulation: str | None = None
    dose: str | None = None
    method: str | None = None
    timing: str | None = None
    phi_days: int | None = Field(default=None, ge=0)
    ppe: list[str] = Field(default_factory=list)


class RuleEvaluation(BaseModel):
    model_config = ConfigDict(frozen=True)

    rule_id: str
    result: RuleResult
    details: str | None = None


class DecisionPayload(BaseModel):
    """Decision node payload (roadmap §6.1). Carries the full version tuple
    components so every decision is auditable."""

    model_config = ConfigDict(frozen=True)

    node_type: Literal[NodeType.DECISION] = NodeType.DECISION
    intent: Intent
    diagnoses: list[Diagnosis] = Field(default_factory=list)
    selected_diagnosis: str | None = None
    interventions: list[InterventionDraft] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    rules_evaluated: list[RuleEvaluation] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    model_version: str
    knowledge_version: str
    rule_version: str
    prompt_policy_version: str
    status: DecisionStatus = DecisionStatus.DRAFT


class DeliveryInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    voice: bool = False
    screen: bool = False
    print_id: str | None = None
    qr_id: str | None = None
    whatsapp_msg_id: str | None = None


class InterventionPayload(BaseModel):
    """Delivered action (roadmap §6.1)."""

    model_config = ConfigDict(frozen=True)

    node_type: Literal[NodeType.INTERVENTION] = NodeType.INTERVENTION
    decision_node_id: str
    delivered_at: datetime | None = None
    delivery: DeliveryInfo = Field(default_factory=DeliveryInfo)
    expected_observation: str | None = None
    followup_due_at: datetime | None = Field(default=None, description="From approved protocol")
    status: InterventionStatus = InterventionStatus.PENDING_APPROVAL


class OutcomeTiming(BaseModel):
    model_config = ConfigDict(frozen=True)

    days_after: int | None = Field(default=None, ge=0)
    weather_context_ref: str | None = None


class OutcomePayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    node_type: Literal[NodeType.OUTCOME] = NodeType.OUTCOME
    intervention_id: str
    reported_at: datetime
    reported_by: Literal["farmer", "worker", "scientist"]
    result: OutcomeResult
    farmer_report: str | None = None
    supporting_media: list[str] = Field(default_factory=list)
    timing: OutcomeTiming | None = None
    verified_by: str | None = None
    failure_class: str | None = None
    escalation_id: str | None = None
    learning_status: Literal["pending", "captured", "rejected"] = "pending"
    expected_result: str | None = None


class EscalationTrigger(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: str
    evidence_refs: list[str] = Field(default_factory=list)


class EscalationPayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    node_type: Literal[NodeType.ESCALATION] = NodeType.ESCALATION
    level: EscalationLevel
    trigger: EscalationTrigger
    status: EscalationStatus = EscalationStatus.OPEN
    assigned_to: str | None = None
    assigned_at: datetime | None = None
    resolved_at: datetime | None = None
    resolution_note: str | None = None
    packet_ref: str | None = Field(default=None, description="Compact case packet for scientist")


class ChangedField(BaseModel):
    model_config = ConfigDict(frozen=True)

    field: str
    original_value: str
    corrected_value: str


class ScientistFeedbackPayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    node_type: Literal[NodeType.SCIENTIST_FEEDBACK] = NodeType.SCIENTIST_FEEDBACK
    decision_node_id: str
    scientist_id: str
    modality: Modality
    action: ScientistAction
    changed_fields: list[ChangedField] = Field(default_factory=list)
    reason: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    reference_media: list[str] = Field(default_factory=list)
    evidence_status: EvidenceStatus = EvidenceStatus.EXPERT_PREFERENCE


class SimilarCaseRefPayload(BaseModel):
    """Reference to a similar validated case (roadmap §6.1; Phase 7)."""

    model_config = ConfigDict(frozen=True)

    node_type: Literal[NodeType.SIMILAR_CASE_REF] = NodeType.SIMILAR_CASE_REF
    similar_case_id: str
    similarity: float = Field(ge=0.0, le=1.0)
    differences: list[str] = Field(
        default_factory=list, description="Always visible — never blind copy"
    )
    outcome: OutcomeResult | None = None
    is_negative_evidence: bool = Field(
        default=False, description="True for failed cases (source §41)"
    )


NodePayload = Annotated[
    (
        InputPayload
        | InterpretationPayload
        | CorrectionPayload
        | ObservationPayload
        | HypothesisPayload
        | QuestionPayload
        | AnswerPayload
        | EvidencePayload
        | ContradictionPayload
        | DecisionPayload
        | InterventionPayload
        | OutcomePayload
        | EscalationPayload
        | ScientistFeedbackPayload
        | SimilarCaseRefPayload
    ),
    Field(discriminator="node_type"),
]


# ---------------------------------------------------------------------------
# CaseNode
# ---------------------------------------------------------------------------

_ALLOWED_STATUS_TRANSITIONS: dict[NodeStatus, set[NodeStatus]] = {
    NodeStatus.ACTIVE: {NodeStatus.SUPERSEDED, NodeStatus.REJECTED},
    NodeStatus.SUPERSEDED: set(),
    NodeStatus.REJECTED: set(),
}


class CaseNode(BaseModel):
    """Append-only CST node (roadmap §6.1).

    Invariant: no UPDATE except status transitions `active -> superseded |
    rejected`. Use `transition_status()` to produce the only legal mutation;
    DB triggers (migration 0002) reject anything else.
    """

    model_config = ConfigDict(frozen=True)

    node_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    case_id: str = Field(min_length=26, max_length=26)
    parent_node_id: str | None = None
    node_type: NodeType
    payload: NodePayload

    created_at: datetime
    created_by: str = Field(description="farmer | system | scientist:<id> | operator")
    source_channel: Channel
    source_modality: Modality

    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    status: NodeStatus = NodeStatus.ACTIVE
    evidence_refs: list[str] = Field(default_factory=list, description="evidence_ledger ULIDs")

    @field_validator("created_by")
    @classmethod
    def _created_by_prefix(cls, v: str) -> str:
        allowed_prefixes = ("farmer", "system", "scientist:", "operator")
        if not v.startswith(allowed_prefixes):
            raise ValueError(
                f"created_by must start with one of {allowed_prefixes}, got {v!r}"
            )
        return v

    @field_validator("payload")
    @classmethod
    def _payload_matches_type(cls, v: NodePayload, info) -> NodePayload:
        node_type = info.data.get("node_type")
        if node_type is not None and v.node_type != node_type:
            raise ValueError(f"payload node_type {v.node_type} != node_type {node_type}")
        return v

    def transition_status(self, new_status: NodeStatus) -> CaseNode:
        """Return a new node with status changed — the only legal mutation.

        Raises ValueError for illegal transitions (append-only invariant).
        """
        if new_status not in _ALLOWED_STATUS_TRANSITIONS[self.status]:
            raise ValueError(
                f"illegal node status transition: {self.status} -> {new_status} "
                "(case nodes are append-only; only active -> superseded|rejected is allowed)"
            )
        return self.model_copy(update={"status": new_status})


class CaseState(BaseModel):
    """Current derived state of a case (roadmap §4.2.2 state machine)."""

    model_config = ConfigDict(frozen=True)

    status: CaseStatus
    active_hypotheses: list[str] = Field(default_factory=list, description="node IDs")
    pending_questions: list[str] = Field(default_factory=list, description="node IDs")
    open_contradictions: list[str] = Field(default_factory=list, description="node IDs")
    decision_status: DecisionStatus | None = None
    prescription_status: PrescriptionStatus | None = None
