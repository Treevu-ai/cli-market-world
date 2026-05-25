# ── CLI Market LATAM — Backend Dockerfile ──
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY market_server.py market_mcp.py market_cli.py market_stores.py market_core.py pyproject.toml ./

RUN mkdir -p /data
ENV MARKET_DATA_DIR=/data

EXPOSE 8765

# exec form — signals (SIGTERM) reach uvicorn directly
CMD ["python", "-m", "uvicorn", "market_server:app", "--host", "0.0.0.0", "--port", "8765"]
