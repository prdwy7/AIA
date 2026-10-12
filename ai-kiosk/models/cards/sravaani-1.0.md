# Card — SraVaani-1.0 (ASR-0.1.1)

| Field | Value |
|---|---|
| Registry ID | `ASR-0.1.1` |
| Model | `ARTPARK-IISc/SraVaani-1.0` |
| Class | ASR |
| License | MIT |
| Deploy | Edge (CPU/ONNX escape path; GPU when free) |
| Role | **FAST FALLBACK** (low latency / GPU contention) (user-specified) |
| Source | https://huggingface.co/ARTPARK-IISc/SraVaani-1.0 |

## What it is

FastConformer + hybrid TDT-CTC decoder, ~430M parameters (~900 MB FP16, ONNX
export). Fine-tuned on ~31k hours across 65 Indian languages; Telugu WER ~25.1
(average). Fine-tunable via NeMo
(github.com/ARTPARK-Speech-Models/SraVaani) — the ASR-0.2.0 domain-adaptation
candidate builds on this lineage.

## Runtime & usage

- Runtime: **ONNX Runtime** (CPU path — 0 GB VRAM; GPU when free).
- Input: 16 kHz mono WAV.
- Output: transcript + confidence; engine recorded as `asr.engine = sravaani`.

## Selection (docs/05 §2)

1. Utterance ≤ 3 s AND GPU free → SraVaani (fast path, low latency).
2. GPU busy (LLM/vision job in flight) → SraVaani ONNX (CPU) — never block the
   farmer on GPU contention.

## Benchmarks / gates

- Latency SLO: p95 < 1.5 s (docs/08 §6.2).
- WER on the Kurnool agri-vocabulary set (baseline ~25.1 Telugu avg; domain
  set expected to differ — measured at M1).

## Invariants

- Always available as the CPU escape path — ASR never dead-ends the case.
- Engine used is always recorded on the `Input` node.
