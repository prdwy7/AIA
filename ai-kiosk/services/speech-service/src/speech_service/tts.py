"""TTS synthesis chain: Piper Telugu → BHASHINI TTS → text-only (docs/05 §2).

Invariant: TTS text is generated from the **locked output object**, never from
raw LLM text. The chain therefore takes `locked_text` as its input and the
caller is responsible for passing the locked advisory/prescription text.

The screen always shows the full answer, so text-only is a valid terminal
state — the farmer is never left without information.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import httpx


@runtime_checkable
class TtsEngine(Protocol):
    """A single TTS backend."""

    name: str

    def available(self) -> bool: ...

    def synthesize(self, text: str) -> bytes:
        """Return WAV bytes. Raises TtsError on failure."""
        ...


class TtsError(RuntimeError):
    """Raised when a TTS engine fails."""


@dataclass(frozen=True)
class TtsOutcome:
    """Result of the TTS chain.

    `audio` is None only when every engine failed — in that case the UI shows
    `text` (the full locked answer) on screen.
    """

    text: str
    audio: bytes | None
    engine: str | None
    notes: list[str]


class PiperEngine:
    """Offline Telugu TTS (default, sub-second on CPU)."""

    name: str = "piper"

    def __init__(self, voice_path: str | None = None) -> None:
        self._voice_path = voice_path or os.environ.get("PIPER_VOICE_PATH", "")
        self._model = None  # lazy

    def available(self) -> bool:
        try:
            import piper  # noqa: F401

            return True
        except ImportError:
            return False

    def synthesize(self, text: str) -> bytes:
        if not self.available():
            raise TtsError("piper-tts not installed")
        try:
            import io

            import piper

            if self._model is None:
                if not self._voice_path:
                    raise TtsError("PIPER_VOICE_PATH not configured")
                self._model = piper.PiperVoice(self._voice_path)
            buf = io.BytesIO()
            self._model.synthesize(text, buf)
            return buf.getvalue()
        except TtsError:
            raise
        except Exception as exc:
            raise TtsError(f"piper synthesis failed: {exc}") from exc


class BhashiniTtsEngine:
    """Online Telugu TTS (higher quality)."""

    name: str = "bhashini-tts"

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        timeout_s: float = 20.0,
    ) -> None:
        self._api_url = api_url or os.environ.get("BHASHINI_TTS_URL", "")
        self._api_key = api_key or os.environ.get("BHASHINI_API_KEY", "")
        self._timeout_s = timeout_s

    def available(self) -> bool:
        return bool(self._api_url and self._api_key)

    def synthesize(self, text: str) -> bytes:
        if not self.available():
            raise TtsError("BHASHINI TTS not configured")
        try:
            resp = httpx.post(
                self._api_url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"text": text, "language": "te"},
                timeout=self._timeout_s,
            )
            resp.raise_for_status()
            return resp.content
        except Exception as exc:
            raise TtsError(f"bhashini tts failed: {exc}") from exc


class TtsChain:
    """Piper → BHASHINI → text-only."""

    def __init__(self, piper: TtsEngine, bhashini: TtsEngine, online: bool = False) -> None:
        self._piper = piper
        self._bhashini = bhashini
        self._online = online

    def synthesize(self, locked_text: str) -> TtsOutcome:
        notes: list[str] = []
        if self._piper.available():
            try:
                return TtsOutcome(
                    text=locked_text,
                    audio=self._piper.synthesize(locked_text),
                    engine=self._piper.name,
                    notes=notes,
                )
            except TtsError as exc:
                notes.append(f"piper failed: {exc}")
        if self._online and self._bhashini.available():
            try:
                return TtsOutcome(
                    text=locked_text,
                    audio=self._bhashini.synthesize(locked_text),
                    engine=self._bhashini.name,
                    notes=notes,
                )
            except TtsError as exc:
                notes.append(f"bhashini-tts failed: {exc}")
        # Text-only fallback: the screen always shows the full answer.
        notes.append("text-only fallback (screen shows full answer)")
        return TtsOutcome(text=locked_text, audio=None, engine=None, notes=notes)
