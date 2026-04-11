"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal, Optional

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM ──────────────────────────────────────────────────────────────────
    anthropic_api_key: str = Field(..., description="Anthropic Claude API key")

    # ── Database ─────────────────────────────────────────────────────────────
    mongodb_uri: str = Field(..., description="MongoDB Atlas connection URI")
    supabase_url: AnyHttpUrl = Field(..., description="Supabase project URL")
    supabase_key: str = Field(..., description="Supabase service-role or anon key")

    # ── Instagram ─────────────────────────────────────────────────────────────
    instagram_app_id: str = Field(..., description="Instagram app ID")
    instagram_app_secret: str = Field(..., description="Instagram app secret")
    instagram_access_token: str = Field(..., description="Long-lived Instagram access token")

    # ── Facebook ──────────────────────────────────────────────────────────────
    facebook_app_id: str = Field(..., description="Facebook app ID")
    facebook_app_secret: str = Field(..., description="Facebook app secret")
    facebook_page_id: str = Field(..., description="Facebook page ID")
    facebook_page_access_token: Optional[str] = Field(
        None, description="Facebook page access token (can be obtained via OAuth)"
    )

    # ── YouTube ───────────────────────────────────────────────────────────────
    youtube_api_key: str = Field(..., description="YouTube Data API v3 key")
    youtube_client_id: str = Field(..., description="YouTube OAuth2 client ID")
    youtube_client_secret: str = Field(..., description="YouTube OAuth2 client secret")

    # ── Redis / Celery ────────────────────────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379/0")
    celery_broker_url: str = Field(default="redis://localhost:6379/1")
    celery_result_backend: str = Field(default="redis://localhost:6379/2")

    # ── Security ──────────────────────────────────────────────────────────────
    jwt_secret_key: str = Field(..., description="Secret key for signing JWTs")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=60)

    # ── Application ───────────────────────────────────────────────────────────
    api_base_url: AnyHttpUrl = Field(default="http://localhost:8000")
    frontend_url: AnyHttpUrl = Field(default="http://localhost:3000")
    environment: Literal["development", "staging", "production"] = Field(default="development")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")

    # ── Derived helpers ───────────────────────────────────────────────────────
    @field_validator("mongodb_uri")
    @classmethod
    def mongodb_uri_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("MONGODB_URI must not be empty")
        return v

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def instagram_graph_url(self) -> str:
        return "https://graph.instagram.com/v18.0"

    @property
    def facebook_graph_url(self) -> str:
        return "https://graph.facebook.com/v18.0"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
