#!/usr/bin/env bash
# Run in cli-market-world AFTER cli-market-core 1.9.34 is on PyPI.
# Bumps pins, triggers Railway deploy, then publish world tag.
set -euo pipefail

cd "$(dirname "$0")/.."

VER="1.9.34"
if ! python3 -m pip index versions "cli-market-core" 2>/dev/null | grep -qE "(^|[[:space:]])${VER}([,[:space:]]|$)"; then
  echo "error: cli-market-core $VER not on PyPI yet" >&2
  exit 1
fi

sed -i "s/^version = \".*\"/version = \"$VER\"/" pyproject.toml
sed -i "s/cli-market-core>=.*/cli-market-core>=$VER\"/" pyproject.toml
sed -i "s/^cli-market-core==.*/cli-market-core==$VER/" requirements-railway.txt
sed -i "s/cli-market-core==.*/cli-market-core==$VER/" .github/workflows/observatory-nightly.yml

BUST=$(date +%Y%m%d%H)
sed -i "s/^ARG CACHE_BUST=.*/ARG CACHE_BUST=$BUST/" Dockerfile

git add pyproject.toml requirements-railway.txt .github/workflows/observatory-nightly.yml Dockerfile
git commit -m "chore(release): pin cli-market-core==$VER; world $VER"
git push origin main

echo "Pushed world $VER — Railway + PyPI workflows should follow."
