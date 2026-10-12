"""speech-service tests: chain selection, cross-check, normalize, TTS.

Heavy runtimes (faster-whisper, onnxruntime, piper) are NOT installed in CI —
the tests use fake engines to exercise the deterministic selection logic,
which is the part that must never regress.
"""

from __future__ import annotations

import pytest
from canonical_schema import AsrEngine, AsrResult
from fastapi.testclient import TestClient
from speech_service.app import _wav_duration_ms, create_app
from speech_service.chain import ASRChain, CriticalEntity, NoEngineAvailable
from speech_service.engines.base import AudioInput, GpuState
from speech_service.normalize import LexiconEntry, LexiconNormalizer
from speech_service.tts import TtsChain, TtsError

# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class FakeEngine:
    def __init__(
        self,
        name: str,
        available: bool = True,
        transcript: str = "కొత్త పై పసపు",
        confidence: float = 0.9,
    ):
        self.name = name
        self._available = available
        self._transcript = transcript
        self._confidence = confidence
        self.calls: list[AudioInput] = []

    def available(self) -> bool:
        return self._available

    def transcribe(self, audio: AudioInput) -> AsrResult:
        self.calls.append(audio)
        engine_map = {
            "vaani-whisper": AsrEngine.VAANI_WHISPER,
            "sravaani": AsrEngine.SRAVAANI,
            "bhashini": AsrEngine.BHASHINI,
        }
        return AsrResult(
            model_id=f"fake-{self.name}",
            version="0.0.0",
            engine=engine_map[self.name],
            confidence=self._confidence,
            duration_ms=100,
            transcript=self._transcript,
        )


class FakeTts:
    def __init__(self, name: str, available: bool = True):
        self.name = name
        self._available = available

    def available(self) -> bool:
        return self._available

    def synthesize(self, text: str) -> bytes:
        if not self._available:
            raise TtsError(f"{self.name} unavailable")
        return b"RIFF-fake-wav"


AUDIO = AudioInput(data=b"fake-wav", duration_ms=2000)
GPU_FREE = GpuState(free=True)
GPU_BUSY = GpuState(free=False, reason="llm-inference-in-flight")


# ---------------------------------------------------------------------------
# Chain selection (docs/05 §2 rules 1–3)
# ---------------------------------------------------------------------------


def _chain(vaani=True, sravaani=True, bhashini=False, online=False, **kw) -> ASRChain:
    return ASRChain(
        vaani=FakeEngine("vaani-whisper", available=vaani),
        sravaani=FakeEngine("sravaani", available=sravaani),
        bhashini=FakeEngine("bhashini", available=bhashini),
        online=online,
        **kw,
    )


def test_short_utterance_gpu_free_uses_sravaani_fast_path():
    chain = _chain()
    engine = chain.select_engine(duration_ms=2000, gpu=GPU_FREE)
    assert engine.name == "sravaani"


def test_long_utterance_gpu_free_uses_vaani_whisper():
    chain = _chain()
    engine = chain.select_engine(duration_ms=8000, gpu=GPU_FREE)
    assert engine.name == "vaani-whisper"


def test_gpu_busy_uses_sravaani_cpu_path():
    """Rule 3: never block the farmer on GPU contention."""
    chain = _chain()
    engine = chain.select_engine(duration_ms=8000, gpu=GPU_BUSY)
    assert engine.name == "sravaani"


def test_vaani_unavailable_falls_to_sravaani():
    chain = _chain(vaani=False)
    engine = chain.select_engine(duration_ms=8000, gpu=GPU_FREE)
    assert engine.name == "sravaani"


def test_all_offline_unavailable_raises():
    chain = _chain(vaani=False, sravaani=False)
    with pytest.raises(NoEngineAvailable):
        chain.select_engine(duration_ms=8000, gpu=GPU_FREE)


def test_force_engine_overrides_fast_path():
    """engine_hint=vaani-whisper must bypass the SraVaani fast path."""
    chain = _chain()
    engine = chain.select_engine(duration_ms=2000, gpu=GPU_FREE, force_engine="vaani-whisper")
    assert engine.name == "vaani-whisper"


def test_force_unavailable_engine_raises():
    chain = _chain(vaani=False)
    with pytest.raises(NoEngineAvailable):
        chain.select_engine(duration_ms=8000, gpu=GPU_FREE, force_engine="vaani-whisper")


def test_online_only_uses_bhashini():
    chain = _chain(vaani=False, sravaani=False, bhashini=True, online=True)
    engine = chain.select_engine(duration_ms=8000, gpu=GPU_FREE)
    assert engine.name == "bhashini"


# ---------------------------------------------------------------------------
# Cross-check (rule 4)
# ---------------------------------------------------------------------------


def test_low_confidence_online_triggers_cross_check_agreement():
    vaani = FakeEngine("vaani-whisper", transcript="పసపు పై పురుగు", confidence=0.5)
    bhashini = FakeEngine("bhashini", transcript="పసపు పై పురుగు", confidence=0.9)
    chain = ASRChain(
        vaani=vaani,
        sravaani=FakeEngine("sravaani", available=False),
        bhashini=bhashini,
        online=True,
        critical_entities=[CriticalEntity(canonical="పురుగు", aliases=("insect",))],
    )
    outcome = chain.transcribe(AUDIO, GPU_FREE)
    assert outcome.engine_used == "vaani-whisper"
    assert outcome.cross_check is not None
    assert outcome.confirmation_required is False
    assert bhashini.calls  # cross-check actually ran


def test_disagreement_on_critical_entity_triggers_confirmation_gate():
    vaani = FakeEngine("vaani-whisper", transcript="పసపు పై పురుగు", confidence=0.5)
    bhashini = FakeEngine("bhashini", transcript="పసపు పై తెల్లని మచ్చలు", confidence=0.9)
    chain = ASRChain(
        vaani=vaani,
        sravaani=FakeEngine("sravaani", available=False),
        bhashini=bhashini,
        online=True,
        critical_entities=[CriticalEntity(canonical="పురుగు", aliases=("insect",))],
    )
    outcome = chain.transcribe(AUDIO, GPU_FREE)
    assert outcome.confirmation_required is True
    assert "పురుగు" in outcome.candidates


def test_high_confidence_skips_cross_check():
    vaani = FakeEngine("vaani-whisper", transcript="పసపు", confidence=0.9)
    bhashini = FakeEngine("bhashini", transcript="పసపు")
    chain = ASRChain(
        vaani=vaani,
        sravaani=FakeEngine("sravaani", available=False),
        bhashini=bhashini,
        online=True,
        critical_entities=[CriticalEntity(canonical="పురుగు")],
    )
    outcome = chain.transcribe(AUDIO, GPU_FREE)
    assert outcome.cross_check is None
    assert not bhashini.calls


def test_offline_never_calls_bhashini():
    vaani = FakeEngine("vaani-whisper", transcript="పసపు", confidence=0.3)
    bhashini = FakeEngine("bhashini", transcript="పసపు")
    chain = ASRChain(
        vaani=vaani,
        sravaani=FakeEngine("sravaani", available=False),
        bhashini=bhashini,
        online=False,
    )
    outcome = chain.transcribe(AUDIO, GPU_FREE)
    assert outcome.cross_check is None
    assert not bhashini.calls


# ---------------------------------------------------------------------------
# Lexicon normalization
# ---------------------------------------------------------------------------


def test_lexicon_normalizes_local_term():
    normalizer = LexiconNormalizer(
        [
            LexiconEntry(term="పసపు", normalized="cotton", category="crop"),
            LexiconEntry(term="మచ్చలు", normalized="spots", category="disease"),
        ]
    )
    result = normalizer.normalize("పసపు పై మచ్చలు ఉన్నాయి")
    assert result.normalized == "cotton పై spots ఉన్నాయి"
    assert result.changed
    assert {m.term for m in result.applied} == {"పసపు", "మచ్చలు"}


def test_lexicon_longest_term_wins():
    normalizer = LexiconNormalizer(
        [
            LexiconEntry(term="పసపు", normalized="cotton", category="crop"),
            LexiconEntry(term="పసపు పురుగు", normalized="cotton-bollworm", category="pest"),
        ]
    )
    result = normalizer.normalize("పసపు పురుగు వచ్చింది")
    assert "cotton-bollworm" in result.normalized
    assert "cotton పురుగు" not in result.normalized


def test_lexicon_no_match_returns_unchanged():
    normalizer = LexiconNormalizer([LexiconEntry(term="పసపు", normalized="cotton")])
    result = normalizer.normalize("వరి పొలంలో నీరు")
    assert not result.changed
    assert result.normalized == "వరి పొలంలో నీరు"


# ---------------------------------------------------------------------------
# TTS chain
# ---------------------------------------------------------------------------


def test_tts_prefers_piper():
    chain = TtsChain(piper=FakeTts("piper"), bhashini=FakeTts("bhashini-tts"), online=True)
    outcome = chain.synthesize("లోకడ్ టెక్స్ట్")
    assert outcome.engine == "piper"
    assert outcome.audio is not None


def test_tts_falls_to_bhashini_when_piper_down():
    chain = TtsChain(
        piper=FakeTts("piper", available=False), bhashini=FakeTts("bhashini-tts"), online=True
    )
    outcome = chain.synthesize("లోకడ్ టెక్స్ట్")
    assert outcome.engine == "bhashini-tts"


def test_tts_text_only_fallback():
    chain = TtsChain(
        piper=FakeTts("piper", available=False),
        bhashini=FakeTts("bhashini-tts", available=False),
        online=True,
    )
    outcome = chain.synthesize("పూర్తి సమాధానం")
    assert outcome.engine is None
    assert outcome.audio is None
    assert outcome.text == "పూర్తి సమాధానం"  # screen always shows the full answer


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    with TestClient(create_app()) as c:
        yield c


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "speech-service"


def test_ready_reports_engine_availability(client: TestClient):
    r = client.get("/ready")
    assert r.status_code == 200
    body = r.json()
    assert set(body["dependencies"]) == {"vaani_whisper", "sravaani", "bhashini"}


def test_transcribe_without_runtimes_is_503(client: TestClient):
    """No ASR engine available → 503 problem+json (graceful degradation).

    Deterministic: force all engines unavailable regardless of whether the
    heavy runtimes (faster-whisper/onnxruntime) happen to be installed.
    """
    import base64

    from speech_service.chain import ASRChain

    client.app.state.asr_chain = ASRChain(
        vaani=FakeEngine("vaani-whisper", available=False),
        sravaani=FakeEngine("sravaani", available=False),
        bhashini=FakeEngine("bhashini", available=False),
        online=False,
    )
    r = client.post(
        "/v1/speech/transcribe",
        json={"audio": base64.b64encode(b"fake").decode(), "language": "te"},
    )
    assert r.status_code == 503
    assert r.headers["content-type"].startswith("application/problem+json")


def test_wav_duration_ms_parses_header():
    import io
    import wave

    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(b"\x00\x00" * 16000)  # 1 s of silence @ 16 kHz 16-bit mono
    assert _wav_duration_ms(buf.getvalue()) == 1000


def test_wav_duration_ms_bad_header_is_zero():
    assert _wav_duration_ms(b"not-a-wav") == 0


def test_synthesize_requires_locked_text(client: TestClient):
    r = client.post("/v1/speech/synthesize", json={})
    assert r.status_code == 200
    assert "locked_text" in r.json()["detail"]
