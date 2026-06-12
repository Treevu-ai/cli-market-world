#!/usr/bin/env bash
# Publish cli-market-core 1.9.34 (Observatory backport).
# Requires push access to Treevu-ai/cli-market-core and PYPI publish via tag CI.
#
# Usage:
#   ./ops/publish_core_1.9.34.sh [path-to-cli-market-core-clone]
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PATCH="$ROOT/ops/patches/cli-market-core-1.9.34.patch"
CORE_DIR="${1:-$ROOT/../cli-market-core}"
BRANCH="release/core-1.9.34"

if [[ ! -f "$PATCH" ]]; then
  echo "error: missing patch $PATCH" >&2
  exit 1
fi

if [[ ! -d "$CORE_DIR/.git" ]]; then
  echo "Cloning cli-market-core into $CORE_DIR ..."
  git clone https://github.com/Treevu-ai/cli-market-core.git "$CORE_DIR"
fi

cd "$CORE_DIR"
git fetch origin main
git checkout -B "$BRANCH" origin/main

if git apply --check "$PATCH" 2>/dev/null; then
  git apply "$PATCH"
else
  echo "Patch already applied or conflicts — review manually." >&2
  git apply "$PATCH" || true
fi

python3 -m pip install -q -e . pytest
python3 -m pytest tests/test_observatory.py -q -o addopts=

git add market_core/market_observatory.py market_core/market_stats.py pyproject.toml
git diff --cached --quiet && echo "Nothing to commit — already on 1.9.34?" && exit 0

git commit -m "release(core): 1.9.34 — Observatory backport from world mirror

- Sync market_observatory (tool normalization, internal filter, sqlite3.Row fix)
- PACKAGE_VERSION 1.9.34"

git push -u origin "$BRANCH"

PR_URL="$(gh pr create --repo Treevu-ai/cli-market-core \
  --base main --head "$BRANCH" \
  --title "release(core): 1.9.34 — Observatory backport" \
  --body "Automated from cli-market-world patch. Observatory nightly unblock + PACKAGE_VERSION fix.")"

echo "$PR_URL"
gh pr merge --repo Treevu-ai/cli-market-core --merge "$(basename "$PR_URL")"

git checkout main
git pull origin main
git tag v1.9.34
git push origin v1.9.34

echo "Tagged v1.9.34 — PyPI publish should run via publish-pypi.yml"
echo "Verify: pip index versions cli-market-core"
