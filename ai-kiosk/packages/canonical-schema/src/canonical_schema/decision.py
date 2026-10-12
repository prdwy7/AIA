"""Decision deltas (learning objects) and prescriptions (roadmap §6.2, §6.6).

Invariant: the original AI decision is never overwritten; original + corrected
states are both retained for learning and audit.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .common import BilingualText, VersionTuple, new_ulid
from .enums import (
    CorrectionType,
    DeltaApprovalStatus,
    EvidenceStatus,
    LearningChannel,
    PrescriptionStatus,
)


class ChangedFieldDelta(BaseModel):
    model_config = ConfigDict(frozen=True)

    field: str
    old_value: str
    new_value: str


class DecisionDelta(BaseModel):
    """Learning object created from a scientist correction (roadmap §6.2)."""

    model_config = ConfigDict(frozen=True)

    delta_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    decision_node_id: str
    case_id: str
    scientist_id: str
    created_at: datetime

    changed_fields: list[ChangedFieldDelta] = Field(default_factory=list)
    correction_type: CorrectionType
    reason: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    evidence_status: EvidenceStatus = EvidenceStatus.EXPERT_PREFERENCE

    context_snapshot_ref: str = Field(
        description="Full snapshot: case, weather, evidence, rules, versions, original output"
    )
    approval_status: DeltaApprovalStatus = DeltaApprovalStatus.PENDING
    learning_channel: LearningChannel = LearningChannel.NONE
    released_version: str | None = Field(
        default=None, description="Which production version consumed it"
    )


class PrescriptionContent(BaseModel):
    model_config = ConfigDict(frozen=True)

    diagnosis: str
    product: str
    formulation: str | None = None
    dose: str | None = None
    method: str | None = None
    timing: str | None = None
    phi: int | None = Field(default=None, ge=0, description="Pre-harvest interval, days")
    ppe: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    explanation: BilingualText
    safety_notes: str | None = None


class PrescriptionVerification(BaseModel):
    model_config = ConfigDict(frozen=True)

    verified_at: datetime | None = None
    verified_by: str | None = None
    result: str | None = None


class Prescription(BaseModel):
    """Locked prescription (roadmap §6.6). Only created from an approved
    decision; records the version tuple for full traceability."""

    model_config = ConfigDict(frozen=True)

    prescription_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    decision_node_id: str
    case_id: str
    status: PrescriptionStatus = PrescriptionStatus.DRAFT

    content: PrescriptionContent
    version_tuple: VersionTuple
    scientist_id: str | None = None
    approved_at: datetime | None = None
    locked_at: datetime | None = None

    print_id: str | None = None
    qr_payload: str = Field(description="prescription_id + verification URL")
    verification: PrescriptionVerification = Field(default_factory=PrescriptionVerification)
