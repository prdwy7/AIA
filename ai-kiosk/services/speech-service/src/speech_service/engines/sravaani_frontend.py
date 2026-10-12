"""SraVaani feature front-end seam.

The SraVaani ONNX graph expects log-mel spectrogram features produced by the
ARTPARK-Speech-Models/SraVaani NeMo toolkit. This module is the explicit
boundary: production installs the toolkit and implements `sravaani_features`;
without it the engine reports unavailable rather than failing mid-request.
"""

from __future__ import annotations

from speech_service.engines.base import AudioInput, EngineError


def sravaani_features(audio: AudioInput) -> dict[str, object]:
    """Compute ONNX input features for SraVaani.

    Raises EngineError when the ARTPARK toolkit is not installed.
    """
    try:
        from sravaani.nemo_frontend import compute_logmel  # type: ignore[import-not-found]
    except ImportError as exc:
        raise EngineError(
            "SraVaani feature front-end not installed "
            "(github.com/ARTPARK-Speech-Models/SraVaani)"
        ) from exc
    return {"input_features": compute_logmel(audio.data, sample_rate=16000)}
