"""Case header model (roadmap §6.1).

A case is the durable, channel-agnostic unit of work. It is created on first
contact (any channel, any modality) and carries the full context: channel,
farmer pseudonym, location, crop, media, weather/soil snapshots, previous
interventions and the version tuple in force.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .common import Location, VersionTuple, new_ulid
from .enums import CaseStatus, Channel, Language


class PreviousIntervention(BaseModel):
    """A previously applied intervention, as reported by the farmer (roadmap §6.1)."""

    model_config = ConfigDict(frozen=True)

    product: str | None = None
    formulation: str | None = None
    dose: str | None = None
    method: str | None = None
    applied_at: datetime | None = None
    days_ago: int | None = Field(default=None, ge=0)
    observed_effect: str | None = None
    source: Literal["farmer_report", "prior_case"] = "farmer_report"


class Case(BaseModel):
    """Case header (roadmap §6.1)."""

    model_config = ConfigDict(frozen=True)

    case_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    short_code: str = Field(description='Human-readable code, e.g. "BNV-4F7K2"')
    qr_payload: str = Field(description="QR payload: case_id + verification URL")

    channel: Channel
    channel_ref: str | None = Field(
        default=None, description="Channel-native reference (e.g., WhatsApp thread ID)"
    )

    farmer_ref: str | None = Field(
        default=None, description="Pseudonymous farmer reference — never a name (DPDP)"
    )
    consent_ref: str | None = Field(default=None, description="Consent record reference")

    kiosk_id: str | None = None
    location: Location | None = None
    language: Language = Language.TE

    crop: str | None = None
    variety: str | None = None
    stage: str | None = None
    severity: str | None = Field(default=None, description="Nullable until known")

    media_refs: list[str] = Field(default_factory=list, description="Media ULIDs")

    weather_snapshot_id: str | None = None
    soil_snapshot_id: str | None = None

    previous_interventions: list[PreviousIntervention] = Field(default_factory=list)

    version_tuple: VersionTuple

    status: CaseStatus = CaseStatus.OPEN
    created_at: datetime
    updated_at: datetime | None = None
    closed_at: datetime | None = None
    close_reason: str | None = None

    @field_validator("short_code")
    @classmethod
    def _short_code_format(cls, v: str) -> str:
        if not (3 <= len(v) <= 16):
            raise ValueError("short_code must be 3-16 chars")
        return v.upper()
