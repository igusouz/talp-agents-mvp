from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path
    prompt_dir: Path
    audit_log_dir: Path
    llm_model: str
    llm_max_tokens: int
    llm_timeout_seconds: float
    llm_retries: int
    llm_thinking_budget: int | None
    backend: str


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return int(raw)


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return float(raw)


def _optional_int_env(name: str, default: int | None = None) -> int | None:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return int(raw)


def load_settings(project_root: Path | None = None) -> Settings:
    root = project_root or Path(__file__).resolve().parents[2]
    audit_dir = Path(os.getenv("TALP_AUDIT_LOG_DIR", root / "logs" / "audit"))
    if not audit_dir.is_absolute():
        audit_dir = root / audit_dir
    return Settings(
        project_root=root,
        prompt_dir=root / "prompts",
        audit_log_dir=audit_dir,
        llm_model=os.getenv("TALP_LLM_MODEL", "gemini-2.5-flash"),
        llm_max_tokens=_int_env("TALP_LLM_MAX_TOKENS", 1024),
        llm_timeout_seconds=_float_env("TALP_LLM_TIMEOUT_SECONDS", 45.0),
        llm_retries=_int_env("TALP_LLM_RETRIES", 1),
        llm_thinking_budget=_optional_int_env("TALP_LLM_THINKING_BUDGET", 0),
        backend=os.getenv("TALP_BACKEND", "llm"),
    )
