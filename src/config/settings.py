from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from pydantic import Field, validator

class Settings(BaseSettings):
    GITHUB_TOKEN: str = Field(..., description="GitHub personal access token")
    GITHUB_REPO: str = Field(..., description="Repository in format username/repo")
    OPENROUTER_API_KEY: str = Field(..., description="OpenRouter API key")
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", description="OpenRouter API base URL")
    OPENROUTER_MODEL: str = Field(default="anthropic/claude-3-opus-20240229", description="OpenRouter model to use")
    BREVO_API_KEY: str = Field(..., description="Brevo API key")
    DATABASE_URL: str = Field(..., description="MySQL connection string")
    DEBUG: bool = Field(default=False, description="Debug mode flag")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    ENVIRONMENT: str = Field(default="development", description="Environment (development/production)")

    @validator("GITHUB_REPO")
    def validate_github_repo(cls, v):
        if "/" not in v:
            raise ValueError("GITHUB_REPO must be in format username/repo")
        return v

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 