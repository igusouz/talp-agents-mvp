from __future__ import annotations

from functools import lru_cache

import httpx
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = Field(default="Workflow Orchestrator", validation_alias="ORCH_APP_NAME")
    app_version: str = Field(default="0.1.0", validation_alias="ORCH_APP_VERSION")
    api_prefix: str = Field(default="/api/v1", validation_alias="ORCH_API_PREFIX")
    log_level: str = Field(default="INFO", validation_alias="ORCH_LOG_LEVEL")
    user_agent: str = Field(
        default="talp-workflow-orchestrator/0.1.0",
        validation_alias="ORCH_USER_AGENT",
    )

    invest_agent_base_url: AnyHttpUrl = Field(
        default="http://invest-agent:8000/api/v1/invest",
        validation_alias="ORCH_INVEST_AGENT_BASE_URL",
    )
    compliance_agent_base_url: AnyHttpUrl = Field(
        default="http://compliance-agent:8000/api/v1/compliance",
        validation_alias="ORCH_COMPLIANCE_AGENT_BASE_URL",
    )
    bdd_agent_base_url: AnyHttpUrl = Field(
        default="http://bdd-agent:8000/api/v1/qa",
        validation_alias="ORCH_BDD_AGENT_BASE_URL",
    )

    request_timeout_seconds: float = Field(
        default=30.0,
        ge=0.1,
        validation_alias="ORCH_REQUEST_TIMEOUT_SECONDS",
    )
    connect_timeout_seconds: float = Field(
        default=5.0,
        ge=0.1,
        validation_alias="ORCH_CONNECT_TIMEOUT_SECONDS",
    )
    read_timeout_seconds: float = Field(
        default=25.0,
        ge=0.1,
        validation_alias="ORCH_READ_TIMEOUT_SECONDS",
    )
    write_timeout_seconds: float = Field(
        default=25.0,
        ge=0.1,
        validation_alias="ORCH_WRITE_TIMEOUT_SECONDS",
    )
    pool_timeout_seconds: float = Field(
        default=5.0,
        ge=0.1,
        validation_alias="ORCH_POOL_TIMEOUT_SECONDS",
    )

    retry_attempts: int = Field(default=3, ge=0, validation_alias="ORCH_RETRY_ATTEMPTS")
    retry_backoff_seconds: float = Field(
        default=0.5,
        ge=0.0,
        validation_alias="ORCH_RETRY_BACKOFF_SECONDS",
    )
    retry_max_backoff_seconds: float = Field(
        default=5.0,
        ge=0.0,
        validation_alias="ORCH_RETRY_MAX_BACKOFF_SECONDS",
    )
    retry_jitter_seconds: float = Field(
        default=0.2,
        ge=0.0,
        validation_alias="ORCH_RETRY_JITTER_SECONDS",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def build_timeout(settings: Settings) -> httpx.Timeout:
    return httpx.Timeout(
        timeout=settings.request_timeout_seconds,
        connect=settings.connect_timeout_seconds,
        read=settings.read_timeout_seconds,
        write=settings.write_timeout_seconds,
        pool=settings.pool_timeout_seconds,
    )
