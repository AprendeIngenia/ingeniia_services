# alembic/env.py
import os
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# Importa metadata de tus modelos
from src.core.database import Base
from src.models.user import User, EmailVerificationToken, RefreshToken

# Config de Alembic
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata para autogenerate
target_metadata = Base.metadata


def _resolve_db_url() -> str:
    """Resuelve la URL de DB desde -x db_url, env var o alembic.ini."""
    xargs = context.get_x_argument(as_dictionary=True)
    url = (xargs or {}).get("db_url") or os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")

    if not url:
        raise RuntimeError("DATABASE_URL no está definida y 'sqlalchemy.url' en alembic.ini está vacío.")

    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    return url


DB_URL = _resolve_db_url()
config.set_main_option("sqlalchemy.url", DB_URL)


def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo 'offline'."""
    context.configure(
        url=DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Ejecuta migraciones en modo 'online' (async)."""
    engine = create_async_engine(DB_URL, poolclass=pool.NullPool)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
