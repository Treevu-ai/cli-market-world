# ── CLI Market LATAM — Backend Dockerfile ──
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev git tesseract-ocr tesseract-ocr-spa && rm -rf /var/lib/apt/lists/*

# Private cli-market-index clone during pip install.
# Railway: service variable GITHUB_TOKEN (or GH_PAT) must match ARG name for build-time inject.
ARG GITHUB_TOKEN
ARG GH_PAT

COPY requirements-railway.txt .
ARG CACHE_BUST=202606120341
RUN set -eux; \
    TOKEN="${GITHUB_TOKEN:-${GH_PAT:-}}"; \
    if [ -z "${TOKEN}" ]; then \
      echo "error: GITHUB_TOKEN (or GH_PAT) build arg required for private cli-market-index" >&2; \
      exit 1; \
    fi; \
    git config --global url."https://x-access-token:${TOKEN}@github.com/".insteadOf "https://github.com/"; \
    pip install --no-cache-dir -r requirements-railway.txt || { \
      echo "=== pip install failed — retrying verbose ===" >&2; \
      pip install -vvv --no-cache-dir -r requirements-railway.txt; \
      exit 1; \
    }; \
    rm -f /root/.gitconfig
COPY *.py pyproject.toml ./
COPY routers/ ./routers/
# Slack ops (cron panels, revenue/funnel routing from API)
COPY ops/billing_slack.py ops/slack_notify.py ops/load_env.py ops/command_control_daily.py ./ops/

RUN mkdir -p /data
ENV MARKET_DATA_DIR=/data

EXPOSE 8765

CMD ["sh", "-c", "python -m uvicorn market_server:app --host 0.0.0.0 --port $PORT"]