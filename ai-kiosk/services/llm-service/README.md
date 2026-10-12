# llm-service (S10)

> **Skeleton service** — built in WS-AI (W2); shadow runner in Phase 14.. Full spec: `docs/02-modules.md` §S10
> and `AI_Kiosk_v2_Project_Roadmap.md`.

## Purpose

local LLM inference management.

## Responsibilities

Ollama runtime; structured output generation (JSON schema enforced before pipeline entry); prompt-policy versioning (PROMPT_POLICY_VERSION); shadow-model runner (candidate model answers live cases hidden, Phase 14); token/latency/VRAM telemetry; model hot-swap.

## Tech

Python; Ollama 0.34.x (Gemma 3 12B Q5_K_M primary, Llama 3.1 8B light); llama.cpp fallback; Pydantic v2 output validation; OpenTelemetry spans per call.

## Interfaces

S11, S6 (vision observations), S26 (shadow orchestration), S20 (GPU state).

## Dependencies

models MODEL-0.1.0 / MODEL-0.1.1, Ollama.

## Scaling

GPU queue with priority (prescription drafting > observations > shadow); OOM handling (evict to SraVaani/CPU path, queue); one GPU per kiosk at pilot.

## Built in

WS-AI (W2); shadow runner in Phase 14.

## Key invariants

LLM output must validate against the Pydantic schema before entering the rules/prescription pipeline; farmer text is data, never instructions; regulatory data is never injected into the LLM context as instructions.

## Endpoints (skeleton)

| Method & path | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /ready` | readiness (dependency checks added as the service is built out) |

## Layout

```
services/llm-service/
├── pyproject.toml
├── README.md
├── src/llm_service/
│   ├── __init__.py
│   ├── _version.py
│   └── main.py          # FastAPI app factory
└── tests/
    └── test_llm_service.py
```
