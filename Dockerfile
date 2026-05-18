# ── CLI Market LATAM — Backend Dockerfile ──
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY market_server.py market_mcp.py market_cli.py market_stores.py pyproject.toml ./

RUN mkdir -p /data
ENV MARKET_DATA_DIR=/data
ENV HOST=0.0.0.0
ENV PORT=8765

EXPOSE 8765

CMD ["sh", "-c", "python -m uvicorn market_server:app --host 0.0.0.0 --port ${PORT:-8765}"]
