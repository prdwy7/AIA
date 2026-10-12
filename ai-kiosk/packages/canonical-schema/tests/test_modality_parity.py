"""Modality parity — Phase 1 exit criterion (roadmap §10.2).

Text/voice/picture (and touch) must be representable **identically** in the
canonical schema: the same case built from each modality yields the same case
structure, differing only in the modality-tagged input node.
"""

from __future__ import annotations

from datetime import UTC, datetime

from canonical_schema import (
    AsrResult,
    Case,
    CaseNode,
    Channel,
    Entities,
    Entity,
    InputPayload,
    Language,
    Location,
    Modality,
    NodeStatus,
    NodeType,
    QualityCheck,
    VersionTuple,
)
from canonical_schema.enums import AsrEngine

NOW = datetime(2026, 10, 1, 10, 0, 0, tzinfo=UTC)
VT = VersionTuple(
    model="gemma-3-12b:0.34.4",
    knowledge="1.0.0",
    rules="1.0.0",
    prompt_policy="1.0.0",
    speech="1.0.0",
    schema="1.0.0",
)


def _case() -> Case:
    return Case(
        case_id="01J9ZKQXV8C4M2N3P5R7T9WXY1",
        short_code="BNV-4F7K2",
        qr_payload="https://verify.example/case/01J9ZKQXV8C4M2N3P5R7T9WXY1",
        channel=Channel.KIOSK,
        farmer_ref="FARMER-0001",
        location=Location(state="AP", district="Kurnool", mandal="Yemmiganur"),
        language=Language.TE,
        crop="cotton",
        stage="flowering",
        version_tuple=VT,
        created_at=NOW,
    )


def _voice_node(case: Case) -> CaseNode:
    return CaseNode(
        case_id=case.case_id,
        node_type=NodeType.INPUT,
        payload=InputPayload(
            modality=Modality.VOICE,
            raw_ref="01J9ZKQXV8C4M2N3P5R7T9WXY2",  # media ULID
            asr=AsrResult(
                model_id="ARTPARK-IISc/whisper-large-v3-vaani-telugu",
                version="1.0.0",
                engine=AsrEngine.VAANI_WHISPER,
                confidence=0.87,
                duration_ms=4200,
                transcript="కొత్త పత్తలపై పసుపు రంగు మచ్చలు కనిపిస్తున్నాయి",
            ),
        ),
        created_at=NOW,
        created_by="farmer",
        source_channel=Channel.KIOSK,
        source_modality=Modality.VOICE,
        confidence=0.87,
    )


def _touch_node(case: Case) -> CaseNode:
    return CaseNode(
        case_id=case.case_id,
        node_type=NodeType.INPUT,
        payload=InputPayload(
            modality=Modality.TOUCH,
            raw_ref="picker:cotton;flowering;yellow_spots",
        ),
        created_at=NOW,
        created_by="farmer",
        source_channel=Channel.KIOSK,
        source_modality=Modality.TOUCH,
        confidence=1.0,  # touch confidence = 1.0 by construction
    )


def _text_node(case: Case) -> CaseNode:
    return CaseNode(
        case_id=case.case_id,
        node_type=NodeType.INPUT,
        payload=InputPayload(
            modality=Modality.TEXT,
            raw_ref="కొత్త పత్తలపై పసుపు రంగు మచ్చలు",
        ),
        created_at=NOW,
        created_by="farmer",
        source_channel=Channel.KIOSK,
        source_modality=Modality.TEXT,
    )


def _picture_node(case: Case) -> CaseNode:
    return CaseNode(
        case_id=case.case_id,
        node_type=NodeType.INPUT,
        payload=InputPayload(
            modality=Modality.PICTURE,
            raw_ref="01J9ZKQXV8C4M2N3P5R7T9WXY3",  # media ULID
            quality=QualityCheck(usable=True, reasons=[]),
        ),
        created_at=NOW,
        created_by="farmer",
        source_channel=Channel.KIOSK,
        source_modality=Modality.PICTURE,
    )


def test_same_case_from_each_modality():
    """The same case is representable identically from voice/touch/text/picture."""
    case = _case()
    nodes = [_voice_node(case), _touch_node(case), _text_node(case), _picture_node(case)]

    # All four input nodes attach to the same case with the same structure.
    for node in nodes:
        assert node.case_id == case.case_id
        assert node.node_type == NodeType.INPUT
        assert node.status == NodeStatus.ACTIVE
        assert node.created_by == "farmer"

    # Modalities are first-class and distinct.
    modalities = [n.payload.modality for n in nodes]
    assert modalities == [
        Modality.VOICE,
        Modality.TOUCH,
        Modality.TEXT,
        Modality.PICTURE,
    ]


def test_mixed_modality_case():
    """Acceptance (source §54): voice, text and image can be mixed in one case."""
    case = _case()
    nodes = [_voice_node(case), _text_node(case), _picture_node(case)]
    case_with_media = case.model_copy(
        update={
            "media_refs": [
                n.payload.raw_ref
                for n in nodes
                if n.payload.modality in (Modality.VOICE, Modality.PICTURE)
            ]
        }
    )
    assert len(case_with_media.media_refs) == 2
    # All nodes coexist in the append-only tree.
    assert len({n.node_id for n in nodes}) == 3


def test_voice_input_requires_asr():
    from pydantic import ValidationError

    try:
        InputPayload(modality=Modality.VOICE, raw_ref="media-1")
        raise AssertionError("voice input without asr must fail validation")
    except ValidationError as e:
        assert "asr" in str(e)


def test_touch_confidence_is_one():
    case = _case()
    node = _touch_node(case)
    assert node.confidence == 1.0


def test_interpretation_entities_shared_across_modalities():
    """The interpretation node shape is identical regardless of input modality."""
    from canonical_schema import InterpretationPayload

    payload = InterpretationPayload(
        transcript="కొత్త పత్తలపై పసుపు రంగు మచ్చలు",
        normalized_query="cotton flowering yellow spots new leaves",
        entities=Entities(
            crop=Entity(value="cotton", confidence=0.95, source="lexicon"),
            stage=Entity(value="flowering", confidence=0.9, source="llm"),
            problem=Entity(value="yellow_spots", confidence=0.7, source="llm"),
        ),
    )
    node = CaseNode(
        case_id="01J9ZKQXV8C4M2N3P5R7T9WXY1",
        node_type=NodeType.INTERPRETATION,
        payload=payload,
        created_at=NOW,
        created_by="system",
        source_channel=Channel.KIOSK,
        source_modality=Modality.SYSTEM,
        confidence=0.85,
    )
    assert node.payload.entities.crop.value == "cotton"
    assert node.payload.entities.stage.value == "flowering"
