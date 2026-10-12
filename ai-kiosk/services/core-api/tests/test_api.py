"""core-api contract tests (docs/04 §1, §7, §8)."""

from __future__ import annotations

import pytest
from core_api.app import create_app
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    with TestClient(create_app()) as c:  # context manager runs the lifespan
        yield c


def _asr() -> dict:
    return {
        "model_id": "whisper-large-v3-vaani-telugu",
        "version": "1.0.0",
        "engine": "vaani-whisper",
        "confidence": 0.87,
        "duration_ms": 2100,
        "transcript": "కొత్త పైపై పసుపు రంగు మచ్చలు",
        "entity_candidates": ["cotton"],
    }


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["service"] == "core-api"
    assert body["uptime_s"] >= 0


def test_ready(client: TestClient):
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["ready"] is True


def test_session_requires_consent(client: TestClient):
    r = client.post("/v1/session", json={"channel": "kiosk", "consent_ack": False})
    assert r.status_code == 403
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["error_code"] == "CONSENT_REQUIRED"


def test_session_creates_case(client: TestClient):
    r = client.post(
        "/v1/session",
        json={"channel": "kiosk", "kiosk_id": "kiosk-1", "language": "te", "consent_ack": True},
    )
    assert r.status_code == 201
    body = r.json()
    assert len(body["session_id"]) == 26  # ULID
    assert len(body["case_id"]) == 26
    assert body["short_code"].startswith("BNV-")


def test_case_and_tree_empty(client: TestClient):
    r = client.post(
        "/v1/cases",
        json={"channel": "kiosk", "language": "te", "consent_ack": True},
    )
    assert r.status_code == 201
    case_id = r.json()["case_id"]

    r = client.get(f"/v1/cases/{case_id}/tree")
    assert r.status_code == 200
    assert r.json()["nodes"] == []
    assert r.json()["state"] == "open"


def test_tree_unknown_case_is_problem_404(client: TestClient):
    r = client.get("/v1/cases/01J9ZKQXV8C4M2N3P5R7T9WXY0/tree")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/problem+json")


def test_voice_input_requires_asr(client: TestClient):
    case_id = client.post(
        "/v1/cases", json={"channel": "kiosk", "consent_ack": True}
    ).json()["case_id"]
    r = client.post(
        f"/v1/cases/{case_id}/inputs",
        json={"modality": "voice", "media_ref": "01J9ZKQXV8C4M2N3P5R7T9WXY2"},
    )
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/problem+json")


def test_voice_input_with_asr_appends_node(client: TestClient):
    case_id = client.post(
        "/v1/cases", json={"channel": "kiosk", "consent_ack": True}
    ).json()["case_id"]
    r = client.post(
        f"/v1/cases/{case_id}/inputs",
        json={"modality": "voice", "media_ref": "01J9ZKQXV8C4M2N3P5R7T9WXY2", "asr_result": _asr()},
    )
    assert r.status_code == 201
    node_id = r.json()["input_node_id"]
    assert len(node_id) == 26

    tree = client.get(f"/v1/cases/{case_id}/tree").json()
    assert len(tree["nodes"]) == 1
    assert tree["nodes"][0]["payload"]["modality"] == "voice"
    assert tree["nodes"][0]["payload"]["asr"]["engine"] == "vaani-whisper"


def test_touch_input_confidence_is_one(client: TestClient):
    case_id = client.post(
        "/v1/cases", json={"channel": "kiosk", "consent_ack": True}
    ).json()["case_id"]
    r = client.post(
        f"/v1/cases/{case_id}/inputs",
        json={"modality": "touch", "payload": "crop=cotton"},
    )
    assert r.status_code == 201
    tree = client.get(f"/v1/cases/{case_id}/tree").json()
    assert tree["nodes"][0]["confidence"] == 1.0


def test_mixed_modalities_in_one_case(client: TestClient):
    case_id = client.post(
        "/v1/cases", json={"channel": "kiosk", "consent_ack": True}
    ).json()["case_id"]
    client.post(
        f"/v1/cases/{case_id}/inputs",
        json={"modality": "voice", "media_ref": "m1", "asr_result": _asr()},
    )
    client.post(
        f"/v1/cases/{case_id}/inputs",
        json={"modality": "text", "payload": "పత్తలపై పసుపు మచ్చలు"},
    )
    client.post(
        f"/v1/cases/{case_id}/inputs",
        json={"modality": "picture", "media_ref": "m2"},
    )
    tree = client.get(f"/v1/cases/{case_id}/tree").json()
    modalities = [n["payload"]["modality"] for n in tree["nodes"]]
    assert modalities == ["voice", "text", "picture"]


def test_inputs_are_append_only(client: TestClient):
    """There is no update/delete endpoint; the store only allows status
    transitions (active -> superseded | rejected)."""
    from canonical_schema import NodeStatus

    case_id = client.post(
        "/v1/cases", json={"channel": "kiosk", "consent_ack": True}
    ).json()["case_id"]
    node_id = client.post(
        f"/v1/cases/{case_id}/inputs",
        json={"modality": "text", "payload": "hello"},
    ).json()["input_node_id"]

    store = client.app.state.store
    updated = store.transition_node_status(case_id, node_id, NodeStatus.SUPERSEDED)
    assert updated.status == NodeStatus.SUPERSEDED

    # A second transition is illegal (superseded is terminal).
    with pytest.raises(ValueError):
        store.transition_node_status(case_id, node_id, NodeStatus.REJECTED)
