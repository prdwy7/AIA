# image-service (S6)

Image evidence pipeline (roadmap §9.4). Picture is a first-class input
modality.

## Purpose

- Quality checks (blur / brightness / size / crop detection) with concrete
  retry instructions shown to the farmer.
- Structured visual observations via **Gemma 3 12B vision** (states
  `OBSERVED | POSSIBLE | UNCERTAIN | CONTRADICTORY | NOT_VISIBLE`).
- Fine-tuned **ViT disease/pest classifier** (CLASS-0.1.0).
- Media-set management (views: whole plant, leaf, stem, fruit, pest close-up,
  field context) with missing-view requests.
- Face-blurring for stored media (policy: faces blurred by default).

## Responsibilities

- `POST /v1/media/analyze` — quality + observations + candidate hypotheses +
  missing views.
- Media-set tracking per case (which views are already received).
- Observation nodes on the CST (via case-service).

## Tech

- Python 3.12; Pillow for deterministic quality checks (Laplacian-variance
  sharpness, mean brightness, size); Ollama (Gemma 3 12B vision) for
  observations; PyTorch/ONNX ViT classifier (optional extra).
- Heavy runtimes are **optional extras**; availability is probed at runtime.

## Interfaces

- Inbound: input-orchestrator (S4), channel adapters (photos).
- Outbound: MinIO (media), case-service (observation nodes), lexicon
  (crop/pest taxonomy).

## Dependencies

- Models VISION-0.1.0 (Gemma 3 12B vision) / CLASS-0.1.0 (ViT-B/16 fine-tuned
  on KVK dataset v1), Ollama, MinIO.

## Scaling

GPU job queue (batched); the classifier runs on CPU/ONNX for low latency;
observation extraction is the GPU-bound step.

## Built in

Phase 5.

## Key invariants

- A **weak visual signal is never converted into a high-confidence diagnosis**
  merely because an image exists (classifier guard: low confidence or small
  top-2 margin → `UNCERTAIN`).
- Faces blurred by default in stored copies.
- Already-received views are **never re-requested**.
- The VLM is an observation extractor + hypothesis generator — it never
  produces a final diagnosis (WACV 2026 HARVEST-Vision: open VLMs ~39–65% on
  fine-grained disease ID → the dedicated ViT classifier is required).

## Run

```bash
uv sync --all-packages
uv run uvicorn image_service.app:app --reload
uv run pytest services/image-service -q
```
