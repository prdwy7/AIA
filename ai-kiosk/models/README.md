# models/ — ML catalog

Machine-readable model registry + per-model cards (docs/05-models.md; roadmap §5.3).

- `registry.yaml` — every model in the system: logical version ID (used in the
  version tuple), class, license, deploy target, purpose, source, M1 gate status.
  Also encodes the ASR chain (user-specified primary + fallback) and TTS chain.
- `cards/` — one card per model with runtime/usage, selection logic, benchmark
  gates, and invariants.

## Conventions

- Baseline pins: **Sep 2026**. All pins live in lockfiles and Dockerfile tags;
  upgrades follow the release framework (roadmap §4.5) with regression gates.
- Model artifacts are **content-addressed** (SHA-256) + signed; the version
  registry (`db: version_registry`) maps logical versions (e.g. `MODEL-0.1.0`)
  to artifact digests.
- The lexicon is part of `SPEECH_VERSION` — released through the same pipeline
  as models and KB.
- **Model-selection gate (docs/05 §4):** each model class ships with a
  benchmark report on the KVK-curated evaluation sets; the primary model must
  beat the alternative by the framework-defined margin or be swapped — the
  architecture is model-agnostic by design.

## ASR chain (user-specified)

| Priority | Model | When |
|---|---|---|
| 1 (primary) | `ARTPARK-IISc/whisper-large-v3-vaani-telugu` (ASR-0.1.0) | default; quality-first |
| 2 (fast fallback) | `ARTPARK-IISc/SraVaani-1.0` (ASR-0.1.1) | ≤ 3 s utterances; GPU busy; latency budget tight |
| 3 (online) | BHASHINI ASR API | online AND confidence < 0.60 (cross-check) |

Selection logic is implemented deterministically in
`services/speech-service/src/speech_service/chain.py` (docs/05 §2).
