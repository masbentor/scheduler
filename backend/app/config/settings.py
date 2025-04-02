from pydantic import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Scheduler"
    version: str = "1.0.0"
    allowed_origins: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()