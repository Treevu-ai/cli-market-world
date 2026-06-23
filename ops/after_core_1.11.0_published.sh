#!/usr/bin/env bash
# Run in cli-market-world AFTER cli-market-core 1.11.0 is on PyPI.
set -euo pipefail

cd "$(dirname "$0")/.."

VER="1.11.0"
if ! python3 -m pip index versions "cli-market-core" 2>/dev/null | grep -qE "(^|[[:space:]])${VER}([,[:space:]]|$)"; then
  echo "error: cli-market-core $VER not on PyPI yet — publish first (core Publish PyPI or world publish-core-pypi)" >&2
  exit 1
fi

sed -i "s/^version = \".*\"/version = \"$VER\"/" pyproject.toml
sed -i "s/cli-market-core>=.*/cli-market-core>=$VER\"/" pyproject.toml
sed -i 's/^cli-market-core @ git+.*/cli-market-core=='"$VER"'/' requirements-railway.txt
sed -i 's/^cli-market-core==.*/cli-market-core=='"$VER"'/' requirements-railway.txt
sed -i 's|cli-market-core @ git+https://[^"]*|cli-market-core=='"$VER"'|g' .github/workflows/ci.yml
sed -i 's/cli-market-core==[0-9.]\+/cli-market-core=='"$VER"'/g' .github/workflows/ci.yml

sed -i "s/^ARG CACHE_BUST=.*/ARG CACHE_BUST=2026-06-23-core-${VER}/" Dockerfile

python3 ops/verify_railway_core_pin.py

git add pyproject.toml requirements-railway.txt .github/workflows/ci.yml Dockerfile
git commit -m "chore(release): pin cli-market-core==${VER} (PyPI, was @8469854)"
git push origin main

echo "Pushed world pin ${VER} — Railway redeploy + bump ops/backend-pin.trigger for backend sync."
