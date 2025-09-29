# --- Etapa 1: Builder ---
# Usamos una imagen base de Python slim para reducir el tamaño.
FROM python:3.11-slim as builde

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copiamos solo el archivo de requerimientos del nuevo servicio
COPY container-images/content_service/requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Etapa 2: Final ---
# Creamos la imagen final a partir de una base limpia
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Copiamos las dependencias instaladas de la etapa de build
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiamos el código fuente del proyecto de content_service
COPY python/content_service/ .

# Exponemos el puerto en el que correrá la aplicación
EXPOSE 8080

# Comando para ejecutar el servidor de Uvicorn
# CMD ["uvicorn", "src.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
# CMD uvicorn src.server.app:app --host 0.0.0.0 --port $PORT
CMD ["bash","-lc","uvicorn src.server.app:app --host 0.0.0.0 --port ${PORT:-8080}"]