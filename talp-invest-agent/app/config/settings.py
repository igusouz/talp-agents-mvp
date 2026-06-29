from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path
    prompt_dir: Path
    audit_log_dir: Path
    llm_provider: str
    llm_model: str
    llm_base_url: str | None
    llm_api_key: str | None
    openrouter_http_referer: str | None
    openrouter_title: str
    llm_temperature: float
    llm_max_tokens: int
    llm_timeout_seconds: float
    llm_retries: int
    llm_thinking_budget: int | None
    backend: str


def _env_first(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value is not None and value.strip():
            return value.strip()
    return default


def _int_env_first(*names: str, default: int) -> int:
    raw = _env_first(*names)
    if raw is None:
        return default
    return int(raw)


def _float_env_first(*names: str, default: float) -> float:
    raw = _env_first(*names)
    if raw is None:
        return default
    return float(raw)


def _optional_int_env_first(*names: str, default: int | None = None) -> int | None:
    raw = _env_first(*names)
    if raw is None:
        return default
    return int(raw)


def _default_model(provider: str) -> str:
    if provider == "openrouter":
        return "google/gemini-2.5-flash"
    return "gemini-2.5-flash"


def _default_base_url(provider: str) -> str | None:
    if provider == "openrouter":
        return "https://openrouter.ai/api/v1"
    return None


def load_settings(project_root: Path | None = None) -> Settings:
    root = project_root or Path(__file__).resolve().parents[2]
    audit_dir = Path(os.getenv("TALP_AUDIT_LOG_DIR", root / "logs" / "audit"))
    if not audit_dir.is_absolute():
        audit_dir = root / audit_dir
    provider = _env_first(
        "INVEST_LLM_PROVIDER",
        "LLM_PROVIDER",
        "TALP_LLM_PROVIDER",
        default="gemini",
    ).lower()
    return Settings(
        project_root=root,
        prompt_dir=root / "prompts",
        audit_log_dir=audit_dir,
        llm_provider=provider,
        llm_model=_env_first(
            "INVEST_LLM_MODEL",
            "LLM_MODEL",
            "TALP_LLM_MODEL",
            default=_default_model(provider),
        ),
        llm_base_url=_env_first(
            "INVEST_LLM_BASE_URL",
            "LLM_BASE_URL",
            "TALP_LLM_BASE_URL",
            default=_default_base_url(provider),
        ),
        llm_api_key=_env_first(
            "INVEST_LLM_API_KEY",
            "LLM_API_KEY",
            "TALP_LLM_API_KEY",
        ),
        openrouter_http_referer=_env_first(
            "INVEST_OPENROUTER_HTTP_REFERER",
            "OPENROUTER_HTTP_REFERER",
            "TALP_OPENROUTER_HTTP_REFERER",
        ),
        openrouter_title=_env_first(
            "INVEST_OPENROUTER_TITLE",
            "OPENROUTER_TITLE",
            "TALP_OPENROUTER_TITLE",
            default="TALP Agents",
        ),
        llm_temperature=_float_env_first(
            "INVEST_LLM_TEMPERATURE",
            "LLM_TEMPERATURE",
            "TALP_LLM_TEMPERATURE",
            default=0.0,
        ),
        llm_max_tokens=_int_env_first(
            "INVEST_LLM_MAX_TOKENS",
            "LLM_MAX_TOKENS",
            "TALP_LLM_MAX_TOKENS",
            default=1024,
        ),
        llm_timeout_seconds=_float_env_first(
            "INVEST_LLM_TIMEOUT_SECONDS",
            "LLM_TIMEOUT_SECONDS",
            "TALP_LLM_TIMEOUT_SECONDS",
            default=45.0,
        ),
        llm_retries=_int_env_first(
            "INVEST_LLM_RETRIES",
            "LLM_RETRIES",
            "TALP_LLM_RETRIES",
            default=1,
        ),
        llm_thinking_budget=_optional_int_env_first(
            "INVEST_LLM_THINKING_BUDGET",
            "LLM_THINKING_BUDGET",
            "TALP_LLM_THINKING_BUDGET",
            default=0,
        ),
        backend=os.getenv("TALP_BACKEND", "llm"),
    )
