#!/usr/bin/env python
"""Precise voice-mode smoke test for speech-service (S5).

Loads the primary ASR engine (Vaani-Whisper Telugu) and transcribes a
16 kHz mono WAV file, printing transcript, confidence, engine, and latency.

This drives the ASR chain *directly* (no HTTP), so it is ideal for verifying
the models and the deterministic selection logic in isolation.

Usage:
  uv run python scripts/voice_test.py <audio.wav> [--engine vaani-whisper]

  --engine  one of: auto | vaani-whisper | sravaani | bhashini
            (default: vaani-whisper — the functional offline primary)

Example:
  uv run python scripts/voice_test.py /tmp/te-sample.wav
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from speech_service.chain import ASRChain
from speech_service.engines.base import AudioInput, GpuState
from speech_service.engines.bhashini import BhashiniEngine
from speech_service.engines.sravaani import SraVaaniEngine
from speech_service.engines.vaani_whisper import VaaniWhisperEngine


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ASR on a Telugu WAV file.")
    parser.add_argument("audio", type=Path, help="16 kHz mono WAV file")
    parser.add_argument(
        "--engine",
        choices=["auto", "vaani-whisper", "sravaani", "bhashini"],
        default="vaani-whisper",
    )
    args = parser.parse_args()

    if not args.audio.exists():
        print(f"error: audio file not found: {args.audio}", file=sys.stderr)
        return 2

    data = args.audio.read_bytes()
    audio = AudioInput(data=data, duration_ms=_wav_duration_ms(data), language="te")

    chain = ASRChain(
        vaani=VaaniWhisperEngine(),
        sravaani=SraVaaniEngine(),
        bhashini=BhashiniEngine(),
        online=False,
    )
    force = None if args.engine == "auto" else args.engine

    print(f"engine hint   : {args.engine}")
    print(f"audio         : {args.audio.name} ({len(data)} bytes, {audio.duration_ms} ms)")
    print("loading/transcribing…", flush=True)

    t0 = time.monotonic()
    outcome = chain.transcribe(audio, GpuState(free=True), force_engine=force)
    wall = (time.monotonic() - t0) * 1000

    r = outcome.result
    print("-" * 60)
    print(f"engine used   : {outcome.engine_used}")
    print(f"model         : {r.model_id} v{r.version}")
    print(f"confidence    : {r.confidence:.3f}")
    print(f"engine time   : {r.duration_ms} ms   (wall {wall:.0f} ms)")
    print(f"transcript    : {r.transcript}")
    if outcome.notes:
        for n in outcome.notes:
            print(f"note          : {n}")
    print("-" * 60)
    return 0


def _wav_duration_ms(data: bytes) -> int:
    import io
    import wave

    try:
        with wave.open(io.BytesIO(data), "rb") as wav:
            rate = wav.getframerate() or 16000
            return int(wav.getnframes() / rate * 1000)
    except Exception:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
