"""Append-only invariants (roadmap §6.1).

- Case nodes are frozen: no field mutation.
- The only legal mutation is a status transition `active -> superseded |
  rejected`, via `CaseNode.transition_status()`.
- Illegal transitions raise (mirrors the DB trigger in migration 0002).
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from canonical_schema import (
    CaseNode,
    Channel,
    InputPayload,
    Modality,
    NodeStatus,
    NodeType,
)
from pydantic import ValidationError

NOW = datetime(2026, 10, 1, 10, 0, 0, tzinfo=UTC)


def _node() -> CaseNode:
    return CaseNode(
        case_id="01J9ZKQXV8C4M2N3P5R7T9WXY1",
        node_type=NodeType.INPUT,
        payload=InputPayload(modality=Modality.TEXT, raw_ref="hello"),
        created_at=NOW,
        created_by="farmer",
        source_channel=Channel.KIOSK,
        source_modality=Modality.TEXT,
    )


def test_node_is_frozen():
    node = _node()
    with pytest.raises(ValidationError):
        node.confidence = 0.9  # type: ignore[misc]
    with pytest.raises(ValidationError):
        node.payload = InputPayload(modality=Modality.TEXT, raw_ref="changed")  # type: ignore[assignment]


def test_legal_transition_active_to_superseded():
    node = _node()
    updated = node.transition_status(NodeStatus.SUPERSEDED)
    assert updated.status == NodeStatus.SUPERSEDED
    # Original node unchanged (immutable).
    assert node.status == NodeStatus.ACTIVE
    # Same identity, only status differs.
    assert updated.node_id == node.node_id
    assert updated.created_at == node.created_at


def test_legal_transition_active_to_rejected():
    node = _node()
    updated = node.transition_status(NodeStatus.REJECTED)
    assert updated.status == NodeStatus.REJECTED


def test_illegal_transition_superseded_to_active():
    node = _node().transition_status(NodeStatus.SUPERSEDED)
    with pytest.raises(ValueError, match="illegal node status transition"):
        node.transition_status(NodeStatus.ACTIVE)


def test_illegal_transition_rejected_to_superseded():
    node = _node().transition_status(NodeStatus.REJECTED)
    with pytest.raises(ValueError, match="illegal node status transition"):
        node.transition_status(NodeStatus.SUPERSEDED)


def test_illegal_transition_active_to_active():
    node = _node()
    with pytest.raises(ValueError, match="illegal node status transition"):
        node.transition_status(NodeStatus.ACTIVE)


def test_correction_appends_not_overwrites():
    """Cross-correction invariant: original interpretation is never overwritten;
    a correction node references it (roadmap §6.1, Phase 4 exit)."""
    from canonical_schema import CorrectionPayload, InterpretationPayload

    original = CaseNode(
        case_id="01J9ZKQXV8C4M2N3P5R7T9WXY1",
        node_type=NodeType.INTERPRETATION,
        payload=InterpretationPayload(transcript="cotton yellow spots"),
        created_at=NOW,
        created_by="system",
        source_channel=Channel.KIOSK,
        source_modality=Modality.SYSTEM,
        confidence=0.6,
    )
    correction = CaseNode(
        case_id="01J9ZKQXV8C4M2N3P5R7T9WXY1",
        parent_node_id=original.node_id,
        node_type=NodeType.CORRECTION,
        payload=CorrectionPayload(
            input_id="01J9ZKQXV8C4M2N3P5R7T9WXY2",
            original_interpretation_ref=original.node_id,
            corrected_interpretation="chilli leaf curl",
            corrected_by="farmer",
            confidence_before=0.6,
            confidence_after=0.95,
        ),
        created_at=NOW,
        created_by="farmer",
        source_channel=Channel.KIOSK,
        source_modality=Modality.TEXT,
        confidence=0.95,
    )
    # Both retained; original still active until explicitly superseded.
    assert original.status == NodeStatus.ACTIVE
    assert correction.payload.original_interpretation_ref == original.node_id
    superseded = original.transition_status(NodeStatus.SUPERSEDED)
    assert superseded.status == NodeStatus.SUPERSEDED
    assert original.status == NodeStatus.ACTIVE  # original object untouched


def test_created_by_prefix_validation():
    with pytest.raises(ValidationError):
        CaseNode(
            case_id="01J9ZKQXV8C4M2N3P5R7T9WXY1",
            node_type=NodeType.INPUT,
            payload=InputPayload(modality=Modality.TEXT, raw_ref="hello"),
            created_at=NOW,
            created_by="random-user",
            source_channel=Channel.KIOSK,
            source_modality=Modality.TEXT,
        )
