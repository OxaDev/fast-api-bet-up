import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from core import env
from db.config import Base

# region Models import for migrations
from db.models.cryptos import CryptoCurrency, CryptoPrice  # noqa

# endregion

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", env.DATABASE_URL)


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


asyncio.run(run_migrations_online())
