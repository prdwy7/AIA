"""Deterministic ASR engine selection + fallback chain (docs/05 §2).

Selection logic (deterministic):
1. Utterance ≤ 3 s AND GPU free → SraVaani (fast path, low latency).
2. GPU free → Vaani-Whisper (default quality).
3. GPU busy (LLM/vision job in flight) → SraVaani ONNX (CPU) — never block
   the farmer on GPU contention.
4. Result confidence < 0.60 AND online → BHASHINI cross-check; if the two
   transcripts disagree on a critical entity → confirmation gate showing both
   candidates.
5. Engine used is recorded on the Input node (`asr.engine`).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from canonical_schema import AsrResult

from speech_service.engines.base import (
    ASREngine,
    AudioInput,
    EngineError,
    GpuState,
    TranscriptionOutcome,
)

FAST_PATH_MAX_MS = 3000  # ≤ 3 s → SraVaani fast path
CROSS_CHECK_THRESHOLD = 0.60  # confidence below this → online cross-check


class NoEngineAvailable(RuntimeError):
    """No ASR engine can serve the request (all runtimes missing)."""


@dataclass(frozen=True)
class CriticalEntity:
    """A term whose misrecognition changes the outcome (crop/pest/product/dose)."""

    canonical: str
    aliases: tuple[str, ...] = ()


@dataclass
class ASRChain:
    """The full ASR pipeline: select → transcribe → (cross-check)."""

    vaani: ASREngine
    sravaani: ASREngine
    bhashini: ASREngine
    online: bool = False
    confidence_threshold: float = CROSS_CHECK_THRESHOLD
    fast_path_max_ms: int = FAST_PATH_MAX_MS
    critical_entities: list[CriticalEntity] = field(default_factory=list)

    # -- selection ---------------------------------------------------------

    def select_engine(
        self, duration_ms: int, gpu: GpuState, force_engine: str | None = None
    ) -> ASREngine:
        """Deterministic engine selection (docs/05 §2, rules 1–3).

        `force_engine` overrides selection (maps to an `engine_hint`) and
        raises `NoEngineAvailable` if that engine cannot serve.
        """
        if force_engine is not None:
            engines = {
                "vaani-whisper": self.vaani,
                "sravaani": self.sravaani,
                "bhashini": self.bhashini,
            }
            if force_engine not in engines or not engines[force_engine].available():
                raise NoEngineAvailable(f"requested engine unavailable: {force_engine}")
            return engines[force_engine]
        if duration_ms <= self.fast_path_max_ms and gpu.free and self.sravaani.available():
            return self.sravaani
        if gpu.free and self.vaani.available():
            return self.vaani
        if self.sravaani.available():
            return self.sravaani  # CPU/ONNX escape path
        if self.vaani.available():
            return self.vaani
        if self.bhashini.available() and self.online:
            return self.bhashini
        raise NoEngineAvailable(
            "no ASR engine available (install faster-whisper or onnxruntime, "
            "or configure BHASHINI online)"
        )

    # -- transcribe --------------------------------------------------------

    def transcribe(
        self,
        audio: AudioInput,
        gpu: GpuState,
        online: bool | None = None,
        force_engine: str | None = None,
    ) -> TranscriptionOutcome:
        """Run the chain: select, transcribe, cross-check if needed."""
        is_online = self.online if online is None else online
        engine = self.select_engine(audio.duration_ms, gpu, force_engine=force_engine)
        result = engine.transcribe(audio)
        notes: list[str] = []

        if (
            result.confidence < self.confidence_threshold
            and is_online
            and self.bhashini.available()
        ):
            try:
                cross = self.bhashini.transcribe(audio)
            except EngineError as exc:
                notes.append(f"bhashini cross-check failed: {exc}")
                return TranscriptionOutcome(
                    result=result, engine_used=engine.name, notes=notes
                )
            candidates = self._disagreement_candidates(result, cross)
            if candidates:
                notes.append(
                    "offline and online transcripts disagree on a critical entity "
                    "→ confirmation gate"
                )
                return TranscriptionOutcome(
                    result=result,
                    engine_used=engine.name,
                    cross_check=cross,
                    confirmation_required=True,
                    candidates=candidates,
                    notes=notes,
                )
            notes.append("bhashini cross-check agreed with offline transcript")
            return TranscriptionOutcome(
                result=result,
                engine_used=engine.name,
                cross_check=cross,
                notes=notes,
            )

        return TranscriptionOutcome(result=result, engine_used=engine.name, notes=notes)

    # -- cross-check helpers -----------------------------------------------

    def _disagreement_candidates(self, offline: AsrResult, online: AsrResult) -> list[str]:
        """Critical entities present in one transcript but not the other."""
        offline_text = offline.transcript.lower()
        online_text = online.transcript.lower()
        candidates: list[str] = []
        for entity in self.critical_entities:
            terms = (entity.canonical, *entity.aliases)
            in_offline = any(t.lower() in offline_text for t in terms)
            in_online = any(t.lower() in online_text for t in terms)
            if in_offline != in_online:
                candidates.append(entity.canonical)
        return candidates
