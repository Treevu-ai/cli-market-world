# syntax=docker/dockerfile:1
# ── CLI Market LATAM — Backend Dockerfile ──
FROM python:3.12-slim

WORKDIR /app

# tesseract: OCR fallback for price extraction; gcc + libpq-dev: psycopg2-binary build.
# git: required for pip install from private GitHub (cli-market-index).
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev git tesseract-ocr tesseract-ocr-spa \
    && rm -rf /var/lib/apt/lists/*

# Private cli-market-index clone during pip install.
# Fly.io: pass via `fly deploy --build-secret github_token=$GITHUB_TOKEN` — never as --build-arg
# (build args get persisted in plaintext in `fly config show`; secret mounts don't).
COPY requirements.txt .
ARG CACHE_BUST=2026-06-23-core-1.11.0
RUN --mount=type=secret,id=github_token set -eux; \
    TOKEN="$(cat /run/secrets/github_token 2>/dev/null || true)"; \
    if [ -z "${TOKEN}" ]; then \
      echo "BUILD FAILED: pass --build-secret github_token=<PAT> to fly deploy (read Treevu-ai/cli-market-index)." >&2; \
      exit 1; \
    fi; \
    git config --global url."https://x-access-token:${TOKEN}@github.com/".insteadOf "https://github.com/"; \
    if ! pip install --no-cache-dir -r requirements.txt; then \
      echo "BUILD FAILED: pip install — core pin must exist on PyPI; index clone needs valid github_token secret" >&2; \
      pip install -vvv --no-cache-dir -r requirements.txt 2>&1 | tail -100 || true; \
      exit 1; \
    fi; \
    rm -f /root/.gitconfig

# Install Chromium and system dependencies for Playwright (VTEX scraping fallback).
# --with-deps uses apt-get to install required shared libraries.
RUN python -m playwright install chromium --with-deps

COPY *.py pyproject.toml ./
COPY routers/ ./routers/
# Slack ops (cron panels, revenue/funnel routing from API)
COPY ops/billing_slack.py ops/slack_notify.py ops/load_env.py ops/command_control_daily.py ./ops/

RUN mkdir -p /data
ENV MARKET_DATA_DIR=/data

EXPOSE 8765

CMD ["sh", "-c", "python -m uvicorn market_server:app --host 0.0.0.0 --port $PORT"]