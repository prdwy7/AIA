#!/usr/bin/env python
"""Record your voice from the Mac microphone and transcribe it with Vaani-Whisper.

Records from the default microphone via sox `rec` (16 kHz mono), then runs the
ASR chain (primary Vaani-Whisper) and prints the transcript.

Usage:
  uv run python scripts/record_voice.py                # record 5 s + transcribe
  uv run python scripts/record_voice.py --seconds 8    # record 8 s
  uv run python scripts/record_voice.py --file foo.wav # transcribe an existing WAV

Requires: sox (brew install sox) for microphone capture.
"""

from __future__ import annotations

import argparse
import subprocess
import tempfile
import time
from pathlib import Path

from speech_service.chain import ASRChain
from speech_service.engines.base import AudioInput, GpuState
from speech_service.engines.bhashini import BhashiniEngine
from speech_service.engines.sravaani import SraVaaniEngine
from speech_service.engines.vaani_whisper import VaaniWhisperEngine


def record(seconds: int) -> Path:
    path = Path(tempfile.gettempdir()) / "kiosk-voice.wav"
    print(f"● RECORDING for {seconds} s — speak a Telugu phrase now…", flush=True)
    subprocess.run(
        ["rec", "-r", "16000", "-c", "1", "-b", "16", str(path), "trim", "0", str(seconds)],
        check=True,
        stderr=subprocess.DEVNULL,
    )
    return path


def transcribe(wav_path: Path) -> None:
    data = wav_path.read_bytes()
    audio = AudioInput(data=data, duration_ms=_wav_duration_ms(data), language="te")
    chain = ASRChain(
        vaani=VaaniWhisperEngine(),
        sravaani=SraVaaniEngine(),
        bhashini=BhashiniEngine(),
        online=False,
    )
    print(f"transcribing ({len(data)} bytes, {audio.duration_ms} ms)…", flush=True)
    t0 = time.monotonic()
    outcome = chain.transcribe(audio, GpuState(free=True), force_engine="vaani-whisper")
    wall = (time.monotonic() - t0) * 1000
    r = outcome.result
    print("-" * 56)
    print(f"engine    : {outcome.engine_used}  ({r.model_id})")
    print(f"confidence: {r.confidence:.3f}")
    print(f"latency   : {r.duration_ms} ms (wall {wall:.0f} ms)")
    print(f"transcript: {r.transcript}")
    print("-" * 56)


def _wav_duration_ms(data: bytes) -> int:
    import io
    import wave

    try:
        with wave.open(io.BytesIO(data), "rb") as wav:
            rate = wav.getframerate() or 16000
            return int(wav.getnframes() / rate * 1000)
    except Exception:
        return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Record + transcribe Telugu speech.")
    p.add_argument("--seconds", type=int, default=5)
    p.add_argument("--file", type=Path, default=None)
    args = p.parse_args()

    if args.file:
        if not args.file.exists():
            print(f"error: not found: {args.file}")
            return 2
        transcribe(args.file)
    else:
        wav = record(args.seconds)
        transcribe(wav)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
