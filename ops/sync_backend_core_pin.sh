#!/usr/bin/env bash
# Bump cli-market-core pin in cli-market-backend/requirements.txt
# Usage (from cli-market-world):
#   BACKEND_DIR=../cli-market-backend ./ops/sync_backend_core_pin.sh 1.9.34
set -euo pipefail

VER="${1:-1.9.35}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="${BACKEND_DIR:-$ROOT/../cli-market-backend}"
REQ="$BACKEND_DIR/requirements.txt"

if [ ! -f "$REQ" ]; then
  echo "error: backend requirements not found: $REQ" >&2
  echo "Set BACKEND_DIR or checkout Treevu-ai/cli-market-backend" >&2
  exit 1
fi

if ! python3 -m pip index versions "cli-market-core" 2>/dev/null | grep -qE "(^|[[:space:]])${VER}([,[:space:]]|$)"; then
  echo "error: cli-market-core ${VER} not on PyPI yet" >&2
  exit 1
fi

if grep -qE '^cli-market-core>=' "$REQ"; then
  sed -i "s/^cli-market-core>=.*/cli-market-core>=${VER}/" "$REQ"
elif grep -qE '^cli-market-core==' "$REQ"; then
  sed -i "s/^cli-market-core==.*/cli-market-core>=${VER}/" "$REQ"
else
  echo "cli-market-core>=${VER}" >> "$REQ"
fi

echo "Updated $REQ → cli-market-core>=${VER}"
grep '^cli-market-core' "$REQ"
