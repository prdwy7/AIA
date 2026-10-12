"""Learning candidates and provenance (roadmap §6.6).

Provenance — every learning signal must answer all 11 questions
(roadmap §4.3.3): who provided it? · what did they observe? · when? · through
which channel? · what evidence did they provide? · what did the AI originally
say? · what was corrected? · was it independently verified? · did the farmer
outcome support the correction? · was it approved for learning? · which
production version used it?
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .common import new_ulid
from .enums import CandidateStatus, LearningChannel


class Provenance(BaseModel):
    """The 11-field provenance ledger. Every field is non-null or explicitly
    "N/A" (enforced at ingestion, Phase 11 exit criterion)."""

    model_config = ConfigDict(frozen=True)

    who: str = Field(description="Who provided it (scientist_id / farmer_ref / system)")
    what_observed: str = Field(description="What they observed")
    when: datetime = Field(description="When")
    channel: str = Field(description="Through which channel (kiosk/whatsapp/web/portal)")
    evidence: str = Field(description="What evidence they provided (or N/A)")
    ai_original: str = Field(description="What the AI originally said")
    corrected: str = Field(description="What was corrected (or N/A)")
    independently_verified: str = Field(description="Was it independently verified? (yes/no/N/A)")
    outcome_support: str = Field(
        description="Did the farmer outcome support it? (yes/no/pending/N/A)"
    )
    approved_for_learning: str = Field(description="Was it approved for learning? (yes/no)")
    used_in_version: str = Field(description="Which production version used it (or N/A)")

    @model_validator(mode="after")
    def _no_empty_fields(self) -> Provenance:
        for name in self.model_fields:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"provenance field {name!r} must be a non-empty string")
        return self


class ValidationReport(BaseModel):
    """Learning sandbox pipeline report (source §10):
    data quality → regression → safety → counterexample → holdout."""

    model_config = ConfigDict(frozen=True)

    data_quality: str | None = None
    regression: str | None = None
    safety: str | None = None
    counterexample: str | None = Field(
        default=None, description="Must find zero blocking counterexamples"
    )
    holdout: str | None = None


class LearningCandidate(BaseModel):
    """Governed candidate artifact (roadmap §6.6). Status is always CANDIDATE
    until explicit approval + validation — never PRODUCTION automatically."""

    model_config = ConfigDict(frozen=True)

    candidate_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    channel: LearningChannel
    source_refs: list[str] = Field(
        default_factory=list, description="decision_delta_ids, outcome_ids, case_ids"
    )
    payload: dict = Field(
        description="Proposed KB entry / rule / training example / lexicon mapping"
    )
    status: CandidateStatus = CandidateStatus.DRAFT
    validation_report: ValidationReport | None = None
    provenance: Provenance
    created_at: datetime
    reviewed_by: str | None = None
    decided_at: datetime | None = None
