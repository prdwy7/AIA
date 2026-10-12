"""Version registry (roadmap §6.6).

Every production artifact (model / knowledge / rules / prompt policy / speech /
schema) is content-addressed (SHA-256) and signed (minisign/cosign). The
previous production version is retained ≥ 12 months for one-command rollback
(RTO ≤ 15 min/device).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .common import new_ulid
from .enums import ArtifactClass, ArtifactStatus, Environment


class VersionRegistryEntry(BaseModel):
    """A versioned artifact (roadmap §6.6 version_registry)."""

    model_config = ConfigDict(frozen=True)

    entry_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    artifact_class: ArtifactClass
    version: str = Field(description="semver")
    artifact_ref: str = Field(description="MinIO key")
    sha256: str = Field(min_length=64, max_length=64)
    signature: str | None = Field(default=None, description="minisign/cosign signature")
    status: ArtifactStatus = ArtifactStatus.CANDIDATE
    environment: Environment = Environment.CENTRAL
    promoted_at: datetime | None = None
    promoted_by: str | None = None
    retired_at: datetime | None = None
    retirement_reason: str | None = None
