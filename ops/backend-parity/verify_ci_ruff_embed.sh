#!/usr/bin/env bash
# Fail if ops/backend-parity/ci.yml embedded ruff.toml drifts from ops/backend-parity/ruff.toml
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CI="$ROOT/ops/backend-parity/ci.yml"
TOML="$ROOT/ops/backend-parity/ruff.toml"
for needle in 'select = ["F", "E9", "W6", "B"]' "collect_prices.py" "market_server.py" ".deps/"; do
  grep -Fq "$needle" "$TOML" || { echo "missing in ruff.toml: $needle" >&2; exit 1; }
  grep -Fq "$needle" "$CI" || { echo "embedded ruff in ci.yml missing: $needle" >&2; exit 1; }
done
echo "OK: ci.yml embedded ruff matches ruff.toml anchors"
