# --- Etapa 1: Builder ---
FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
    
WORKDIR /app
    
# Copiamos el archivo de requerimientos desde su ubicación original
COPY requirements.txt .
    
# Instalamos las dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
    
# --- Etapa 2: Final ---
FROM python:3.11-slim
    
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app
    
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

# Exponemos el puerto para el servicio
EXPOSE 8001

# Comando para ejecutar el servidor con recarga automática
CMD ["uvicorn", "src.server.app:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]