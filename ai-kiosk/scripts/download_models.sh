#!/usr/bin/env bash
# Download the ASR models from HuggingFace (docs/05 §2).
#
#   Vaani-Whisper Telugu (PRIMARY, faster-whisper int8):
#     ARTPARK-IISc/whisper-large-v3-vaani-telugu
#   SraVaani-1.0 (FAST FALLBACK, ONNX/FP16):
#     ARTPARK-IISc/SraVaani-1.0
#
# Usage: ./scripts/download_models.sh   (== make download-models)
#   KIOSK_MODELS_DIR  override the cache dir (default ~/.cache/kiosk/models)
#   HF_ENDPOINT       optional HuggingFace mirror
set -euo pipefail

VAANI_REPO="ARTPARK-IISc/whisper-large-v3-vaani-telugu"
SRAVAANI_REPO="ARTPARK-IISc/SraVaani-1.0"

MODELS_DIR="${KIOSK_MODELS_DIR:-$HOME/.cache/kiosk/models}"

if command -v hf >/dev/null 2>&1; then
  CLI=(hf download)
elif command -v huggingface-cli >/dev/null 2>&1; then
  CLI=(huggingface-cli download)
elif command -v python >/dev/null 2>&1; then
  CLI=(python -c "import sys,huggingface_hub;huggingface_hub.snapshot_download(sys.argv[1], local_dir=sys.argv[-1])")
else
  echo "ERROR: install huggingface_hub (uv sync --active --extra asr -p services/speech-service)" >&2
  exit 1
fi

mkdir -p "$MODELS_DIR/vaani-whisper-telugu" "$MODELS_DIR/sravaani-1.0"

echo "==> [1/2] Vaani-Whisper Telugu (primary): $VAANI_REPO"
"${CLI[@]}" "$VAANI_REPO" --local-dir "$MODELS_DIR/vaani-whisper-telugu"

echo "==> [2/2] SraVaani-1.0 (fast fallback): $SRAVAANI_REPO"
"${CLI[@]}" "$SRAVAANI_REPO" --local-dir "$MODELS_DIR/sravaani-1.0"

cat <<EOF

Downloaded ASR models to: $MODELS_DIR
  vaani-whisper-telugu/   -> ASR primary
  sravaani-1.0/           -> ASR fast fallback (ONNX)

The speech-service engines lazy-load from this cache (KIOSK_MODELS_DIR) or
download on first use. Heavy runtimes: uv sync --active --extra asr -p services/speech-service
EOF
