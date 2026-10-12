"""ASR engine abstractions (docs/05 §2).

An engine is anything that can turn 16 kHz mono WAV bytes into an
`AsrResult`. Concrete engines probe their runtime at `available()` time so
the service degrades gracefully when a runtime (faster-whisper, ONNX,
network) is missing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from canonical_schema import AsrResult


@dataclass(frozen=True)
class AudioInput:
    """Normalized audio: 16 kHz mono WAV (ffmpeg upstream)."""

    data: bytes
    duration_ms: int
    language: str = "te"
    source: str = "kiosk"  # kiosk | whatsapp | web


@dataclass(frozen=True)
class GpuState:
    """GPU availability snapshot (from device-agent / Ollama)."""

    free: bool
    free_vram_gb: float = 0.0
    reason: str | None = None  # e.g. "llm-inference-in-flight"


@runtime_checkable
class ASREngine(Protocol):
    """A single ASR backend."""

    name: str  # "vaani-whisper" | "sravaani" | "bhashini"
    model_id: str
    version: str

    def available(self) -> bool:
        """Whether the engine can serve requests right now."""
        ...

    def transcribe(self, audio: AudioInput) -> AsrResult:
        """Transcribe. Raises EngineError on failure."""
        ...


class EngineError(RuntimeError):
    """Raised when an engine fails to transcribe."""


@dataclass
class TranscriptionOutcome:
    """Result of the ASR chain, including any cross-check.

    `engine_used` is what gets recorded on the Input node (`asr.engine`).
    `confirmation_required` triggers the confirmation gate when the offline
    and online transcripts disagree on a critical entity.
    """

    result: AsrResult
    engine_used: str
    cross_check: AsrResult | None = None
    confirmation_required: bool = False
    candidates: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
