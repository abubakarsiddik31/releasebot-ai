from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    GITHUB_TOKEN: str
    GITHUB_REPO: str
    OPENAI_API_KEY: str
    BREVO_API_KEY: str
    DATABASE_URL: str
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 