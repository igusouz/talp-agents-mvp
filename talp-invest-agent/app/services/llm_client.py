from __future__ import annotations

import json
import os
from typing import Protocol

from app.schemas.models import BadStoryReport, InvestAnalysis
from app.services.prompt_registry import PromptTemplate


class InvestAnalyzer(Protocol):
    model_name: str

    def analyze(self, user_story_text: str, prompt: PromptTemplate) -> InvestAnalysis:
        ...


class ReportGenerator(Protocol):
    model_name: str

    def generate(
        self,
        user_story_text: str,
        analysis: InvestAnalysis,
        prompt: PromptTemplate,
    ) -> BadStoryReport:
        ...


def _gemini_api_key() -> str | None:
    return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")


def _build_gemini_chat_model(model_name: str, temperature: float):
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as exc:
        raise RuntimeError(
            "langchain-google-genai is required for the llm backend"
        ) from exc

    kwargs = {
        "model": model_name,
        "temperature": temperature,
    }
    api_key = _gemini_api_key()
    if api_key:
        kwargs["google_api_key"] = api_key
    return ChatGoogleGenerativeAI(**kwargs)


class GeminiInvestAnalyzer:
    def __init__(self, model_name: str, temperature: float = 0.0) -> None:
        self.model_name = model_name
        self._llm = _build_gemini_chat_model(model_name, temperature)

    def analyze(self, user_story_text: str, prompt: PromptTemplate) -> InvestAnalysis:
        structured = self._llm.with_structured_output(InvestAnalysis)
        return structured.invoke(prompt.format(user_story_text=user_story_text))


class GeminiReportGenerator:
    def __init__(self, model_name: str, temperature: float = 0.0) -> None:
        self.model_name = model_name
        self._llm = _build_gemini_chat_model(model_name, temperature)

    def generate(
        self,
        user_story_text: str,
        analysis: InvestAnalysis,
        prompt: PromptTemplate,
    ) -> BadStoryReport:
        structured = self._llm.with_structured_output(BadStoryReport)
        return structured.invoke(
            prompt.format(
                user_story_text=user_story_text,
                invest_analysis_json=json.dumps(
                    analysis.model_dump(),
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            )
        )
