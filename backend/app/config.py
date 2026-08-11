from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL: str = "claude-haiku-4-5-20251001"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3007"]

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
