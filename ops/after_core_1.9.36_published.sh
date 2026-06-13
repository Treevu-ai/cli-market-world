#!/usr/bin/env bash
# Run in cli-market-world AFTER cli-market-core 1.9.36 is on PyPI.
set -euo pipefail

cd "$(dirname "$0")/.."

VER="1.9.36"
if ! curl -fsSL "https://pypi.org/pypi/cli-market-core/${VER}/json" >/dev/null 2>&1; then
  echo "error: cli-market-core $VER not on PyPI yet — run Publish cli-market-core (patch) workflow first" >&2
  exit 1
fi

sed -i "s/^version = \".*\"/version = \"$VER\"/" pyproject.toml
# pyproject min stays >=1.9.35 so pip install -e . works during PyPI propagation lag
sed -i 's/cli-market-core>=.*/cli-market-core>=1.9.35"/' pyproject.toml
sed -i "s/^cli-market-core==.*/cli-market-core==$VER/" requirements-railway.txt
sed -i 's/cli-market-core==1\.9\.[0-9]*/cli-market-core=='"$VER"'/g' .github/workflows/ci.yml
sed -i 's/cli-market-core>=1\.9\.[0-9]*/cli-market-core>='"$VER"'/g' .github/workflows/morning-ops-chain.yml
sed -i 's/cli-market-core>=1\.9\.[0-9]*/cli-market-core>='"$VER"'/g' .github/workflows/daily-briefing.yml
sed -i 's/cli-market-core>=1\.9\.[0-9]*/cli-market-core>='"$VER"'/g' .github/workflows/gtm-preflight.yml

BUST=$(date +%Y%m%d%H)
sed -i "s/^ARG CACHE_BUST=.*/ARG CACHE_BUST=$BUST/" Dockerfile

git add pyproject.toml requirements-railway.txt .github/workflows/ci.yml \
  .github/workflows/morning-ops-chain.yml .github/workflows/daily-briefing.yml \
  .github/workflows/gtm-preflight.yml Dockerfile
git commit -m "chore(release): pin cli-market-core==$VER; world $VER"
git push origin main

echo "Pushed world $VER — bump ops/backend-pin.trigger for backend sync."
