"""Knowledge base, evidence ledger and lexicon (roadmap §6.3, §6.4)."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from .common import BilingualText, new_ulid
from .enums import KEntryStatus, KEntryType, SourceType


class EvidenceSource(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: SourceType
    name: str
    url: str | None = None
    version: str | None = None
    published_date: date | None = None
    retrieved_date: date | None = None


class EvidenceScope(BaseModel):
    model_config = ConfigDict(frozen=True)

    crops: list[str] = Field(default_factory=list)
    regions: list[str] = Field(default_factory=list)
    seasons: list[str] = Field(default_factory=list)


class EvidenceLedger(BaseModel):
    """Claims → sources (roadmap §6.3). Authority level 1..7 per roadmap §4.6.1."""

    model_config = ConfigDict(frozen=True)

    evidence_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    claim: str = Field(description="Normalized statement")
    source: EvidenceSource
    authority_level: int = Field(ge=1, le=7)
    effective_from: date | None = None
    effective_to: date | None = None
    superseded_by: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    scope: EvidenceScope = Field(default_factory=EvidenceScope)
    verified_by: str | None = Field(default=None, description="scientist_id")
    verified_at: datetime | None = None


class KEntryTestCase(BaseModel):
    model_config = ConfigDict(frozen=True)

    question: BilingualText
    expected_answer_points: list[str] = Field(default_factory=list)
    risk_tier: str | None = None


class KEntryScope(BaseModel):
    model_config = ConfigDict(frozen=True)

    crops: list[str] = Field(default_factory=list)
    stages: list[str] = Field(default_factory=list)
    regions: list[str] = Field(default_factory=list)
    seasons: list[str] = Field(default_factory=list)


class KBEntry(BaseModel):
    """Structured knowledge entry (roadmap §6.4)."""

    model_config = ConfigDict(frozen=True)

    entry_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    kb_version: str
    entry_type: KEntryType
    title: BilingualText
    summary: BilingualText
    structured_fields: dict = Field(
        default_factory=dict,
        description=(
            "JSONB per type, e.g. product {active_ingredient, formulation, dose_range, "
            "method, phi_days, ppe[], target_pests[], crop_restrictions[]}"
        ),
    )
    scope: KEntryScope = Field(default_factory=KEntryScope)
    authority_level: int = Field(ge=1, le=7)
    source_ref: str | None = Field(default=None, description="evidence_ledger ULID")
    effective_from: date | None = None
    effective_to: date | None = None
    status: KEntryStatus = KEntryStatus.ACTIVE
    superseded_by: str | None = None
    test_cases: list[KEntryTestCase] = Field(default_factory=list)
    created_by: str
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None


class PassageMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    crop: str | None = None
    stage: str | None = None
    region: str | None = None
    authority_level: int | None = Field(default=None, ge=1, le=7)
    effective_from: date | None = None


class KBPassage(BaseModel):
    """Retrieval passage (roadmap §6.4). Dense embedding: BGE-M3 (1024-d);
    sparse weights: BGE-M3 lexical."""

    model_config = ConfigDict(frozen=True)

    passage_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    entry_id: str
    kb_version: str
    text: BilingualText
    chunk_index: int = Field(ge=0)
    embedding_dense: list[float] | None = Field(
        default=None, description="1024-d BGE-M3 dense vector"
    )
    sparse_weights: dict[str, float] | None = Field(
        default=None, description="BGE-M3 lexical sparse weights"
    )
    metadata: PassageMetadata = Field(default_factory=PassageMetadata)


class LexiconEntry(BaseModel):
    """Local terminology mapping (roadmap §6.5 lexicon)."""

    model_config = ConfigDict(frozen=True)

    term: str = Field(description="Local/dialectal term as spoken or typed")
    canonical: str = Field(description="Canonical term (Telugu script preferred)")
    crop: str | None = None
    region: str | None = None
    status: str = Field(default="active", description="active | retired")
    source: str | None = Field(default=None, description="e.g. farmer correction, KB")
    created_at: datetime
