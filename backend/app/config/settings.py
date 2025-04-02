from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    app_name: str = "Scheduler API"
    debug: bool = False
    version: str = "1.0.0"
    allowed_origins: List[str] = ["http://localhost:5173"]  # Vite's default port
    min_group_members: int = 2  # Minimum members required per group
    
    model_config = {
        "env_file": ".env"
    }

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings() 