"""Version tuple completeness (roadmap §4.5, §6.1).

Every decision and prescription must carry a complete version tuple
(model, knowledge, rules, prompt_policy, speech, schema) — no field may be
missing. This is the audit trail that lets any prescription be traced to the
exact model/KB/rule versions that produced it (Phase 15 audit criterion).
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest
from canonical_schema import (
    BilingualText,
    DecisionPayload,
    Intent,
    Prescription,
    PrescriptionContent,
    VersionTuple,
)
from pydantic import ValidationError

NOW = datetime(2026, 10, 1, 10, 0, 0, tzinfo=UTC)


def test_version_tuple_all_six_fields():
    vt = VersionTuple(
        model="gemma-3-12b:0.34.4",
        knowledge="1.0.0",
        rules="1.0.0",
        prompt_policy="1.0.0",
        speech="1.0.0",
        schema="1.0.0",
    )
    assert set(vt.as_dict().keys()) == {
        "model",
        "knowledge",
        "rules",
        "prompt_policy",
        "speech",
        "schema",
    }


def test_version_tuple_is_frozen():
    vt = VersionTuple(
        model="m", knowledge="k", rules="r", prompt_policy="p", speech="s", schema="sc"
    )
    with pytest.raises(FrozenInstanceError):
        vt.model = "other"  # type: ignore[misc]


def test_decision_payload_carries_version_components():
    payload = DecisionPayload(
        intent=Intent.PRESCRIPTION,
        diagnoses=[{"problem_id": "cotton-leaf-curl", "confidence": 0.8}],
        selected_diagnosis="cotton-leaf-curl",
        interventions=[
            {"product_id": "prod-1", "formulation": "50% SP", "dose": "500 g/acre"}
        ],
        evidence_refs=["01J9ZKQXV8C4M2N3P5R7T9WXY9"],
        rules_evaluated=[{"rule_id": "rule-1", "result": "pass"}],
        confidence=0.82,
        model_version="gemma-3-12b:0.34.4",
        knowledge_version="1.0.0",
        rule_version="1.0.0",
        prompt_policy_version="1.0.0",
    )
    assert payload.model_version
    assert payload.knowledge_version
    assert payload.rule_version
    assert payload.prompt_policy_version


def test_prescription_requires_complete_version_tuple():
    content = PrescriptionContent(
        diagnosis="cotton-leaf-curl",
        product="product-x",
        dose="500 g/acre",
        explanation=BilingualText(te="వివరణ", en="Explanation"),
    )
    # A complete tuple is accepted.
    rx = Prescription(
        decision_node_id="01J9ZKQXV8C4M2N3P5R7T9WXY4",
        case_id="01J9ZKQXV8C4M2N3P5R7T9WXY1",
        content=content,
        version_tuple=VersionTuple(
            model="m", knowledge="k", rules="r", prompt_policy="p", speech="s", schema="sc"
        ),
        qr_payload="https://verify.example/rx/01J9ZKQXV8C4M2N3P5R7T9WXY5",
    )
    assert rx.version_tuple.schema == "sc"

    # A partial tuple is rejected — VersionTuple has no optional fields.
    with pytest.raises(TypeError):
        VersionTuple(model="m", knowledge="k", rules="r", prompt_policy="p", speech="s")  # type: ignore[call-arg]

    # ...and the same holds through Pydantic validation (the real ingestion path).
    with pytest.raises(ValidationError):
        Prescription.model_validate(
            {
                "decision_node_id": "01J9ZKQXV8C4M2N3P5R7T9WXY4",
                "case_id": "01J9ZKQXV8C4M2N3P5R7T9WXY1",
                "content": {
                    "diagnosis": "cotton-leaf-curl",
                    "product": "product-x",
                    "explanation": {"te": "వివరణ", "en": "Explanation"},
                },
                "version_tuple": {
                    "model": "m",
                    "knowledge": "k",
                    "rules": "r",
                    "prompt_policy": "p",
                    "speech": "s",
                },
                "qr_payload": "https://verify.example/rx/01J9ZKQXV8C4M2N3P5R7T9WXY5",
            }
        )


def test_prescription_traceability_sample():
    """Phase 15 audit: a prescription traces to model/KB/rule versions."""
    rx = Prescription(
        decision_node_id="01J9ZKQXV8C4M2N3P5R7T9WXY4",
        case_id="01J9ZKQXV8C4M2N3P5R7T9WXY1",
        content=PrescriptionContent(
            diagnosis="d",
            product="p",
            explanation=BilingualText(te="త", en="e"),
        ),
        version_tuple=VersionTuple(
            model="gemma-3-12b:0.34.4",
            knowledge="1.2.0",
            rules="2.0.1",
            prompt_policy="1.0.3",
            speech="1.1.0",
            schema="1.0.0",
        ),
        qr_payload="https://verify.example/rx/x",
    )
    d = rx.version_tuple.as_dict()
    assert d["model"] == "gemma-3-12b:0.34.4"
    assert d["knowledge"] == "1.2.0"
    assert d["rules"] == "2.0.1"
