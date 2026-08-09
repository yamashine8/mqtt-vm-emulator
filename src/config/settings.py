from functools import lru_cache
from typing import Literal

from src.config.base_settings import AppBaseSettings


class Settings(AppBaseSettings):

    MODE: Literal["DEV", "TEST", "PROD"]
    AMQP_URL: str
    API_PORT: int

@lru_cache
def get_settings() -> Settings:
    return Settings()