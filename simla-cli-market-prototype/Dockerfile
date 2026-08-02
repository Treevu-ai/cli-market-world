FROM python:3.12-slim

WORKDIR /app

# Deps primero para cachear mejor
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código fuente
COPY src/ ./src/
COPY config/ ./config/

# Logs dir (la app lo crea, pero lo precreamos por si acaso)
RUN mkdir -p logs

ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=8080
ENV LOG_LEVEL=INFO
ENV PYTHONIOENCODING=utf-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["uvicorn", "src.simla_middleware:app", "--host", "0.0.0.0", "--port", "8080"]
