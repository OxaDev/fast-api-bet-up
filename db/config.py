from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=(settings.app_env == "development"))
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[Any, Any]:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    # Création automatique des tables (pré-prod / demo)
    # En prod, privilégiez Alembic pour les migrations.
    from core import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
