"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PLACEHOLDER_API_KEYS = frozenset(
    {
        "replace-me",
        "your-google-api-key-here",
    }
)


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
    llm_provider: str = Field(
        default="gemini",
        validation_alias=AliasChoices("QA_LLM_PROVIDER", "LLM_PROVIDER", "TALP_LLM_PROVIDER"),
    )
    llm_model: str | None = Field(
        default=None,
        validation_alias=AliasChoices("QA_LLM_MODEL", "LLM_MODEL", "TALP_LLM_MODEL"),
    )
    llm_base_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("QA_LLM_BASE_URL", "LLM_BASE_URL", "TALP_LLM_BASE_URL"),
    )
    llm_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("QA_LLM_API_KEY", "LLM_API_KEY", "TALP_LLM_API_KEY"),
    )
    openrouter_api_key: str | None = Field(default=None, validation_alias="OPENROUTER_API_KEY")
    openrouter_http_referer: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "QA_OPENROUTER_HTTP_REFERER",
            "OPENROUTER_HTTP_REFERER",
            "TALP_OPENROUTER_HTTP_REFERER",
        ),
    )
    openrouter_title: str = Field(
        default="TALP Agents",
        validation_alias=AliasChoices(
            "QA_OPENROUTER_TITLE",
            "OPENROUTER_TITLE",
            "TALP_OPENROUTER_TITLE",
        ),
    )
    google_api_key: str | None = Field(default=None, validation_alias="GOOGLE_API_KEY")
    gemini_api_key: str | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    llm_temperature: float = Field(
        default=0.0,
        validation_alias=AliasChoices("QA_LLM_TEMPERATURE", "LLM_TEMPERATURE", "TALP_LLM_TEMPERATURE"),
    )
    llm_timeout_seconds: int = Field(
        default=60,
        validation_alias=AliasChoices("QA_LLM_TIMEOUT_SECONDS", "LLM_TIMEOUT_SECONDS", "TALP_LLM_TIMEOUT_SECONDS"),
    )

    @staticmethod
    def _default_model(provider: str) -> str:
        if provider == "openrouter":
            return "google/gemini-2.5-flash"
        return "gemini-2.5-flash"

    @staticmethod
    def _default_base_url(provider: str) -> str:
        if provider == "openrouter":
            return "https://openrouter.ai/api/v1"
        return "https://generativelanguage.googleapis.com/v1beta/openai"

    @model_validator(mode="after")
    def validate_llm_credentials(self) -> "Settings":
        self.llm_provider = self.llm_provider.strip().lower()
        if self.llm_provider not in {"gemini", "openrouter"}:
            raise ValueError("QA_LLM_PROVIDER, LLM_PROVIDER or TALP_LLM_PROVIDER must be 'gemini' or 'openrouter'")

        if not self.llm_model:
            self.llm_model = self._default_model(self.llm_provider)

        if not self.llm_base_url:
            self.llm_base_url = self._default_base_url(self.llm_provider)

        if not self.llm_api_key:
            if self.llm_provider == "openrouter":
                self.llm_api_key = self.openrouter_api_key
            else:
                self.llm_api_key = self.google_api_key or self.gemini_api_key

        if not self.llm_api_key:
            if self.llm_provider == "openrouter":
                raise ValueError("QA_LLM_API_KEY, LLM_API_KEY, TALP_LLM_API_KEY or OPENROUTER_API_KEY must be set")
            raise ValueError("QA_LLM_API_KEY, LLM_API_KEY, TALP_LLM_API_KEY, GOOGLE_API_KEY or GEMINI_API_KEY must be set")

        if self.llm_api_key.strip().lower() in PLACEHOLDER_API_KEYS:
            raise ValueError("LLM API key is still set to a placeholder value")

        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance for the application lifecycle."""

    return Settings()
