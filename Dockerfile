# ── CLI Market LATAM — Backend Dockerfile ──
FROM python:3.12-slim

WORKDIR /app

# cli-market-core from PyPI (requirements-railway.txt).
COPY requirements-railway.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev tesseract-ocr tesseract-ocr-spa && rm -rf /var/lib/apt/lists/*

# Install the shared core (and its transitive deps) from PyPI.
RUN pip install --no-cache-dir -r requirements-railway.txt

ARG CACHE_BUST=1
COPY *.py pyproject.toml ./
COPY routers/ ./routers/

RUN mkdir -p /data
ENV MARKET_DATA_DIR=/data

EXPOSE 8765

CMD ["sh", "-c", "python -m uvicorn market_server:app --host 0.0.0.0 --port $PORT"]
