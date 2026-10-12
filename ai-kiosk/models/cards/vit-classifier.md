# Card — ViT-B/16 KVK classifier (CLASS-0.1.0)

| Field | Value |
|---|---|
| Registry ID | `CLASS-0.1.0` |
| Model | ViT-B/16 fine-tuned on KVK dataset v1 |
| Class | Classifier |
| License | internal (KVK-curated dataset) |
| Deploy | Edge (ONNX, ~0.5 GB or CPU) |
| Purpose | Disease/pest classification |
| Source | KVK-curated dataset v1 (see below) |

## Why a dedicated classifier (docs/05 §3)

WACV 2026 HARVEST-Vision: open VLMs achieve only **~39–65%** on fine-grained
crop disease classification vs ~93% for prompted proprietary models. A domain
classifier is required for reliable disease/pest ID. The VLM (Gemma 3 12B
vision) stays as observation extractor + hypothesis generator — it never
produces a final diagnosis.

## Dataset (KVK-curated, DVC-versioned, consented)

- Top 10–15 diseases/pests of Kurnool crops (cotton, paddy, groundnut, maize,
  arhar, castor, millets, chilli).
- ≥ 500 images/class.
- Two-scientist labeling with adjudication (Cohen's κ ≥ 0.80).

## Runtime & usage

- Runtime: ONNX (CPU or GPU); preprocess resize 224 + normalize → softmax over
  the KVK class set → top-k.
- **Diagnosis guard (invariant):** top probability < 0.60 OR top-2 margin <
  0.15 → `UNCERTAIN` — a weak visual signal is never converted into a
  high-confidence diagnosis merely because an image exists. The case proceeds
  to the clarification/hypothesis branch instead.

## Benchmarks / gates

- Disease/pest image set: F1 per class; quality-check precision/recall.
