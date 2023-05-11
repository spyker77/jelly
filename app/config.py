import logging
from functools import lru_cache

from pydantic import BaseSettings

logger = logging.getLogger("gunicorn.error")


class Settings(BaseSettings):
    mongodb_database: str
    mongodb_url: str
    elasticsearch_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    logger.info("Loading config settings from the environment...")
    return Settings()
