#!/usr/bin/env bash
# Copy Observatory mirror files from cli-market-world → cli-market-backend.
# Usage (from cli-market-world):
#   BACKEND_DIR=../cli-market-backend ./ops/sync_backend_observatory_mirror.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORLD_DIR="${WORLD_DIR:-$ROOT}"
BACKEND_DIR="${BACKEND_DIR:-$ROOT/../cli-market-backend}"

MIRROR_FILES=(
  market_observatory.py
  routers/observatory.py
)

if [ ! -d "$BACKEND_DIR" ]; then
  echo "error: backend dir not found: $BACKEND_DIR" >&2
  exit 1
fi

changed=0
for rel in "${MIRROR_FILES[@]}"; do
  src="$WORLD_DIR/$rel"
  dst="$BACKEND_DIR/$rel"
  if [ ! -f "$src" ]; then
    echo "error: world missing $rel" >&2
    exit 1
  fi
  mkdir -p "$(dirname "$dst")"
  if [ -f "$dst" ] && cmp -s "$src" "$dst"; then
    echo "unchanged: $rel"
    continue
  fi
  cp "$src" "$dst"
  echo "synced: $rel"
  changed=1
done

if [ "$changed" -eq 0 ]; then
  echo "OK: backend observatory mirror already matches world"
else
  echo "OK: observatory mirror files updated in backend checkout"
fi
