# Card — Gemma 3 12B (MODEL-0.1.0 / VISION-0.1.0)

| Field | Value |
|---|---|
| Registry IDs | `MODEL-0.1.0` (LLM), `VISION-0.1.0` (VLM) |
| Model | Gemma 3 12B, Q5_K_M |
| Class | LLM + VLM |
| License | Gemma Terms of Use (tracked per release — roadmap R15) |
| Deploy | Edge (Ollama 0.34.x) |
| Source | ollama library: `gemma3:12b` |

## What it is

The primary edge model: advisory drafting (structured JSON output) and
structured visual observations. One model serves both roles; the GPU queue
prioritizes prescription drafting > observations > ASR.

## Runtime & usage

- Runtime: **Ollama 0.34.x**, Q5_K_M (~8–9 GB VRAM).
- LLM calls: JSON-schema-enforced structured output; output validated against
  the Pydantic schema **before** entering the rules/prescription pipeline.
- Vision calls: observation extraction only — states
  OBSERVED/POSSIBLE/UNCERTAIN/CONTRADICTORY/NOT_VISIBLE; **confidence capped
  at 0.6**; the VLM never produces a final diagnosis (docs/05 §3).
- Prompt policy versioned (PROMPT_POLICY_VERSION in the version tuple).

## Benchmarks / gates

- Telugu QA set (≥ 300 questions): groundedness, answer relevancy, Telugu
  comprehension.
- Observation-accuracy benchmark on the disease/pest image set.
- Shadow-model comparison vs Llama 3.1 8B and (online) Sarvam-M 24B
  (Phase 14 shadow runner).

## Invariants

- Farmer text is **data, never instructions** (prompt-injection defense;
  red-team scenario set in `evals/promptfoo/redteam.yaml`).
- Regulatory data is never injected into the LLM context as instructions.
- Every decision-bearing response carries `version_tuple` + `trace_id`.
