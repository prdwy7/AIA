"""HuggingFace model download helpers for the ASR runtime (docs/05 §2).

Two ASR models ship from HuggingFace:
- `ARTPARK-IISc/whisper-large-v3-vaani-telugu` — PRIMARY offline Telugu ASR
  (faster-whisper int8 on GPU).
- `ARTPARK-IISc/SraVaani-1.0` — FAST FALLBACK ASR (ONNX/FP16 on CPU).

Downloads are lazy (`huggingface_hub` is imported only when needed, from the
`[asr]` extra) and honor `KIOSK_MODELS_DIR` (default `~/.cache/kiosk/models`),
so an operator can pre-populate the edge cache via `scripts/download_models.sh`
before the device goes offline.
"""

from __future__ import annotations

import os

VAANI_REPO = "ARTPARK-IISc/whisper-large-v3-vaani-telugu"
SRAVAANI_REPO = "ARTPARK-IISc/SraVaani-1.0"

_DEFAULT_MODELS_DIR = "~/.cache/kiosk/models"


def models_dir() -> str:
    """Root directory for downloaded model artifacts (edge-local cache)."""
    return os.path.expanduser(os.environ.get("KIOSK_MODELS_DIR", _DEFAULT_MODELS_DIR))


def _snapshot(repo_id: str, local_dir: str) -> str:
    from huggingface_hub import snapshot_download

    os.makedirs(local_dir, exist_ok=True)
    return snapshot_download(repo_id=repo_id, local_dir=local_dir)


def download_vaani(local_dir: str | None = None) -> str:
    """Download Vaani-Whisper Telugu → returns the local model directory."""
    return _snapshot(VAANI_REPO, local_dir or os.path.join(models_dir(), "vaani-whisper-telugu"))


def download_sravaani(local_dir: str | None = None) -> str:
    """Download SraVaani-1.0 → returns the local model directory."""
    return _snapshot(SRAVAANI_REPO, local_dir or os.path.join(models_dir(), "sravaani-1.0"))
