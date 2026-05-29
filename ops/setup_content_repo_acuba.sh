#!/usr/bin/env bash
# Setup cli-market-content at Ricardo's path (WSL/Linux).
set -euo pipefail

CONTENT_ROOT="/home/acuba/Proyectos/cli-market-content"
PRODUCT_ROOT="/home/acuba/Proyectos/nuevo"

cd "$PRODUCT_ROOT"
python3 ops/init_content_repo.py --target "$CONTENT_ROOT" --force

export CLI_MARKET_CONTENT_DIR="$CONTENT_ROOT"
pip install pillow httpx -q
python3 ops/sync_linkedin_metrics.py || true
python3 ops/generate_all_linkedin_assets.py --patch

if [[ ! -d "$CONTENT_ROOT/.git" ]]; then
  git -C "$CONTENT_ROOT" init
  git -C "$CONTENT_ROOT" add .
  git -C "$CONTENT_ROOT" commit -m "Initial GTM content from cli-market-world template"
fi

echo ""
echo "Listo: $CONTENT_ROOT"
echo "export CLI_MARKET_CONTENT_DIR=$CONTENT_ROOT"
echo "Post día 1: $CONTENT_ROOT/linkedin/Day-01.md"
echo "Imagen:     $CONTENT_ROOT/linkedin/assets/day-01/day-01-linkedin.png"
