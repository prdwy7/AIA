# speech-service (S5)

Full voice pipeline (roadmap §9.1). Voice is a first-class input modality.

## Purpose

- VAD + ffmpeg normalization (16 kHz mono WAV) upstream of ASR.
- ASR engine selection with a deterministic fallback chain:
  **Vaani-Whisper Telugu (primary) → SraVaani-1.0 (fast fallback) → BHASHINI (online cross-check)**.
- Agricultural vocabulary normalization (lexicon pass).
- TTS synthesis: **Piper Telugu → BHASHINI TTS → text-only** (screen always
  shows the full answer).

## ASR chain (user-specified models)

| Priority | Engine | Model / runtime | When used |
|---|---|---|---|
| 1 (primary) | **Vaani-Whisper Telugu** | `ARTPARK-IISc/whisper-large-v3-vaani-telugu` (Apache-2.0, 2B) via faster-whisper int8 | Default; quality-first path. Telugu-specialized Whisper large-v3 fine-tune on the Vaani dataset; strong Telugu lexicon. Standard usage: `chunk_length_s=30`, `forced_decoder_ids=None`. |
| 2 (fast fallback) | **SraVaani-1.0** | `ARTPARK-IISc/SraVaani-1.0` (MIT, ~430M, ONNX/FP16) | GPU busy with LLM/vision inference; latency budget tight; short utterances (≤ 3 s). FastConformer + hybrid TDT-CTC decoder; Telugu WER ~25.1 (avg); fine-tunable via NeMo (github.com/ARTPARK-Speech-Models/SraVaani). |
| 3 (online) | **BHASHINI ASR API** | bhashini.gov.in | Online AND (a) offline transcript confidence < 0.60, or (b) cross-check of a low-confidence transcript. |

### Selection logic (deterministic, `chain.py`)

1. Utterance ≤ 3 s AND GPU free → SraVaani (fast path, low latency).
2. GPU free → Vaani-Whisper (default quality).
3. GPU busy (LLM/vision job in flight) → SraVaani ONNX (CPU) — never block
   the farmer on GPU contention.
4. Result confidence < 0.60 AND online → BHASHINI cross-check; if the two
   transcripts disagree on a critical entity → confirmation gate showing both
   candidates.
5. Engine used is recorded on the `Input` node (`asr.engine`) — per-engine WER
   is tracked.

### TTS chain

Piper Telugu (default, offline, sub-second on CPU) → BHASHINI TTS (online,
higher quality) → text-only display. TTS text is generated from the **locked
output object**, never from raw LLM text.

## Responsibilities

- `POST /v1/speech/transcribe` — ASR with engine hint (auto | vaani-whisper | sravaani | bhashini).
- `POST /v1/speech/synthesize` — TTS with fallback chain.
- Lexicon normalization pass (`normalize.py`).
- Record engine/model/confidence on every `Input` node.

## Tech

- Python 3.12; faster-whisper (int8) for the Whisper family; ONNX Runtime for
  SraVaani; Piper (piper1-gpl) for TTS; ffmpeg; silero-vad (upstream).
- GPU-aware job queue: ASR yields to LLM inference when VRAM is contended →
  SraVaani on the CPU/ONNX path.
- Heavy runtimes are **optional extras** (`[asr]`, `[tts]`); engine
  availability is probed at runtime so the service degrades gracefully.

## Interfaces

- Inbound: input-orchestrator (S4), channel adapters.
- Outbound: MinIO (audio objects), BHASHINI API (online), case-service (via S4).

## Dependencies

- Models ASR-0.1.0 (Vaani-Whisper) / ASR-0.1.1 (SraVaani) / TTS-0.1.0 (Piper).
- ffmpeg, silero-vad; `canonical-schema`.

## Scaling

Concurrency-limited GPU queue; per-engine latency SLOs: Vaani-Whisper < 3 s,
SraVaani < 1.5 s (p95). Horizontal replicas share the GPU pool via queue.

## Built in

Basic chain in Phase 1 (kiosk MVP); full fallback + cross-check in Phase 4;
scientist voice feedback in Phase 8.

## Key invariants

- Engine used is recorded on the `Input` node (`asr.engine`).
- Confidence < 0.60 AND online → BHASHINI cross-check; disagreement on a
  critical entity → confirmation gate showing both candidates.
- TTS text is generated from the **locked output object**, never raw LLM text.
- The farmer is never blocked on GPU contention (SraVaani CPU escape path).

## Model download (HuggingFace)

The two user-specified ASR models are prefetched lazily from HuggingFace on
first use and cached under `KIOSK_MODELS_DIR` (default `~/.cache/kiosk/models`).
To pre-populate the edge cache (e.g. before the device goes offline):

```bash
make download-models   # == ./scripts/download_models.sh
```

Heavy runtimes (faster-whisper, onnxruntime, huggingface_hub) are the optional
`[asr]` extra:

```bash
uv sync --all-packages --extra asr
```

Alternatively, point the engines at pre-downloaded artifacts via
`ASR_MODEL_DIR` / `ASR_MODEL_PATH` (kept as `--model_dir` / `--model_path` in
`engines/vaani_whisper.py` / `engines/sravaani.py`).

## Run

```bash
uv sync --all-packages
uv run uvicorn speech_service.app:app --reload
uv run pytest services/speech-service -q
```
