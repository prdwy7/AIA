"""Media records (roadmap §6.1 media table, §9.4.6 image privacy).

Media is stored in MinIO with case references; edge cache is LUKS-encrypted.
Faces are blurred by default in stored copies; the original is retained only
if a scientist explicitly requests it for diagnosis, with recorded consent.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .common import QualityCheck, new_ulid
from .enums import FaceBlurStatus, MediaKind


class Media(BaseModel):
    """Audio/image metadata + MinIO reference (roadmap §6.1)."""

    model_config = ConfigDict(frozen=True)

    media_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    case_id: str = Field(min_length=26, max_length=26)
    kind: MediaKind
    minio_key: str
    content_hash: str = Field(description="SHA-256 — media dedup key for sync")
    size_bytes: int = Field(ge=0)
    mime_type: str | None = None
    duration_ms: int | None = Field(default=None, ge=0, description="Audio only")
    width: int | None = Field(default=None, ge=0, description="Image only")
    height: int | None = Field(default=None, ge=0, description="Image only")

    quality: QualityCheck | None = None
    face_blur: FaceBlurStatus = FaceBlurStatus.BLURRED
    blur_original_requested_by: str | None = Field(
        default=None, description="Scientist who requested the unblurred original"
    )
    blur_consent_ref: str | None = None

    flagged_for_learning: bool = False
    retention_until: datetime | None = Field(
        default=None, description="1 year default; 5 years if flagged with consent"
    )
    created_at: datetime
