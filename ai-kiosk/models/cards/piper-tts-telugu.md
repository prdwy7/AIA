# Card — Piper TTS Telugu (TTS-0.1.0)

| Field | Value |
|---|---|
| Registry ID | `TTS-0.1.0` |
| Model | Piper Telugu (medium quality) |
| Class | TTS |
| License | MIT |
| Deploy | Edge (CPU) |
| Purpose | Offline Telugu speech |
| Source | piper1-gpl (Telugu voice, medium) |

## What it is

Offline neural TTS for the kiosk — sub-second on CPU, zero VRAM. The default
voice for every spoken response; the screen always shows the full answer as
text (the text-only fallback is the third step of the TTS chain).

## Runtime & usage

- Runtime: piper1-gpl (CPU).
- Input: Telugu text generated from the **locked output object** — never from
  raw LLM text (invariant).
- Output: 22.05 kHz WAV → kiosk speaker.

## TTS chain (docs/05 §2)

1. Piper Telugu (default, offline, sub-second on CPU).
2. BHASHINI TTS Telugu (online, higher quality) — TTS-0.2.0.
3. Text-only display (screen always shows the full answer).

## Benchmarks / gates

- MOS test with farmers (target ≥ 4/5, docs/08 §6.3).
- A/B vs BHASHINI TTS when online.
