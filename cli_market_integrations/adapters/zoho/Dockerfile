FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" httpx python-dotenv
COPY cli_market_integrations/ ./cli_market_integrations/
ENV PYTHONPATH=/app
ENV SERVER_PORT=8080
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["uvicorn", "cli_market_integrations.adapters.zoho.app:app", "--host", "0.0.0.0", "--port", "8080"]
