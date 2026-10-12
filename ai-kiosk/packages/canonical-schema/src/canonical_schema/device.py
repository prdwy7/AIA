"""Device fleet and sync (roadmap §6.7).

Edge devices are stateless w.r.t. production artifacts: they are
re-provisioned from signed bundles. Sync is append-only + idempotent —
conflicts are structurally impossible for case data; media dedups by content
hash.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .common import VersionTuple, new_ulid
from .enums import AckStatus, DeviceStatus, SyncEventType


class DeviceHealth(BaseModel):
    """Latest health snapshot (roadmap §6.7)."""

    model_config = ConfigDict(frozen=True)

    cpu_pct: float | None = Field(default=None, ge=0, le=100)
    mem_pct: float | None = Field(default=None, ge=0, le=100)
    gpu_pct: float | None = Field(default=None, ge=0, le=100)
    disk_pct: float | None = Field(default=None, ge=0, le=100)
    temp_c: float | None = None
    printer_ok: bool = True
    network: str | None = Field(default=None, description="ethernet | wifi | 4g | offline")


class SyncState(BaseModel):
    model_config = ConfigDict(frozen=True)

    last_event_seq: int = Field(default=0, ge=0)
    pending_events: int = Field(default=0, ge=0)
    last_sync_at: datetime | None = None


class Device(BaseModel):
    """Kiosk device record (roadmap §6.7)."""

    model_config = ConfigDict(frozen=True)

    device_id: str = Field(description="kiosk_id")
    name: str
    location: str | None = None
    hardware_profile: str | None = Field(default=None, description="e.g. option-a-4060ti")
    cert_fingerprint: str = Field(description="mTLS device certificate fingerprint")
    status: DeviceStatus = DeviceStatus.OFFLINE
    last_seen_at: datetime | None = None
    active_version_tuple: VersionTuple | None = None
    sync_state: SyncState = Field(default_factory=SyncState)
    health: DeviceHealth | None = None


class SyncEvent(BaseModel):
    """Append-only edge → central event (roadmap §6.7). Idempotent by
    event_id (idempotency_key = event_id)."""

    model_config = ConfigDict(frozen=True)

    event_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    device_id: str
    seq: int = Field(ge=1)
    case_id: str | None = None
    event_type: SyncEventType
    payload: dict = Field(default_factory=dict)
    created_at: datetime
    ack_status: AckStatus = AckStatus.PENDING
    idempotency_key: str = Field(description="= event_id")


class ManifestArtifact(BaseModel):
    model_config = ConfigDict(frozen=True)

    class_name: str
    version: str
    sha256: str = Field(min_length=64, max_length=64)
    signature: str | None = None
    minio_key: str
    size: int = Field(ge=0)


class SyncManifest(BaseModel):
    """Central → edge manifest (roadmap §6.7)."""

    model_config = ConfigDict(frozen=True)

    manifest_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    issued_at: datetime
    device_id: str
    artifacts: list[ManifestArtifact] = Field(default_factory=list)
    applied_state: VersionTuple | None = Field(
        default=None, description="Edge reports back which versions are active"
    )
