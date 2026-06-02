"""LangChain workflow for BDD QA analysis."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from openai import RateLimitError

from app.core.config import Settings, get_settings
from app.core.exceptions import UpstreamRateLimitError
from app.prompts.repository import PromptBundle, get_prompt_repository
from app.schemas.qa import QAAnalysisResponse, QARequest

logger = logging.getLogger(__name__)
PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
PROMPT_REPOSITORY = get_prompt_repository()


def _load_prompt(name: str) -> str:
    """Load a prompt file from the prompts directory.

    This preserves a small compatibility helper for tests while the
    implementation uses the structured prompt repository internally.
    """

    legacy_candidates = {
        "system.md": [PROMPTS_DIR / "system" / "qa.md", PROMPTS_DIR / "system.md"],
        "few_shots.md": [PROMPTS_DIR / "few_shots" / "qa.md", PROMPTS_DIR / "few_shots.md"],
    }
    candidates = legacy_candidates.get(name, [PROMPTS_DIR / name])

    for path in candidates:
        if path.exists():
            return path.read_text(encoding="utf-8").strip()

    raise FileNotFoundError(f"Prompt file not found: {name}")


def _format_acceptance_criteria(criteria: list[str]) -> str:
    """Convert criteria into a compact prompt-friendly block."""

    if not criteria:
        return "No acceptance criteria provided."

    return "\n".join(f"- {item}" for item in criteria)


def _extract_acceptance_criteria_from_story(story: str) -> list[str]:
    """Attempt to extract acceptance criteria from the story text.

    Heuristics:
    - If a section header like 'Acceptance criteria:' exists, collect following
      lines that start with '-' until a blank line.
    - Collect any lines starting with '- ' anywhere in the story as fallback.
    """
    lines = [ln.rstrip() for ln in story.splitlines()]
    criteria: list[str] = []

    # Look for explicit 'Acceptance' header
    for i, ln in enumerate(lines):
        if ln.lower().strip().startswith("acceptance criteria") or ln.lower().strip().startswith("acceptance:"):
            # collect subsequent lines that look like list items
            for sub in lines[i + 1 :]:
                if not sub.strip():
                    break
                if sub.strip().startswith("-"):
                    criteria.append(sub.strip().lstrip("- "))
            if criteria:
                return criteria

    # Fallback: collect any '- ' prefixed lines anywhere
    for ln in lines:
        stripped = ln.strip()
        if stripped.startswith("-"):
            criteria.append(stripped.lstrip("- "))

    return criteria


class QAAnalysisChain:
    """Encapsulates the structured analysis workflow."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._prompts: PromptBundle = PROMPT_REPOSITORY.load_bundle("qa")
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "{system_prompt}"),
                (
                    "human",
                    "{human_prompt}",
                ),
            ]
        )
        self._llm = ChatOpenAI(
            model=self.settings.llm_model,
            base_url=self.settings.llm_base_url,
            api_key=self.settings.llm_api_key,
            temperature=self.settings.llm_temperature,
            timeout=self.settings.llm_timeout_seconds,
        )
        self._chain = self._prompt | self._llm.with_structured_output(QAAnalysisResponse)

    def invoke(self, request: QARequest) -> QAAnalysisResponse:
        """Run the QA analysis workflow for one user story."""

        logger.info(
            "Running QA analysis using prompt_version=%s story_length=%s",
            self._prompts.version,
            len(request.story),
        )
        payload = {
            "system_prompt": self._prompts.compose_system_prompt(),
            "human_prompt": self._prompts.render_human_prompt(
                story=request.story.strip(),
            ),
            "story": request.story.strip(),
        }
        try:
            return self._chain.invoke(payload)
        except RateLimitError as exc:
            logger.warning(
                "QA analysis rate-limited by upstream provider for prompt_version=%s",
                self._prompts.version,
            )
            raise UpstreamRateLimitError(
                "LLM provider is rate-limited right now. Please retry in a few seconds."
            ) from exc
        except Exception:
            logger.exception("QA analysis failed for prompt_version=%s", self._prompts.version)
            raise


@lru_cache(maxsize=1)
def get_qa_chain() -> QAAnalysisChain:
    """Return a cached chain instance for reuse across requests."""

    return QAAnalysisChain()
