# ── CLI Market LATAM — Backend Dockerfile ──
#
# Base: official Playwright Python image — ships Chromium + all system deps.
# Needed for the VTEX Cloudflare-bypass fallback (collect_prices.py).
# Python version: 3.11 (matches jammy tag; project requires >=3.10).
#
# To use a newer Playwright version, update the tag here AND in
# requirements-railway.txt (playwright>=X.Y.Z).
FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

WORKDIR /app

# tesseract: OCR fallback for price extraction; gcc + libpq-dev: psycopg2-binary build.
# git: required for pip install from private GitHub (cli-market-index).
# The playwright base image is Ubuntu jammy — apt-get works normally.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev git tesseract-ocr tesseract-ocr-spa \
    && rm -rf /var/lib/apt/lists/*

# Private cli-market-index clone during pip install.
# Railway: service variable GITHUB_TOKEN (or GH_PAT) must match ARG name for build-time inject.
ARG GITHUB_TOKEN
ARG GH_PAT

COPY requirements-railway.txt .
ARG CACHE_BUST=202606171200
RUN set -eux; \
    TOKEN="${GITHUB_TOKEN:-${GH_PAT:-}}"; \
    if [ -z "${TOKEN}" ]; then \
      echo "BUILD FAILED: set GITHUB_TOKEN or GH_PAT on the Railway API service (read Treevu-ai/cli-market-index). See ops/RAILWAY_DEPLOY.md" >&2; \
      exit 1; \
    fi; \
    git config --global url."https://x-access-token:${TOKEN}@github.com/".insteadOf "https://github.com/"; \
    if ! pip install --no-cache-dir -r requirements-railway.txt; then \
      echo "BUILD FAILED: pip install — core pin must exist on PyPI; index clone needs valid GITHUB_TOKEN/GH_PAT" >&2; \
      pip install -vvv --no-cache-dir -r requirements-railway.txt 2>&1 | tail -100 || true; \
      exit 1; \
    fi; \
    rm -f /root/.gitconfig

# Install Chromium browser binaries into the expected cache path.
# The playwright base image ships the binaries already; this RUN is a safety
# net in case pip upgrades playwright to a version with a different browser
# revision hash. It's a no-op if the binaries are already present.
RUN python -m playwright install chromium --with-deps

COPY *.py pyproject.toml ./
COPY routers/ ./routers/
# Slack ops (cron panels, revenue/funnel routing from API)
COPY ops/billing_slack.py ops/slack_notify.py ops/load_env.py ops/command_control_daily.py ./ops/

RUN mkdir -p /data
ENV MARKET_DATA_DIR=/data

EXPOSE 8765

CMD ["sh", "-c", "python -m uvicorn market_server:app --host 0.0.0.0 --port $PORT"]