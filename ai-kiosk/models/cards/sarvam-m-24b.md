# Card — Sarvam-M 24B (MODEL-0.2.0)

| Field | Value |
|---|---|
| Registry ID | `MODEL-0.2.0` |
| Model | Sarvam-M 24B (FP8/AWQ) |
| Class | LLM |
| License | Apache-2.0 |
| Deploy | Central (vLLM/Ollama) |
| Purpose | Online-mode drafting, eval judge |
| Source | Sarvam AI (HuggingFace: `Sarvam-AI/Sarvam-M`) |

## What it is

The central online-mode LLM. At the Sep 2026 baseline it is the strongest open
Telugu LLM (Telugu reward 8.05) — used when the kiosk is online for
higher-quality drafting, and as the **evaluation judge** in the CI evaluation
gate (groundedness, Telugu comprehension).

## Runtime & usage

- Runtime: vLLM (FP8) or Ollama (AWQ) on the central GPU node.
- Same structured-output contract as edge models (JSON schema enforced,
  Pydantic-validated before pipeline entry).
- Online mode is an enhancement — the kiosk is fully functional offline
  (hard requirement, roadmap R10).

## Benchmarks / gates

- Telugu QA set: groundedness, answer relevancy, Telugu comprehension.
- As judge: agreement with scientist decisions on the golden-case set
  (≥ 50 scripted cases) before it is trusted as an eval judge.

## Invariants

- Same safety invariants as edge LLMs (farmer text = data; regulatory data
  never as instructions; version tuple + trace_id on every output).
- License is Apache-2.0 — no ToU risk (contrast with Gemma/Llama; roadmap R15).
