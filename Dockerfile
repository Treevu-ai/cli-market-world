# ── CLI Market LATAM — Backend Dockerfile ──
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev tesseract-ocr tesseract-ocr-spa && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

COPY market_server.py market_mcp.py market_cli.py market_stores.py market_core.py server_deps.py pyproject.toml collect_prices.py ./
COPY routers/ ./routers/
COPY market_connectors/ ./market_connectors/

RUN mkdir -p /data
ENV MARKET_DATA_DIR=/data

EXPOSE 8765

# API only — collector runs as a separate Railway service (Dockerfile.collector)
CMD python -m uvicorn market_server:app --host 0.0.0.0 --port $PORT