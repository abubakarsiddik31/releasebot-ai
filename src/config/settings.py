from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    # Required fields with defaults
    GITHUB_TOKEN: str = Field(default="", description="GitHub personal access token")
    GITHUB_REPO: str = Field(default="", description="Repository in format username/repo")
    GITHUB_REPO_OWNER: str = Field(default="", description="GitHub repository owner")
    GITHUB_REPO_NAME: str = Field(default="", description="GitHub repository name")
    
    # Optional fields with defaults
    OPENROUTER_API_KEY: str = Field(default="", description="OpenRouter API key")
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", description="OpenRouter API base URL")
    OPENROUTER_MODEL: str = Field(default="anthropic/claude-3-opus-20240229", description="OpenRouter model to use")
    
    BREVO_API_KEY: str = Field(default="", description="Brevo API key")
    BREVO_SENDER_EMAIL: str = Field(default="", description="Brevo sender email address")
    BREVO_SENDER_NAME: str = Field(default="", description="Brevo sender name")
    
    # Database configuration
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5435/releasebot", description="PostgreSQL connection string")
    POSTGRES_USER: str = Field(default="", description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(default="", description="PostgreSQL password")
    POSTGRES_DB: str = Field(default="", description="PostgreSQL database name") 
    
    # Application settings
    APP_VERSION: str = Field(default="0.1.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode flag")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    ENVIRONMENT: str = Field(default="development", description="Environment (development/production)")
    CORS_ORIGINS: list[str] = Field(
        default=["*"],
        description="List of allowed CORS origins. Defaults to ['*'] for development.",
    )
    API_BASE_URL: str = Field(default="http://localhost:8000", description="Base URL for API")

    @classmethod
    @validator("GITHUB_REPO")
    def validate_github_repo(cls, v, values):
        if v and "/" not in v:  # Only validate if value is provided
            raise ValueError("GITHUB_REPO must be in format username/repo")
        return v
        
    @classmethod
    @validator('GITHUB_REPO_OWNER', 'GITHUB_REPO_NAME', always=True)
    def set_github_repo_parts(cls, v, values, field):
        if field.name == 'GITHUB_REPO_OWNER' and not v and 'GITHUB_REPO' in values and values['GITHUB_REPO']:
            return values['GITHUB_REPO'].split('/')[0]
        if field.name == 'GITHUB_REPO_NAME' and not v and 'GITHUB_REPO' in values and values['GITHUB_REPO']:
            return values['GITHUB_REPO'].split('/')[-1]
        return v

    @classmethod
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        if not v:  # If empty, return default
            return "INFO"
        v = v.upper()
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v not in valid_levels:
            return "INFO"  # Default to INFO for invalid levels
        return v
        
    @classmethod
    @validator("CORS_ORIGINS", pre=True)
    def validate_cors_origins(cls, v):
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v or ["*"]  # Default to ["*"] if not provided or empty

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 