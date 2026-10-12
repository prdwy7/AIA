"""Structured visual observations via Gemma 3 12B vision (roadmap §9.4.4).

The VLM is an **observation extractor + hypothesis generator** — it never
produces a final diagnosis. Observations carry an explicit state:

    OBSERVED | POSSIBLE | UNCERTAIN | CONTRADICTORY | NOT_VISIBLE

A weak visual signal is never converted into a high-confidence diagnosis
merely because an image exists.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import httpx

OBSERVATION_TYPES = ("lesion", "discoloration", "insect_presence", "distortion", "wilting", "other")
OBSERVATION_STATES = ("OBSERVED", "POSSIBLE", "UNCERTAIN", "CONTRADICTORY", "NOT_VISIBLE")

# Cap on observation confidence from the VLM alone — diagnosis confidence
# comes from the classifier + rules, not from the VLM.
VLM_CONFIDENCE_CAP = 0.6


@dataclass(frozen=True)
class Observation:
    observation_type: str  # OBSERVATION_TYPES
    state: str  # OBSERVATION_STATES
    notes: str | None = None
    confidence: float | None = None  # capped at VLM_CONFIDENCE_CAP


@dataclass(frozen=True)
class ImageContext:
    """Case context passed to the extractor (crop/stage known so far)."""

    crop: str | None = None
    stage: str | None = None
    region: str | None = None


@runtime_checkable
class ObservationExtractor(Protocol):
    def available(self) -> bool: ...

    def extract(self, image_bytes: bytes, context: ImageContext) -> list[Observation]: ...


class GemmaVisionExtractor:
    """Gemma 3 12B vision via Ollama (lazy, GPU-bound)."""

    def __init__(
        self,
        model: str = "gemma3:12b",
        base_url: str = "http://localhost:11434",
        timeout_s: float = 120.0,
    ) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout_s = timeout_s

    def available(self) -> bool:
        try:
            resp = httpx.get(f"{self._base_url}/api/tags", timeout=3.0)
            resp.raise_for_status()
            models = [m.get("name", "") for m in resp.json().get("models", [])]
            return any(m.startswith(self._model.split(":")[0]) for m in models)
        except Exception:
            return False

    def extract(self, image_bytes: bytes, context: ImageContext) -> list[Observation]:
        if not self.available():
            raise RuntimeError("Ollama / Gemma 3 vision not available")
        prompt = _build_prompt(context)
        resp = httpx.post(
            f"{self._base_url}/api/chat",
            json={
                "model": self._model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [base64.b64encode(image_bytes).decode()],
                    }
                ],
                "stream": False,
                "format": "json",
            },
            timeout=self._timeout_s,
        )
        resp.raise_for_status()
        content = resp.json()["message"]["content"]
        return _parse_observations(content)


def _build_prompt(context: ImageContext) -> str:
    crop = context.crop or "unknown"
    stage = context.stage or "unknown"
    return (
        "You are an agricultural image observation extractor. Describe ONLY what is "
        f"visible in this crop image (crop: {crop}, stage: {stage}). Do NOT diagnose. "
        "Return JSON: {\"observations\": [{\"type\": one of "
        + ", ".join(OBSERVATION_TYPES)
        + ", \"state\": one of "
        + ", ".join(OBSERVATION_STATES)
        + ", \"notes\": string, \"confidence\": 0..1}]}. "
        "If nothing relevant is visible, return a single NOT_VISIBLE observation."
    )


def _parse_observations(content: str) -> list[Observation]:
    try:
        data = json.loads(content)
        raw = data.get("observations", [])
    except (json.JSONDecodeError, AttributeError):
        return [
            Observation(observation_type="other", state="UNCERTAIN", notes="unparseable VLM output")
        ]
    out: list[Observation] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        otype = str(item.get("type", "other"))
        state = str(item.get("state", "UNCERTAIN")).upper()
        if otype not in OBSERVATION_TYPES:
            otype = "other"
        if state not in OBSERVATION_STATES:
            state = "UNCERTAIN"
        conf = item.get("confidence")
        conf = max(0.0, min(VLM_CONFIDENCE_CAP, float(conf))) if conf is not None else None
        out.append(
            Observation(
                observation_type=otype,
                state=state,
                notes=str(item.get("notes", "")) or None,
                confidence=conf,
            )
        )
    return out or [Observation(observation_type="other", state="NOT_VISIBLE")]


class MockExtractor:
    """Test double with canned observations."""

    def __init__(
        self, observations: list[Observation] | None = None, available: bool = True
    ) -> None:
        self._observations = observations or []
        self._available = available

    def available(self) -> bool:
        return self._available

    def extract(self, image_bytes: bytes, context: ImageContext) -> list[Observation]:
        return list(self._observations)


def candidate_hypotheses(observations: list[Observation]) -> list[str]:
    """Map observations to candidate hypothesis problem IDs (weak signal).

    These are candidates for the hypothesis branch — never a diagnosis.
    """
    mapping = {
        "lesion": "lesion-unknown",
        "discoloration": "discoloration-unknown",
        "insect_presence": "insect-unknown",
        "distortion": "distortion-unknown",
        "wilting": "wilting-unknown",
    }
    seen: list[str] = []
    for obs in observations:
        if obs.state in ("OBSERVED", "POSSIBLE"):
            cand = mapping.get(obs.observation_type)
            if cand and cand not in seen:
                seen.append(cand)
    return seen
