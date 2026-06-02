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
    )
