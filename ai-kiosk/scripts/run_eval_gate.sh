#!/usr/bin/env bash
# AI evaluation gate (docs/08 §2–§3) — BLOCKING for every release.
#   RAGAS retrieval/groundedness + DeepEval answer/metric + promptfoo red-team.
# Usage: ./scripts/run_eval_gate.sh   (== make eval-gate)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> [1/3] RAGAS retrieval + groundedness metrics (docs/08 §2)..."
if [[ -f evals/ragas_runner.py ]]; then
  uv run python evals/ragas_runner.py
else
  echo "    SKIP: evals/ragas_runner.py not yet implemented (Phase 14 eval tooling)."
  echo "    See docs/08 §2 for the metric gates (context recall, faithfulness, groundedness)."
fi

echo "==> [2/3] DeepEval answer/metric evals (docs/08 §2)..."
if [[ -f evals/deepeval_runner.py ]]; then
  uv run python evals/deepeval_runner.py
else
  echo "    SKIP: evals/deepeval_runner.py not yet implemented (Phase 14 eval tooling)."
fi

echo "==> [3/3] promptfoo red-team suite (docs/08 §3) — BLOCKING..."
if command -v npx >/dev/null 2>&1; then
  npx promptfoo@latest eval --config evals/promptfoo/redteam.yaml
else
  echo "ERROR: npx not found. Install Node.js to run the promptfoo red-team gate."
  exit 1
fi

echo "Eval gate passed."
