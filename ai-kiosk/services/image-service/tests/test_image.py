"""image-service tests: quality, observations, classifier guard, media sets, API.

Test images are generated with Pillow (no fixture files needed):
- "good": random noise (sharp, mid-brightness, large enough)
- "small": 100x100 noise
- "dark": solid near-black
- "blurry": smooth horizontal gradient
- "overexposed": solid near-white
"""

from __future__ import annotations

import base64
import io
import json
import math
import random

import pytest
from fastapi.testclient import TestClient
from image_service.app import create_app
from image_service.classifier import Classification, MockClassifier, classify_with_guard
from image_service.media_set import MediaSet, MediaSetManager
from image_service.observations import (
    MockExtractor,
    Observation,
    _parse_observations,
    candidate_hypotheses,
)
from image_service.quality import check_image_quality
from PIL import Image

# ---------------------------------------------------------------------------
# Image fixtures
# ---------------------------------------------------------------------------


def _to_png(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _noise_image(w: int = 640, h: int = 480, seed: int = 42) -> bytes:
    random.seed(seed)
    img = Image.new("RGB", (w, h))
    img.putdata(
        [
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            for _ in range(w * h)
        ]
    )
    return _to_png(img)


def _sine_image(w: int = 640, h: int = 480) -> bytes:
    """Smooth low-frequency pattern — what an out-of-focus photo looks like
    (near-zero Laplacian variance)."""
    img = Image.new("RGB", (w, h))
    img.putdata(
        [(int(127 + 64 * math.sin(2 * math.pi * x / 128)),) * 3 for x in range(w) for _ in range(h)]
    )
    return _to_png(img)


def _solid_image(rgb: tuple[int, int, int], w: int = 640, h: int = 480) -> bytes:
    return _to_png(Image.new("RGB", (w, h), rgb))


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


GOOD = _noise_image()
SMALL = _noise_image(100, 100)
DARK = _solid_image((10, 10, 10))
BLURRY = _sine_image()
OVEREXPOSED = _solid_image((250, 250, 250))


# ---------------------------------------------------------------------------
# Quality (deterministic checks)
# ---------------------------------------------------------------------------


def test_good_image_usable():
    q = check_image_quality(GOOD)
    assert q.usable
    assert q.reasons == []
    assert q.retry_instruction is None


def test_small_image_rejected():
    q = check_image_quality(SMALL)
    assert not q.usable
    assert "too_small" in q.reasons


def test_dark_image_rejected():
    q = check_image_quality(DARK)
    assert not q.usable
    assert "too_dark" in q.reasons


def test_blurry_image_rejected():
    q = check_image_quality(BLURRY)
    assert not q.usable
    assert "blurry" in q.reasons


def test_overexposed_image_rejected():
    q = check_image_quality(OVEREXPOSED)
    assert not q.usable
    assert "overexposed" in q.reasons


def test_unreadable_image_rejected():
    q = check_image_quality(b"this is not an image")
    assert not q.usable
    assert "unreadable_image" in q.reasons


def test_retry_instruction_present_when_unusable():
    for bad in (SMALL, DARK, BLURRY, OVEREXPOSED, b"nope"):
        q = check_image_quality(bad)
        assert not q.usable
        assert q.retry_instruction  # bilingual, concrete


# ---------------------------------------------------------------------------
# Observations (VLM parsing, confidence cap, hypothesis mapping)
# ---------------------------------------------------------------------------


def test_vlm_confidence_capped():
    content = json.dumps(
        {
            "observations": [
                {"type": "lesion", "state": "OBSERVED", "notes": "n", "confidence": 0.99}
            ]
        }
    )
    obs = _parse_observations(content)
    assert obs[0].confidence == 0.6  # VLM_CONFIDENCE_CAP


def test_parse_observations_invalid_json():
    obs = _parse_observations("not json at all")
    assert len(obs) == 1
    assert obs[0].state == "UNCERTAIN"


def test_parse_observations_invalid_state_coerced():
    content = json.dumps({"observations": [{"type": "lesion", "state": "BOGUS"}]})
    obs = _parse_observations(content)
    assert obs[0].state == "UNCERTAIN"


def test_candidate_hypotheses_only_observed_or_possible():
    obs = [
        Observation(observation_type="lesion", state="OBSERVED"),
        Observation(observation_type="discoloration", state="POSSIBLE"),
        Observation(observation_type="wilting", state="UNCERTAIN"),
        Observation(observation_type="insect_presence", state="NOT_VISIBLE"),
    ]
    cands = candidate_hypotheses(obs)
    assert cands == ["lesion-unknown", "discoloration-unknown"]


# ---------------------------------------------------------------------------
# Classifier diagnosis guard
# ---------------------------------------------------------------------------


def test_guard_low_confidence_uncertain():
    clf = MockClassifier([Classification("healthy", 0.55), Classification("leaf-disease", 0.30)])
    g = classify_with_guard(GOOD, clf)
    assert g.state == "UNCERTAIN"
    assert "top probability" in (g.reason or "")


def test_guard_small_margin_uncertain():
    clf = MockClassifier([Classification("leaf-disease", 0.70), Classification("mildew", 0.65)])
    g = classify_with_guard(GOOD, clf)
    assert g.state == "UNCERTAIN"
    assert "margin" in (g.reason or "")


def test_guard_clear_classified():
    clf = MockClassifier([Classification("leaf-disease", 0.90), Classification("mildew", 0.05)])
    g = classify_with_guard(GOOD, clf)
    assert g.state == "CLASSIFIED"
    assert g.top.class_name == "leaf-disease"
    assert g.margin == pytest.approx(0.85)


def test_guard_no_classes_uncertain():
    clf = MockClassifier([])
    g = classify_with_guard(GOOD, clf)
    assert g.state == "UNCERTAIN"


# ---------------------------------------------------------------------------
# Media sets (do-not-repeat memory)
# ---------------------------------------------------------------------------


def test_media_set_record_not_missing():
    ms = MediaSet(case_id="c1")
    ms.record("leaf", "m1")
    assert "leaf" not in ms.missing()
    assert "whole_plant" in ms.missing()


def test_media_set_never_rerequests_and_instructions_only_missing():
    ms = MediaSet(case_id="c1")
    ms.record("whole_plant", "m1")
    ms.record("leaf", "m2")
    missing = ms.missing()
    assert "whole_plant" not in missing and "leaf" not in missing
    instructions = ms.instructions()
    assert len(instructions) == len(missing)  # only for missing views


def test_media_set_unknown_view_raises():
    ms = MediaSet(case_id="c1")
    with pytest.raises(ValueError):
        ms.record("aerial", "m1")


def test_media_set_manager_tracks_per_case():
    mgr = MediaSetManager()
    mgr.record("c1", "leaf", "m1")
    assert mgr.get("c1").has("leaf")
    assert not mgr.get("c2").has("leaf")  # separate case, separate set


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    extractor = MockExtractor(
        observations=[
            Observation(
                observation_type="lesion",
                state="OBSERVED",
                notes="brown spot",
                confidence=0.8,
            ),
            Observation(observation_type="wilting", state="UNCERTAIN"),
        ]
    )
    classifier = MockClassifier(
        [Classification("leaf-disease", 0.90), Classification("mildew", 0.05)]
    )
    with TestClient(create_app(extractor=extractor, classifier=classifier)) as c:
        yield c


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "image-service"


def test_ready_reports_dependencies(client: TestClient):
    r = client.get("/ready")
    assert r.status_code == 200
    body = r.json()
    assert body["ready"] is True
    assert body["dependencies"]["vision"] is True
    assert body["dependencies"]["classifier"] is True
    assert body["dependencies"]["media_source"] is False


def test_analyze_good_image_full_pipeline(client: TestClient):
    r = client.post(
        "/v1/media/analyze",
        json={
            "case_id": "case-1",
            "image_b64": _b64(GOOD),
            "view": "leaf",
            "requested_views": ["whole_plant", "leaf", "pest_closeup"],
            "crop": "cotton",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["quality"]["usable"] is True
    assert body["observations"][0]["state"] == "OBSERVED"
    assert body["observations"][0]["confidence"] == 0.6  # capped
    # only OBSERVED/POSSIBLE feed hypotheses
    assert [h["hypothesis"] for h in body["candidate_hypotheses"]] == ["lesion-unknown"]
    assert body["classification"]["state"] == "CLASSIFIED"
    # leaf recorded → not missing
    assert body["missing_views"] == ["whole_plant", "pest_closeup"]
    assert len(body["missing_view_instructions"]) == 2


def test_analyze_unusable_image_skips_vision_and_records_nothing(client: TestClient):
    r = client.post(
        "/v1/media/analyze",
        json={"case_id": "case-2", "image_b64": _b64(DARK), "view": "leaf"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["quality"]["usable"] is False
    assert "too_dark" in body["quality"]["reasons"]
    assert body["quality"]["retry_instruction"]
    assert body["observations"] == []
    assert body["classification"] is None
    # bad photo is not "received" → leaf still missing
    assert "leaf" in body["missing_views"]


def test_analyze_vision_down_degrades_gracefully():
    with TestClient(
        create_app(
            extractor=MockExtractor(available=False), classifier=MockClassifier(available=False)
        )
    ) as c:
        r = c.post(
            "/v1/media/analyze",
            json={"case_id": "case-3", "image_b64": _b64(GOOD), "view": "leaf"},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["quality"]["usable"] is True
    assert body["observations"] == []
    assert body["classification"] is None


def test_analyze_requires_image(client: TestClient):
    r = client.post("/v1/media/analyze", json={"case_id": "case-4"})
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/problem+json")


def test_analyze_media_ref_without_source_503(client: TestClient):
    r = client.post(
        "/v1/media/analyze",
        json={"case_id": "case-5", "media_ref": "cases/case-5/photo1.jpg"},
    )
    assert r.status_code == 503
    assert r.headers["content-type"].startswith("application/problem+json")


def test_analyze_unknown_view_422(client: TestClient):
    r = client.post(
        "/v1/media/analyze",
        json={"case_id": "case-6", "image_b64": _b64(GOOD), "view": "aerial"},
    )
    assert r.status_code == 422


def test_media_set_flow_never_rerequests_across_requests(client: TestClient):
    # First photo: leaf.
    r1 = client.post(
        "/v1/media/analyze",
        json={"case_id": "case-7", "image_b64": _b64(GOOD), "view": "leaf"},
    ).json()
    assert "leaf" not in r1["missing_views"]
    # Second photo: whole_plant.
    r2 = client.post(
        "/v1/media/analyze",
        json={"case_id": "case-7", "image_b64": _b64(GOOD), "view": "whole_plant"},
    ).json()
    assert "leaf" not in r2["missing_views"]  # never re-requested
    assert "whole_plant" not in r2["missing_views"]
    assert r2["missing_views"] == ["pest_closeup"]
