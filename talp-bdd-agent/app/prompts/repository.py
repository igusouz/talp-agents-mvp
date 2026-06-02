"""Prompt repository for loading versioned QA prompt bundles."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PromptBundle:
    """Versioned prompt bundle for the QA analysis chain."""

    version: str
    system_prompt: str
    few_shots: str
    template: str

    def compose_system_prompt(self) -> str:
        """Combine the system prompt with few-shot guidance."""

        return f"{self.system_prompt}\n\n{self.few_shots}".strip()

    def render_human_prompt(self, story: str) -> str:
        """Render the human prompt template with the current story.

        Note: Acceptance criteria are expected to be present inside the
        `story` text and should be extracted by the chain when needed.
        """

        # Template may include an {acceptance_criteria} placeholder for
        # backwards compatibility; provide empty string if not available.
        try:
            return self.template.format(story=story, acceptance_criteria="").strip()
        except Exception:
            return self.template.format(story=story).strip()


class PromptRepository:
    """Load prompt files from the structured prompt directory tree."""

    def __init__(self, base_path: Path | None = None) -> None:
        self.base_path = base_path or Path(__file__).resolve().parent

    def load_bundle(self, name: str = "qa") -> PromptBundle:
        """Load a prompt bundle by name."""

        system_prompt = self._read_first_existing(
            self.base_path / "system" / f"{name}.md",
            self.base_path / f"{name}.md",
        )
        few_shots = self._read_first_existing(
            self.base_path / "few_shots" / f"{name}.md",
            self.base_path / f"few_shots_{name}.md",
        )
        template = self._read_first_existing(
            self.base_path / "templates" / f"{name}_analysis.md",
            self.base_path / f"{name}_analysis.md",
        )
        version = self._read_first_existing(
            self.base_path / "versions" / f"{name}_v1.md",
            self.base_path / f"{name}_v1.md",
        ).splitlines()[0].replace("Prompt version:", "").strip()

        return PromptBundle(
            version=version,
            system_prompt=system_prompt,
            few_shots=few_shots,
            template=template,
        )

    def _read_first_existing(self, *paths: Path) -> str:
        """Return the content of the first existing file path."""

        for path in paths:
            if path.exists():
                return path.read_text(encoding="utf-8").strip()
        raise FileNotFoundError(f"No prompt file found for candidates: {paths!r}")


def get_prompt_repository() -> PromptRepository:
    """Return the default prompt repository."""

    return PromptRepository()
