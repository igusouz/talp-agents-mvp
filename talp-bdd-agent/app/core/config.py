"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings for the FastAPI application and LLM client."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = Field(default="BDD QA Agent", validation_alias="QA_APP_NAME")
    app_version: str = Field(default="0.1.0", validation_alias="QA_APP_VERSION")
    api_prefix: str = Field(default="/api/v1", validation_alias="QA_API_PREFIX")
    log_level: str = Field(default="INFO", validation_alias="QA_LOG_LEVEL")
    llm_model: str = Field(default="gpt-4o-mini", validation_alias="QA_LLM_MODEL")
    llm_base_url: str | None = Field(default=None, validation_alias="QA_LLM_BASE_URL")
    llm_api_key: str | None = Field(default=None, validation_alias="QA_LLM_API_KEY")
    llm_temperature: float = Field(default=0.0, validation_alias="QA_LLM_TEMPERATURE")
    llm_timeout_seconds: int = Field(default=60, validation_alias="QA_LLM_TIMEOUT_SECONDS")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance for the application lifecycle."""

    return Settings()
