"""FastAPI application for speech-service (docs/04 §1).

Endpoints:
- GET  /health, GET /ready
- POST /v1/speech/transcribe  — ASR with engine hint
- POST /v1/speech/synthesize  — TTS with fallback chain
"""

from __future__ import annotations

import base64
import time
from contextlib import asynccontextmanager

from canonical_schema import HealthResponse, ReadyResponse, TranscribeRequest, TranscribeResponse
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from speech_service._version import __version__
from speech_service.chain import ASRChain, NoEngineAvailable
from speech_service.engines.base import AudioInput, EngineError, GpuState
from speech_service.engines.bhashini import BhashiniEngine
from speech_service.engines.sravaani import SraVaaniEngine
from speech_service.engines.vaani_whisper import VaaniWhisperEngine
from speech_service.tts import BhashiniTtsEngine, PiperEngine, TtsChain


def _wav_duration_ms(data: bytes) -> int:
    """Parse a 16 kHz mono WAV header and return duration in ms.

    Returns 0 when the header is unparseable (the engine then measures).
    """
    import io
    import wave

    try:
        with wave.open(io.BytesIO(data), "rb") as wav:
            rate = wav.getframerate() or 16000
            return int(wav.getnframes() / rate * 1000)
    except Exception:
        # Best-effort parse: any malformed/truncated header → 0 (engine measures).
        return 0


def _build_chain() -> ASRChain:
    return ASRChain(
        vaani=VaaniWhisperEngine(),
        sravaani=SraVaaniEngine(),
        bhashini=BhashiniEngine(),
        online=False,  # dev default; production sets from connectivity probe
    )


def _build_tts() -> TtsChain:
    return TtsChain(
        piper=PiperEngine(),
        bhashini=BhashiniTtsEngine(),
        online=False,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.started_at = time.monotonic()
    app.state.asr_chain = _build_chain()
    app.state.tts_chain = _build_tts()
    app.state.gpu_state = GpuState(free=True)  # dev default
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="AI Kiosk — speech-service", version=__version__, lifespan=lifespan)

    @app.exception_handler(NoEngineAvailable)
    async def _no_engine(request: Request, exc: NoEngineAvailable) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            media_type="application/problem+json",
            content={
                "type": "about:blank",
                "title": "No ASR engine available",
                "status": 503,
                "detail": str(exc),
                "instance": str(request.url.path),
            },
        )

    @app.exception_handler(EngineError)
    async def _engine_error(request: Request, exc: EngineError) -> JSONResponse:
        return JSONResponse(
            status_code=502,
            media_type="application/problem+json",
            content={
                "type": "about:blank",
                "title": "ASR engine error",
                "status": 502,
                "detail": str(exc),
                "instance": str(request.url.path),
            },
        )

    @app.get("/health", response_model=HealthResponse)
    def health(request: Request) -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="speech-service",
            version=__version__,
            uptime_s=round(time.monotonic() - request.app.state.started_at, 3),
        )

    @app.get("/ready", response_model=ReadyResponse)
    def ready(request: Request) -> ReadyResponse:
        chain: ASRChain = request.app.state.asr_chain
        deps = {
            "vaani_whisper": chain.vaani.available(),
            "sravaani": chain.sravaani.available(),
            "bhashini": chain.bhashini.available(),
        }
        return ReadyResponse(ready=any(deps.values()), dependencies=deps)

    @app.post("/v1/speech/transcribe", response_model=TranscribeResponse)
    def transcribe(request: Request, body: TranscribeRequest) -> TranscribeResponse:
        """ASR with deterministic engine selection (docs/05 §2)."""
        chain: ASRChain = request.app.state.asr_chain
        gpu: GpuState = request.app.state.gpu_state
        audio_bytes = base64.b64decode(body.audio)
        audio = AudioInput(
            data=audio_bytes,
            duration_ms=_wav_duration_ms(audio_bytes),
            language=body.language.value if hasattr(body.language, "value") else str(body.language),
        )
        force_engine = None if body.engine_hint == "auto" else str(body.engine_hint)
        outcome = chain.transcribe(audio, gpu, force_engine=force_engine)
        return TranscribeResponse(
            transcript=outcome.result.transcript,
            confidence=outcome.result.confidence,
            engine_used=outcome.result.engine,
            duration_ms=outcome.result.duration_ms,
            entity_candidates=outcome.result.entity_candidates,
        )

    @app.post("/v1/speech/synthesize")
    def synthesize(request: Request, body: dict) -> dict:
        """TTS from the locked output object (never raw LLM text)."""
        chain: TtsChain = request.app.state.tts_chain
        locked_text = str(body.get("locked_text", ""))
        if not locked_text:
            return {"detail": "locked_text is required"}
        outcome = chain.synthesize(locked_text)
        return {
            "engine": outcome.engine,
            "audio_b64": base64.b64encode(outcome.audio).decode() if outcome.audio else None,
            "text": outcome.text,
            "notes": outcome.notes,
        }

    return app


app = create_app()
