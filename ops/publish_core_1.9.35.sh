#!/usr/bin/env bash
# Publish cli-market-core 1.9.35 (observatory_snapshot_streak).
# Requires push access to Treevu-ai/cli-market-core and PYPI publish via tag CI.
#
# Usage:
#   ./ops/publish_core_1.9.35.sh [path-to-cli-market-core-clone]
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PATCH="$ROOT/ops/patches/cli-market-core-1.9.35.patch"
CORE_DIR="${1:-$ROOT/../cli-market-core}"
BRANCH="release/core-1.9.35"
VER="1.9.35"

if [[ ! -f "$PATCH" ]]; then
  echo "error: missing patch $PATCH" >&2
  exit 1
fi

if [[ ! -d "$CORE_DIR/.git" ]]; then
  echo "Cloning cli-market-core into $CORE_DIR ..."
  git clone https://github.com/Treevu-ai/cli-market-core.git "$CORE_DIR"
fi

cd "$CORE_DIR"
git fetch origin main --tags
git checkout -B "$BRANCH" origin/main

if ! git rev-parse "v1.9.34" >/dev/null 2>&1; then
  git tag "v1.9.34" origin/main
  git push origin "v1.9.34" || echo "warn: could not push v1.9.34 tag"
fi

git apply --check "$PATCH"
git apply "$PATCH"

python3 -m pip install -q -e . pytest
python3 -m pytest tests/test_observatory.py -q -o addopts=

git add market_core/market_observatory.py market_core/market_stats.py pyproject.toml tests/test_observatory.py
git diff --cached --quiet && echo "Nothing to commit — already on ${VER}?" && exit 0

git commit -m "release(core): ${VER} — observatory_snapshot_streak

- Export observatory_snapshot_streak for daily snapshot streak gate
- PACKAGE_VERSION ${VER}"

git push -u origin "$BRANCH"

PR_URL="$(gh pr create --repo Treevu-ai/cli-market-core \
  --base main --head "$BRANCH" \
  --title "release(core): ${VER} — observatory_snapshot_streak" \
  --body "Automated from cli-market-world patch ops/patches/cli-market-core-1.9.35.patch.")"

echo "$PR_URL"
gh pr merge --repo Treevu-ai/cli-market-core --merge "$(basename "$PR_URL")"

git checkout main
git pull origin main
git tag "v${VER}"
git push origin "v${VER}"

echo "Tagged v${VER} — run Actions → Publish cli-market-core (patch) with version ${VER} if PyPI not auto-published"
