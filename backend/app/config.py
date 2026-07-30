from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://rtgs:changeme@db:5432/rtgs_dashboard"
    ANTHROPIC_API_KEY: str = "sk-ant-placeholder"
    CLAUDE_MODEL: str = "claude-haiku-4-5-20251001"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
