# Card — Llama 3.1 8B (MODEL-0.1.1)

| Field | Value |
|---|---|
| Registry ID | `MODEL-0.1.1` |
| Model | Llama 3.1 8B, Q5_K_M |
| Class | LLM |
| License | Llama 3.1 Community License (tracked per release — roadmap R15) |
| Deploy | Edge (Ollama 0.34.x) |
| Source | ollama library: `llama3.1:8b` |

## What it is

Lightweight fallback LLM for the edge: used when the 12B model is unavailable
(boot, OOM, maintenance) and as the canary-comparison model in the release
pipeline.

## Runtime & usage

- Runtime: **Ollama 0.34.x**, Q5_K_M (~5–6 GB VRAM).
- Same structured-output contract as Gemma 3 12B (JSON schema enforced,
  Pydantic-validated before pipeline entry).
- Model hot-swap is an llm-service responsibility (S10).

## Benchmarks / gates

- Telugu QA set: groundedness, answer relevancy, Telugu comprehension.
- Canary: correction rate and groundedness must not be worse than production
  before promotion (docs/05 §4, roadmap §4.5).

## Invariants

- Same safety invariants as the primary LLM (farmer text = data; regulatory
  data never as instructions; version tuple + trace_id on every output).
