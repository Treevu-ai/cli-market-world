#!/usr/bin/env bash
# Setup cli-market-content at Ricardo's path (WSL/Linux).
set -euo pipefail

CONTENT_ROOT="/home/acuba/Proyectos/cli-market-content"
PRODUCT_ROOT="/home/acuba/Proyectos/nuevo"

cd "$PRODUCT_ROOT"

pick_python() {
  if [[ -x "$PRODUCT_ROOT/.venv/bin/python" ]]; then
    echo "$PRODUCT_ROOT/.venv/bin/python"
    return
  fi
  if [[ -x "$PRODUCT_ROOT/venv/bin/python" ]]; then
    echo "$PRODUCT_ROOT/venv/bin/python"
    return
  fi
  echo "python3"
}

PY="$(pick_python)"
PIP="${PY%/python}/pip"
if [[ ! -x "$PIP" ]]; then
  PIP="$PY -m pip"
fi

ensure_deps() {
  if "$PY" -c "from PIL import Image; import httpx" 2>/dev/null; then
    echo "OK: pillow + httpx ya disponibles ($PY)"
    return
  fi
  echo "Instalando pillow + httpx en entorno del proyecto…"
  if [[ -x "${PY%/python}/pip" ]]; then
    "${PY%/python}/pip" install pillow httpx -q
    return
  fi
  if [[ ! -d "$PRODUCT_ROOT/.venv" ]]; then
    python3 -m venv "$PRODUCT_ROOT/.venv"
    PY="$PRODUCT_ROOT/.venv/bin/python"
  fi
  "$PRODUCT_ROOT/.venv/bin/pip" install pillow httpx -q
  PY="$PRODUCT_ROOT/.venv/bin/python"
}

"$PY" ops/init_content_repo.py --target "$CONTENT_ROOT" --force
ensure_deps
# Re-resolve PY after possible venv creation
PY="$(pick_python)"

export CLI_MARKET_CONTENT_DIR="$CONTENT_ROOT"
"$PY" ops/sync_linkedin_metrics.py || true
"$PY" ops/generate_all_linkedin_assets.py --patch

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
echo "Python:     $PY"
