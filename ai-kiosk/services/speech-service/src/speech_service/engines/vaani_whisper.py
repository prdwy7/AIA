"""Vaani-Whisper Telugu — PRIMARY offline ASR engine (docs/05 §2, priority 1).

Model: `ARTPARK-IISc/whisper-large-v3-vaani-telugu` (Apache-2.0, ~2B) — a
Telugu-specialized Whisper large-v3 fine-tune on the Vaani dataset with a
strong Telugu agricultural lexicon.

Runtime: HuggingFace `transformers` (WhisperForConditionalGeneration). This
checkpoint is NOT a drop-in for faster-whisper/CTranslate2: it uses 128 mel
bins (standard Whisper uses 80) and ships a `vocab.json`+`merges.txt`
tokenizer (no `tokenizer.json`), both of which `transformers` handles natively.
The model's own model card prescribes the `transformers` pipeline.

The transformers import and the model download are lazy, so the service (and
its tests) run without the heavy runtime installed. The model is prefetched
from HuggingFace on first use (cached under `KIOSK_MODELS_DIR`, or via
`scripts/download_models.sh`) unless `model_dir` is provided.
"""

from __future__ import annotations

import time

from canonical_schema import AsrEngine, AsrResult

from speech_service.engines.base import AudioInput, EngineError

MODEL_ID = "whisper-large-v3-vaani-telugu"
MODEL_VERSION = "1.0.0"
HF_REPO = "ARTPARK-IISc/whisper-large-v3-vaani-telugu"


class VaaniWhisperEngine:
    """Primary Telugu ASR (quality-first path)."""

    name: str = "vaani-whisper"
    model_id: str = MODEL_ID
    version: str = MODEL_VERSION

    def __init__(
        self,
        device: str = "cpu",
        model_dir: str | None = None,
    ) -> None:
        self._device = device
        self._model_dir = model_dir
        self._model = None  # lazy
        self._processor = None  # lazy

    def available(self) -> bool:
        try:
            import torch  # noqa: F401
            import transformers  # noqa: F401

            return True
        except ImportError:
            return False

    def ensure_downloaded(self) -> str:
        """Prefetch the model from HuggingFace → returns the local directory."""
        from speech_service.engines.download import download_vaani

        return download_vaani(self._model_dir)

    def _ensure_model(self):
        if self._model is None:
            from transformers import WhisperForConditionalGeneration, WhisperProcessor

            model_dir = self._model_dir or self.ensure_downloaded()
            try:
                self._processor = WhisperProcessor.from_pretrained(model_dir)
                self._model = WhisperForConditionalGeneration.from_pretrained(model_dir)
            except Exception as exc:
                raise EngineError(f"vaani-whisper model load failed: {exc}") from exc
            # The model card sets these to None so language is auto-detected
            # (Telugu/English code-switching) rather than forced.
            self._model.config.forced_decoder_ids = None
            self._model.generation_config.forced_decoder_ids = None
        return self._model, self._processor

    def transcribe(self, audio: AudioInput) -> AsrResult:
        import torch

        if not self.available():
            raise EngineError("transformers/torch runtime not installed")
        model, processor = self._ensure_model()
        start = time.monotonic()
        try:
            inputs = processor(
                self._decode_wav(audio.data), sampling_rate=16000, return_tensors="pt"
            )
            with torch.no_grad():
                generated_ids = model.generate(inputs.input_features)
            transcript = processor.batch_decode(
                generated_ids, skip_special_tokens=True
            )[0].strip()
            duration_ms = int((time.monotonic() - start) * 1000)
            # transformers 5.x no longer exposes per-token scores from
            # `generate`; a log-prob confidence estimator is a follow-up.
            confidence = 1.0
        except EngineError:
            raise
        except Exception as exc:
            raise EngineError(f"vaani-whisper transcription failed: {exc}") from exc
        return AsrResult(
            model_id=self.model_id,
            version=self.version,
            engine=AsrEngine.VAANI_WHISPER,
            confidence=confidence,
            duration_ms=duration_ms,
            transcript=transcript,
        )

    @staticmethod
    def _decode_wav(data: bytes):
        """Decode a 16 kHz mono/mono-style WAV into float32 mono samples in [-1, 1]."""
        import io
        import wave

        import numpy as np

        with wave.open(io.BytesIO(data), "rb") as wav:
            channels = wav.getnchannels()
            sampwidth = wav.getsampwidth()
            raw = wav.readframes(wav.getnframes())

        if sampwidth == 2:
            arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        elif sampwidth == 1:
            arr = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
        else:
            raise EngineError(f"unsupported WAV sample width: {sampwidth}")

        if channels == 2:
            arr = arr.reshape(-1, 2).mean(axis=1)
        elif channels != 1:
            raise EngineError(f"unsupported WAV channel count: {channels}")

        return arr.astype(np.float32)



