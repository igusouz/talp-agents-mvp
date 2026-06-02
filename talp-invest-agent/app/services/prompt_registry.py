from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from app.schemas.models import PromptRecord


@dataclass(frozen=True)
class PromptTemplate:
    record: PromptRecord
    template: str
    metadata: dict[str, Any]

    def format(self, **kwargs: str) -> str:
        return self.template.format(**kwargs)


class PromptRegistry:
    def __init__(self, prompt_dir: Path) -> None:
        self.prompt_dir = prompt_dir

    def load(self, prompt_id: str, version: str) -> PromptTemplate:
        path = self.prompt_dir / f"{prompt_id}_v{version}.yaml"
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
        if not isinstance(data, dict):
            raise ValueError(f"Prompt file is invalid: {path}")
        if data.get("id") != prompt_id or str(data.get("version")) != version:
            raise ValueError(f"Prompt metadata mismatch: {path}")
        template = data.get("template")
        if not isinstance(template, str) or not template.strip():
            raise ValueError(f"Prompt template is missing: {path}")
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return PromptTemplate(
            record=PromptRecord(
                id=prompt_id,
                version=version,
                path=str(path),
                sha256=digest,
            ),
            template=template,
            metadata=data,
        )

