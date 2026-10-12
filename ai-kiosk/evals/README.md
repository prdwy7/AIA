# evals — AI evaluation (docs/08 §2–§3, docs/05 §5)

The evaluation pyramid is CI-blocking at every release (and monthly on a
production sample). Datasets are KVK-curated, consent-gated, pseudonymous
(no PII; phone numbers → `farmer_ref`; faces blurred), and DVC-versioned.

| Path | What | Spec |
|---|---|---|
| `promptfoo/redteam.yaml` | 10 red-team scenarios (blocking) | docs/08 §3 |
| `golden_cases/` | ≥ 50 scripted end-to-end cases (crops × modalities × risk tiers) | docs/08 §1 (pyramid #3) |
| `agri_vocab/` | ≥ 500 Telugu+Latin lexicon utterances (ASR/lexicon eval) | docs/05 §5 |

## Tools

- **RAGAS** — retrieval + groundedness metrics (context recall, faithfulness).
- **DeepEval** — answer/metric evals + LLM-as-judge.
- **promptfoo** — red-team + regression suites (CI-blocking).
- **lm-evaluation-harness** — base-model benchmarks for model selection gates.

## LLM-as-judge bias controls (docs/08 §2)

Judge models are pinned + versioned; judge outputs sampled for human audit
(≥ 10% weekly); metric thresholds are set by the evaluation framework spec, not
by the model under test.

## Run

```bash
make eval-gate     # → scripts/run_eval_gate.sh
```
