"""BHASHINI ASR — ONLINE cross-check engine (docs/05 §2, priority 3).

Government platform (bhashini.gov.in). Used only when online AND:
(a) the offline transcript confidence < 0.60, or
(b) as a cross-check of a low-confidence transcript.

Adds a network dependency — never the default path.
"""

from __future__ import annotations

import os
import time

import httpx
from canonical_schema import AsrEngine, AsrResult

from speech_service.engines.base import AudioInput, EngineError

MODEL_ID = "bhashini-asr-telugu"
MODEL_VERSION = "api-1"


class BhashiniEngine:
    """Online Telugu ASR (cross-check only)."""

    name: str = "bhashini"
    model_id: str = MODEL_ID
    version: str = MODEL_VERSION

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        timeout_s: float = 15.0,
    ) -> None:
        self._api_url = api_url or os.environ.get("BHASHINI_API_URL", "")
        self._api_key = api_key or os.environ.get("BHASHINI_API_KEY", "")
        self._timeout_s = timeout_s

    def available(self) -> bool:
        return bool(self._api_url and self._api_key)

    def transcribe(self, audio: AudioInput) -> AsrResult:
        if not self.available():
            raise EngineError("BHASHINI API not configured (BHASHINI_API_URL/KEY)")
        start = time.monotonic()
        try:
            resp = httpx.post(
                self._api_url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                files={"audio": ("audio.wav", audio.data, "audio/wav")},
                data={"language": audio.language},
                timeout=self._timeout_s,
            )
            resp.raise_for_status()
            body = resp.json()
            transcript = str(body.get("transcript", "")).strip()
            confidence = float(body.get("confidence", 0.0) or 0.0)
        except Exception as exc:
            raise EngineError(f"bhashini transcription failed: {exc}") from exc
        return AsrResult(
            model_id=self.model_id,
            version=self.version,
            engine=AsrEngine.BHASHINI,
            confidence=max(0.0, min(1.0, confidence)),
            duration_ms=int((time.monotonic() - start) * 1000),
            transcript=transcript,
        )
