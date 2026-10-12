"""Append-only audit log (roadmap §6.7, §14.8).

7-year retention, immutable: DB triggers reject UPDATE/DELETE (migration 0005).
Every entry records who/what/when/version.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .common import new_ulid


class AuditEntry(BaseModel):
    """One immutable audit record."""

    model_config = ConfigDict(frozen=True)

    audit_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    actor: str = Field(description="user ID, device ID, or system component")
    actor_role: str | None = None
    action: str = Field(description="e.g. case.create, prescription.lock, release.promote")
    entity_type: str = Field(description="e.g. case, prescription, kb_entry, rule")
    entity_id: str
    version_tuple: dict | None = Field(
        default=None, description="Version tuple in force at the time of the action"
    )
    detail: dict = Field(default_factory=dict)
    created_at: datetime
