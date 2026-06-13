#!/usr/bin/env bash
# Sync CI test prerequisites from cli-market-world → cli-market-backend.
# Fixes: ModuleNotFoundError persistence (cli-market-index) + unknown integration mark.
#
# Usage:
#   BACKEND_DIR=../cli-market-backend ./ops/sync_backend_ci.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="${BACKEND_DIR:-$ROOT/../cli-market-backend}"
PARITY_DIR="$ROOT/ops/backend-parity"

if [ ! -d "$BACKEND_DIR" ]; then
  echo "error: backend dir not found: $BACKEND_DIR" >&2
  exit 1
fi

mkdir -p "$BACKEND_DIR/.github/workflows"

cp "$PARITY_DIR/pytest.ini" "$BACKEND_DIR/pytest.ini"
echo "synced: pytest.ini"

cp "$PARITY_DIR/ci.yml" "$BACKEND_DIR/.github/workflows/ci.yml"
echo "synced: .github/workflows/ci.yml"

if [ -f "$PARITY_DIR/INDEX_PIN" ]; then
  cp "$PARITY_DIR/INDEX_PIN" "$BACKEND_DIR/ops/INDEX_PIN" 2>/dev/null || true
fi

echo "OK: backend CI parity files updated"
