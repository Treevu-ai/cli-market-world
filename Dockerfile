# ── CLI Market LATAM — Backend Dockerfile ──
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev git tesseract-ocr tesseract-ocr-spa && rm -rf /var/lib/apt/lists/*

# Private cli-market-index clone during pip install.
# Railway → API service → Variables: GITHUB_TOKEN (PAT with repo scope on cli-market-index).
ARG GITHUB_TOKEN

COPY requirements-railway.txt .
RUN set -eux; \
    if [ -z "${GITHUB_TOKEN}" ]; then \
      echo "error: GITHUB_TOKEN build arg required for private cli-market-index (git+https)" >&2; \
      exit 1; \
    fi; \
    git config --global url."https://x-access-token:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"; \
    pip install --no-cache-dir -r requirements-railway.txt; \
    rm -f /root/.gitconfig

ARG CACHE_BUST=1
COPY *.py pyproject.toml ./
COPY routers/ ./routers/
# Slack ops (cron panels, revenue/funnel routing from API)
COPY ops/billing_slack.py ops/slack_notify.py ops/load_env.py ops/command_control_daily.py ./ops/

RUN mkdir -p /data
ENV MARKET_DATA_DIR=/data

EXPOSE 8765

CMD ["sh", "-c", "python -m uvicorn market_server:app --host 0.0.0.0 --port $PORT"]