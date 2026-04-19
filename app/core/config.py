from functools import lru_cache
from typing import Any, Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# This module defines the application settings using Pydantic's BaseSettings.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", # Load environment variables from a .env file if it exists
        env_file_encoding="utf-8", #  Use UTF-8 encoding for the .env file
        extra="ignore", # Ignore any extra fields in the environment variables that are not defined in the Settings model
    )

    # App
    app_name: str = "E-Commerce API"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ecommerce_api"

    # JWT
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # Redis
    redis_url: str = "redis://localhost:6379"

    # CORS
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"]
    )

    # Stripe
    stripe_secret_key: str = "sk_test_change_me"
    stripe_webhook_secret: str = "whsec_change_me"

    # Brevo (formerly Sendinblue)
    brevo_api_key: str = "change-me"
    mail_from: str = "ahmedfaisal833@yahoo.com"

    http_only: bool = False  # Set to True in production for security


    # Normalize the CORS origins to ensure they are always returned as a list, even if provided as a comma-separated string
    @field_validator("cors_origins", mode="before") 
    @classmethod
    def parse_cors_origins(cls, value: Any) -> Any:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    # Normalize the debug value to ensure it can be set using various string representations of boolean values
    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug_value(cls, value: Any) -> Any:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug", "development", "dev"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "production", "prod"}:
                return False
        return value
    
    # Normalize the database URL to ensure compatibility with async drivers
    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
        return value


# Cache the settings instance to avoid reloading it multiple times
@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
