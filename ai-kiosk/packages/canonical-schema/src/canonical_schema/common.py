"""Shared value objects used across the canonical schema.

Conventions (roadmap §6):
- All IDs are ULIDs (sortable, unique across edge + central).
- All timestamps are UTC (display in Asia/Kolkata is a presentation concern).
- Text fields are bilingual `{te, en}` where the system produces them;
  farmer-provided raw text is kept verbatim in `raw` fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from ulid import ULID

from .enums import AsrEngine, Language


def new_ulid() -> str:
    """Generate a new ULID string (canonical ID format)."""
    return str(ULID())


class BilingualText(BaseModel):
    """Telugu-first bilingual text (user requirement: Telugu-first UX)."""

    model_config = ConfigDict(frozen=True)

    te: str = Field(description="Telugu (script or transliteration as provided)")
    en: str = Field(default="", description="English rendering")

    def display(self, language: Language | str = Language.TE) -> str:
        lang = Language(language)
        if lang in (Language.TE, Language.TE_EN):
            return self.te or self.en
        return self.en or self.te


class Location(BaseModel):
    """Geographic location of a case (roadmap §6.1)."""

    model_config = ConfigDict(frozen=True)

    state: str | None = None
    district: str | None = None
    mandal: str | None = None
    village: str | None = None
    lat: float | None = Field(default=None, ge=-90, le=90)
    lon: float | None = Field(default=None, ge=-180, le=180)
    accuracy_m: float | None = Field(default=None, ge=0, description="GPS accuracy in meters")


@dataclass(frozen=True)
class VersionTuple:
    """The six versioned artifacts that every decision/prescription must record
    (roadmap §4.5). All fields are required — a decision without a complete
    version tuple is invalid.

    A frozen dataclass (not a BaseModel) so the `schema` field does not shadow
    `BaseModel.schema`; Pydantic validates it when nested in models.
    """

    model: str  # LLM/model version (e.g., gemma-3-12b:0.34.4)
    knowledge: str  # KB version (semver)
    rules: str  # Rules bundle version (semver)
    prompt_policy: str  # Prompt policy version (semver)
    speech: str  # Speech (ASR+TTS) bundle version (semver)
    schema: str  # Canonical schema version (semver)

    def as_dict(self) -> dict[str, str]:
        return {
            "model": self.model,
            "knowledge": self.knowledge,
            "rules": self.rules,
            "prompt_policy": self.prompt_policy,
            "speech": self.speech,
            "schema": self.schema,
        }


class Entity(BaseModel):
    """A single extracted entity (roadmap §6.1 interpretation payload)."""

    model_config = ConfigDict(frozen=True)

    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: str = Field(description="Where it came from: asr | lexicon | llm | touch | rule")
    normalized: str | None = Field(
        default=None, description="Canonical form (e.g., lexicon mapping)"
    )


class Entities(BaseModel):
    """Entity bag on an interpretation (roadmap §6.1)."""

    crop: Entity | None = None
    variety: Entity | None = None
    stage: Entity | None = None
    problem: Entity | None = None
    product: Entity | None = None
    dose: Entity | None = None
    location: Entity | None = None
    other: dict[str, Entity] = Field(default_factory=dict)


class Ambiguity(BaseModel):
    """Ambiguity record — candidates the farmer can disambiguate (roadmap §6.1)."""

    model_config = ConfigDict(frozen=True)

    candidates: list[str] = Field(default_factory=list)
    explanation: str | None = None


class UncertaintyRecord(BaseModel):
    """System uncertainty record — "I may have understood this incorrectly"
    (source §37.1)."""

    model_config = ConfigDict(frozen=True)

    confidence: float = Field(ge=0.0, le=1.0)
    why: str
    what_would_resolve: str


class QualityCheck(BaseModel):
    """Deterministic media quality check (roadmap §9.4.4 image; audio)."""

    model_config = ConfigDict(frozen=True)

    usable: bool
    reasons: list[str] = Field(default_factory=list)
    retry_instruction: str | None = Field(
        default=None, description="Concrete retry instruction shown to the farmer"
    )


class AsrResult(BaseModel):
    """ASR output (roadmap §6.1 input payload, voice)."""

    model_config = ConfigDict(frozen=True)

    model_id: str
    version: str
    engine: AsrEngine
    confidence: float = Field(ge=0.0, le=1.0)
    duration_ms: int = Field(ge=0)
    transcript: str = Field(description="Original transcript — immutable once stored")
    entity_candidates: list[str] = Field(
        default_factory=list, description="Low-confidence entity candidates for confirmation"
    )


class Timestamps(BaseModel):
    """UTC timestamps shared by many records."""

    model_config = ConfigDict(frozen=True)

    created_at: datetime
    updated_at: datetime | None = None


class IdRef(BaseModel):
    """Reference to another record by ULID."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=26, max_length=26, description="ULID")
