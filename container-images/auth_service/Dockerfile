# --- Stage 1: builder ---
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copia SOLO requirements para cachear mejor
COPY container-images/auth_service/requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential && rm -rf /var/lib/apt/lists/*

# --- Stage 2: final ---
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY --from=builder /usr/local /usr/local

# Copia el código del servicio
COPY python/auth_service/ /app/

# Script de arranque: migraciones + uvicorn con $PORT
COPY container-images/auth_service/start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8080
CMD ["/app/start.sh"]