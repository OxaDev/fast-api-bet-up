from functools import lru_cache

from pydantic import BaseModel

from core import env


class Settings(BaseModel):
    app_env: str = env.APP_ENV
    database_url: str = env.DATABASE_URL


@lru_cache
def get_settings() -> Settings:
    return Settings()
