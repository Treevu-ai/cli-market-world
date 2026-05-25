# ── CLI Market LATAM — Backend Dockerfile ──
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-spa && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

COPY market_server.py market_mcp.py market_cli.py market_stores.py market_core.py pyproject.toml collect_prices.py ./

RUN mkdir -p /data
ENV MARKET_DATA_DIR=/data

EXPOSE 8765

# shell form so $PORT is expanded at runtime
CMD python -m uvicorn market_server:app --host 0.0.0.0 --port $PORT
