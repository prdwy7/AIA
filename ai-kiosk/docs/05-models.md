# 05 — Models (ML Catalog)

> Roadmap §5.3. Machine-readable registry: `models/registry.yaml` + per-model cards
> in `models/cards/`. Baseline pins are Sep 2026; all pins live in lockfiles and
> Dockerfile tags; upgrades follow the release framework (roadmap §4.5) with
> regression gates.

## 1. Model registry (initial entries)

| ID | Model | Class | License | Deploy | Purpose | Status at M1 |
|---|---|---|---|---|---|---|
| MODEL-0.1.0 | Gemma 3 12B (Q5_K_M) | LLM+VLM | Gemma ToU | Edge (Ollama) | Advisory drafting, structured observations | Baseline benchmark |
| MODEL-0.1.1 | Llama 3.1 8B (Q5_K_M) | LLM | Llama 3.1 CL | Edge (Ollama) | Lightweight fallback / canary comparison | Baseline benchmark |
| MODEL-0.2.0 | Sarvam-M 24B (FP8/AWQ) | LLM | Apache-2.0 | Central (vLLM/Ollama) | Online-mode drafting, eval judge | Baseline benchmark |
| ASR-0.1.0 | whisper-large-v3-vaani-telugu (faster-whisper, int8) | ASR | Apache-2.0 | Edge | **Primary** offline Telugu/English transcription | WER benchmark on agri-vocab set |
| ASR-0.1.1 | SraVaani-1.0 (ONNX/FP16) | ASR | MIT | Edge | **Fast fallback** (low latency / GPU contention) | Latency + WER benchmark |
| ASR-0.2.0 | IndicWav2Vec Telugu (fine-tuned) | ASR | per AI4Bharat | Edge | Domain-adapted ASR candidate | Phase 5 candidate |
| TTS-0.1.0 | Piper Telugu (medium quality) | TTS | MIT | Edge | Offline Telugu speech | MOS test with farmers |
| TTS-0.2.0 | BHASHINI TTS Telugu | TTS | platform terms | Central | Online-quality speech | A/B with Piper |
| EMB-0.1.0 | BGE-M3 | Embedding | MIT | Edge + Central | KB + case embeddings | Recall benchmark |
| RERANK-0.1.0 | BGE-Reranker-v2-M3 | Reranker | MIT | Edge + Central | Evidence reranking | NDCG benchmark |
| VISION-0.1.0 | Gemma 3 12B vision | VLM | Gemma ToU | Edge | Structured observations | Observation-accuracy benchmark |
| CLASS-0.1.0 | ViT-B/16 fine-tuned (KVK dataset v1) | Classifier | — | Edge (ONNX) | Disease/pest classification | F1 per class benchmark |

## 2. ASR chain (user-specified, primary + fallback)

| Priority | Engine | Model / runtime | When used | Notes |
|---|---|---|---|---|
| **1 (primary)** | **Vaani-Whisper Telugu** | `ARTPARK-IISc/whisper-large-v3-vaani-telugu` (Apache-2.0, 2B) via faster-whisper int8 | Default; quality-first path | Telugu-specialized Whisper large-v3 fine-tune on the Vaani dataset; strong Telugu lexicon; standard usage (`chunk_length_s=30`, `forced_decoder_ids = None`) |
| **2 (fast fallback)** | **SraVaani-1.0** | `ARTPARK-IISc/SraVaani-1.0` (MIT, ~430M, ~900 MB FP16, ONNX export) | GPU busy with LLM/vision inference; latency budget tight; short utterances | FastConformer + hybrid TDT-CTC decoder; fine-tuned on ~31k hours across 65 Indian languages; Telugu WER ~25.1 (avg); fine-tunable via NeMo (github.com/ARTPARK-Speech-Models/SraVaani) |
| **3 (online)** | **BHASHINI ASR API** | Government platform (bhashini.gov.in) | Online AND (a) offline transcript confidence < 0.60, or (b) cross-check of a low-confidence transcript | Higher quality on some domains; adds network dependency; used as cross-check, not default |

**Selection logic (deterministic, in speech-service `chain.py`):**
1. Utterance ≤ 3 s AND GPU free → SraVaani (fast path, low latency).
2. GPU free → Vaani-Whisper (default quality).
3. GPU busy (LLM/vision job in flight) → SraVaani ONNX (CPU) — never block the farmer on GPU contention.
4. Result confidence < 0.60 AND online → BHASHINI cross-check; if the two transcripts disagree on a critical entity → confirmation gate showing both candidates.
5. Engine used is recorded on the `Input` node (`asr.engine`) — per-engine WER is tracked.

**TTS chain:** Piper Telugu (default, offline, sub-second on CPU) → BHASHINI TTS
(online, higher quality) → text-only display (screen always shows the full answer).
TTS text is generated from the **locked output object**, never from raw LLM text.

## 3. Why a dedicated vision classifier (CLASS-0.1.0)

Research (WACV 2026 HARVEST-Vision): open VLMs achieve only **~39–65%** on
fine-grained crop disease classification vs ~93% for prompted proprietary models →
a domain classifier is required for reliable disease/pest ID. The VLM (Gemma 3 12B
vision) stays as **observation extractor + hypothesis generator** — it never produces
a final diagnosis. Dataset: KVK-curated, top 10–15 diseases/pests of Kurnool crops,
≥ 500 images/class, two-scientist labeling with adjudication (Cohen's κ ≥ 0.80).

## 4. Model selection gate (Phase 1/5 exit)

Each model class ships with a benchmark report on the KVK-curated evaluation sets
(Telugu agri-vocabulary ASR set, KB retrieval set, disease image set, Telugu QA set).
The primary model must beat the alternative by the framework-defined margin or be
swapped — the architecture is model-agnostic by design.

## 5. Evaluation sets (KVK-curated, DVC-versioned, consented)

| Set | Size (v1) | Used for |
|---|---|---|
| Kurnool agri-vocabulary ASR set | ≥ 500 utterances (dialectal; crop/pest/product/dose/location terms; recorded with local farmers) | WER/CER, entity accuracy, per-engine comparison |
| KB retrieval set | ≥ 200 questions with gold evidence (per crop) | Retrieval recall, NDCG, reranker quality |
| Disease/pest image set | Top 10–15 classes × ≥ 500 images (two-scientist labeling) | Quality-check P/R, observation accuracy, classifier F1 per class |
| Telugu QA set | ≥ 300 questions (informational + advisory) | Groundedness, answer relevancy, Telugu comprehension |
| Similar-case golden pairs | ≥ 100 curated pairs (similar + dissimilar) | NDCG@10, difference visibility |
| Red-team corpus | 10 scenarios × variants | Safety gates, prompt-injection defense |

Specs: `evals/agri_vocab/README.md`, `evals/golden_cases/README.md`,
`evals/promptfoo/redteam.yaml`.

## 6. Version tuple (roadmap §4.5.1)

```text
SYSTEM_VERSION =
    MODEL_VERSION
  + KNOWLEDGE_VERSION
  + RULE_VERSION
  + PROMPT_POLICY_VERSION
  + SPEECH_VERSION
  + DATA_SCHEMA_VERSION
```

- Every prescription records the full version tuple.
- Every edge device reports its active tuple; the admin console shows fleet distribution.
- The lexicon is part of `SPEECH_VERSION` — released through the same pipeline as models and KB.
- Model artifacts are **content-addressed**: SHA-256 + signature; the version registry maps logical versions (MODEL-0.1.0) to artifact digests.

## 7. GPU sizing (edge, 16 GB VRAM)

| Workload | Model / runtime | VRAM (est.) |
|---|---|---|
| Edge LLM + vision | Gemma 3 12B Q5_K_M (Ollama) | ~8–9 GB |
| ASR (primary) | Vaani-Whisper 2B, faster-whisper int8 | ~2–3 GB |
| ASR (fast path) | SraVaani ONNX | 0 (CPU path) |
| Embeddings | BGE-M3 int8 | ~1.2 GB |
| Reranker | BGE-Reranker-v2-M3 | ~1–2 GB (batched, time-shared with LLM) |
| Classifier | ViT-B/16 ONNX | ~0.5 GB (or CPU) |
| TTS | Piper | 0 (CPU) |

Worst-case concurrent (LLM drafting + ASR + embeddings): ~13.5 GB → **16 GB VRAM is
comfortable** with headroom for KV cache and batched vision observations. The GPU
queue prioritizes prescription drafting > observations > ASR; ASR always has the
CPU/ONNX escape path (SraVaani) so the farmer is never blocked on GPU contention.
