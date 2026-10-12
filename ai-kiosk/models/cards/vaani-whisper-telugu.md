# Card — Vaani-Whisper Telugu (ASR-0.1.0)

| Field | Value |
|---|---|
| Registry ID | `ASR-0.1.0` |
| Model | `ARTPARK-IISc/whisper-large-v3-vaani-telugu` |
| Class | ASR |
| License | Apache-2.0 |
| Deploy | Edge (kiosk GPU) |
| Role | **PRIMARY** offline Telugu/English transcription (user-specified) |
| Source | https://huggingface.co/ARTPARK-IISc/whisper-large-v3-vaani-telugu |

## What it is

Telugu-specialized Whisper large-v3 fine-tune on the Vaani dataset (IISc ARTPARK).
~2B parameters; strong Telugu lexicon — the straight-forward, high-quality path for
offline transcription at the kiosk.

## Runtime & usage

- Runtime: **faster-whisper, int8** (GPU; ~2–3 GB VRAM).
- Standard usage: `chunk_length_s=30`, `forced_decoder_ids=None`.
- Input: 16 kHz mono WAV (ffmpeg-normalized by speech-service).
- Output: transcript + per-segment confidence; engine recorded on the `Input`
  node (`asr.engine = vaani-whisper`).

## Selection (docs/05 §2)

Used when the GPU is free and the utterance is > 3 s (default quality path).
Utterances ≤ 3 s with a free GPU go to the fast path (SraVaani); a busy GPU
forces the SraVaani CPU/ONNX escape path — the farmer is never blocked on
GPU contention.

## Benchmarks / gates

- WER/CER + entity accuracy on the Kurnool agri-vocabulary set (≥ 500
  dialectal utterances) — `evals/agri_vocab/`.
- Latency SLO: p95 < 3 s (docs/08 §6.2).
- Model-selection gate (docs/05 §4): must beat SraVaani by the framework margin
  on the agri-vocab set or the chain order is swapped.

## Invariants

- Confidence < 0.60 AND online → BHASHINI cross-check; critical-entity
  disagreement → confirmation gate showing both candidates.
- Engine used is always recorded on the `Input` node (per-engine WER tracking).
