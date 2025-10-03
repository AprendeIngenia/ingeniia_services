set -euo pipefail

# Alembic necesita DATABASE_URL en env (lo obtendremos de Secret Manager)
echo "[start] running alembic upgrade head..."
alembic upgrade head

echo "[start] launching uvicorn..."
exec uvicorn src.server.app:app --host 0.0.0.0 --port "${PORT:-8080}"
