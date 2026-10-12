"""SraVaani-1.0 — FAST FALLBACK ASR engine (docs/05 §2, priority 2).

Model: `ARTPARK-IISc/SraVaani-1.0` (MIT, ~430M params, ~900 MB FP16, ONNX
export). FastConformer encoder + hybrid TDT-CTC decoder, fine-tuned on ~31k
hours across 65 Indian languages; Telugu WER ~25.1 (avg). Fine-tunable via
NeMo (github.com/ARTPARK-Speech-Models/SraVaani).

Used when:
- GPU is busy with LLM/vision inference (CPU/ONNX path — the farmer is never
  blocked on GPU contention), or
- the utterance is short (≤ 3 s) and the latency budget is tight.

The onnxruntime import and the model download are lazy, so the service runs
without them installed. The ONNX model is prefetched from HuggingFace on first
use (cached under `KIOSK_MODELS_DIR`, or via `scripts/download_models.sh`)
unless `model_path` is provided.
"""

from __future__ import annotations

import os
import time

from canonical_schema import AsrEngine, AsrResult

from speech_service.engines.base import AudioInput, EngineError

MODEL_ID = "SraVaani-1.0"
MODEL_VERSION = "1.0.0"
HF_REPO = "ARTPARK-IISc/SraVaani-1.0"


class SraVaaniEngine:
    """Fast Telugu ASR (low latency / GPU-contention path)."""

    name: str = "sravaani"
    model_id: str = MODEL_ID
    version: str = MODEL_VERSION

    def __init__(self, model_path: str | None = None, providers: list[str] | None = None) -> None:
        self._model_path = model_path
        self._providers = providers or ["CPUExecutionProvider"]
        self._session = None  # lazy

    def available(self) -> bool:
        try:
            import onnxruntime  # noqa: F401

            return True
        except ImportError:
            return False

    def ensure_downloaded(self) -> str:
        """Prefetch the model from HuggingFace → returns the local directory."""
        from speech_service.engines.download import download_sravaani

        return download_sravaani()

    def _ensure_session(self):
        if self._session is None:
            import onnxruntime as ort

            model_path = self._model_path
            if model_path is None:
                # Lazy prefetch from HuggingFace (cached under KIOSK_MODELS_DIR).
                model_path = _find_onnx(self.ensure_downloaded())
            try:
                self._session = ort.InferenceSession(model_path, providers=self._providers)
            except Exception as exc:
                raise EngineError(f"sravaani session load failed: {exc}") from exc
        return self._session

    def transcribe(self, audio: AudioInput) -> AsrResult:
        if not self.available():
            raise EngineError("onnxruntime not installed")
        session = self._ensure_session()
        start = time.monotonic()
        try:
            # The SraVaani ONNX graph expects log-mel features; the feature
            # front-end is provided by the NeMo/ARTPARK toolkit in production.
            # Here we keep the boundary explicit: feeders implement
            # `sravaani_features(audio) -> dict[str, np.ndarray]`.
            from speech_service.engines.sravaani_frontend import sravaani_features

            inputs = sravaani_features(audio)
            outputs = session.run(None, inputs)
            transcript = _decode_outputs(outputs)
            duration_ms = int((time.monotonic() - start) * 1000)
        except EngineError:
            raise
        except Exception as exc:
            raise EngineError(f"sravaani transcription failed: {exc}") from exc
        return AsrResult(
            model_id=self.model_id,
            version=self.version,
            engine=AsrEngine.SRAVAANI,
            confidence=0.85,  # replaced by CTC posterior mean in production
            duration_ms=duration_ms,
            transcript=transcript,
        )


def _find_onnx(model_dir: str) -> str:
    """Locate the ONNX graph inside a downloaded SraVaani snapshot."""
    import glob

    candidates = glob.glob(os.path.join(model_dir, "**", "*.onnx"), recursive=True)
    if not candidates:
        raise EngineError(f"no .onnx model found under {model_dir}")
    return candidates[0]


def _decode_outputs(outputs: object) -> str:
    """Decode SraVaani graph outputs into text.

    Production wiring uses the ARTPARK-Speech-Models/SraVaani decoding
    utilities (greedy/beam over the TDT-CTC head). Kept as a seam so the
    engine contract stays stable while the decoder is finalized.
    """
    raise EngineError("sravaani decoder not wired — install the ARTPARK toolkit")
