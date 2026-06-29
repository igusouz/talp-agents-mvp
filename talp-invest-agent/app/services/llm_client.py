from __future__ import annotations

import json
import os
from typing import Protocol

from app.config.settings import Settings
from app.schemas.models import BadStoryReport, InvestAnalysis
from app.services.prompt_registry import PromptTemplate

PLACEHOLDER_API_KEYS = frozenset(
    {
        "replace-me",
        "your-google-api-key-here",
    }
)


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


def _gemini_api_key() -> str:
    api_key = (
        os.getenv("INVEST_LLM_API_KEY")
        or os.getenv("LLM_API_KEY")
        or os.getenv("TALP_LLM_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
    )
    if not api_key:
        raise ValueError(
            "INVEST_LLM_API_KEY, LLM_API_KEY, TALP_LLM_API_KEY, GOOGLE_API_KEY "
            "or GEMINI_API_KEY must be set when TALP_BACKEND=llm"
        )

    _validate_api_key(api_key, "Gemini")

    return api_key


def _openrouter_api_key(explicit_api_key: str | None = None) -> str:
    api_key = (
        explicit_api_key
        or os.getenv("INVEST_LLM_API_KEY")
        or os.getenv("LLM_API_KEY")
        or os.getenv("TALP_LLM_API_KEY")
        or os.getenv("OPENROUTER_API_KEY")
    )
    if not api_key:
        raise ValueError(
            "INVEST_LLM_API_KEY, LLM_API_KEY, TALP_LLM_API_KEY or OPENROUTER_API_KEY "
            "must be set when LLM_PROVIDER=openrouter"
        )

    _validate_api_key(api_key, "OpenRouter")

    return api_key


def _validate_api_key(api_key: str, provider_name: str) -> None:
    if api_key.strip().lower() in PLACEHOLDER_API_KEYS:
        raise ValueError(f"{provider_name} API key is still set to a placeholder value")


def _build_gemini_chat_model(
    model_name: str,
    temperature: float,
    *,
    max_tokens: int | None = None,
    request_timeout: float | None = None,
    retries: int | None = None,
    thinking_budget: int | None = None,
):
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
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if request_timeout is not None:
        kwargs["request_timeout"] = request_timeout
    if retries is not None:
        kwargs["retries"] = retries
    if thinking_budget is not None:
        kwargs["thinking_budget"] = thinking_budget
    kwargs["google_api_key"] = _gemini_api_key()
    return ChatGoogleGenerativeAI(**kwargs)


def _build_openai_compatible_chat_model(
    model_name: str,
    temperature: float,
    *,
    base_url: str,
    api_key: str,
    max_tokens: int | None = None,
    request_timeout: float | None = None,
    retries: int | None = None,
    openrouter_http_referer: str | None = None,
    openrouter_title: str | None = None,
):
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError(
            "langchain-openai is required for OpenAI-compatible LLM providers"
        ) from exc

    default_headers = {}
    if openrouter_http_referer:
        default_headers["HTTP-Referer"] = openrouter_http_referer
    if openrouter_title:
        default_headers["X-OpenRouter-Title"] = openrouter_title

    kwargs = {
        "model": model_name,
        "base_url": base_url,
        "api_key": api_key,
        "temperature": temperature,
    }
    if request_timeout is not None:
        kwargs["timeout"] = request_timeout
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if retries is not None:
        kwargs["max_retries"] = retries
    if default_headers:
        kwargs["default_headers"] = default_headers
    return ChatOpenAI(**kwargs)


def _build_chat_model(settings: Settings, temperature: float):
    provider = settings.llm_provider.lower()
    if provider == "gemini":
        return _build_gemini_chat_model(
            settings.llm_model,
            temperature,
            max_tokens=settings.llm_max_tokens,
            request_timeout=settings.llm_timeout_seconds,
            retries=settings.llm_retries,
            thinking_budget=settings.llm_thinking_budget,
        )
    if provider == "openrouter":
        if not settings.llm_base_url:
            raise ValueError("LLM_BASE_URL must be set for OpenRouter")
        return _build_openai_compatible_chat_model(
            settings.llm_model,
            temperature,
            base_url=settings.llm_base_url,
            api_key=_openrouter_api_key(settings.llm_api_key),
            max_tokens=settings.llm_max_tokens,
            request_timeout=settings.llm_timeout_seconds,
            retries=settings.llm_retries,
            openrouter_http_referer=settings.openrouter_http_referer,
            openrouter_title=settings.openrouter_title,
        )
    raise ValueError("LLM_PROVIDER must be 'gemini' or 'openrouter'")


class LLMInvestAnalyzer:
    def __init__(self, settings: Settings, temperature: float = 0.0) -> None:
        self.model_name = settings.llm_model
        self._llm = _build_chat_model(settings, temperature)

    def analyze(self, user_story_text: str, prompt: PromptTemplate) -> InvestAnalysis:
        structured = self._llm.with_structured_output(InvestAnalysis)
        result = structured.invoke(prompt.format(user_story_text=user_story_text))
        parsed = getattr(result, "parsed", None)
        if parsed is not None:
            return InvestAnalysis.model_validate(parsed)
        return InvestAnalysis.model_validate(result)


class LLMReportGenerator:
    def __init__(self, settings: Settings, temperature: float = 0.0) -> None:
        self.model_name = settings.llm_model
        self._llm = _build_chat_model(settings, temperature)

    def generate(
        self,
        user_story_text: str,
        analysis: InvestAnalysis,
        prompt: PromptTemplate,
    ) -> BadStoryReport:
        structured = self._llm.with_structured_output(BadStoryReport)
        result = structured.invoke(
            prompt.format(
                user_story_text=user_story_text,
                invest_analysis_json=json.dumps(
                    analysis.model_dump(),
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            )
        )
        parsed = getattr(result, "parsed", None)
        if parsed is not None:
            return BadStoryReport.model_validate(parsed)
        return BadStoryReport.model_validate(result)


class GeminiInvestAnalyzer:
    def __init__(
        self,
        model_name: str,
        temperature: float = 0.0,
        *,
        max_tokens: int | None = None,
        request_timeout: float | None = None,
        retries: int | None = None,
        thinking_budget: int | None = None,
    ) -> None:
        self.model_name = model_name
        self._llm = _build_gemini_chat_model(
            model_name,
            temperature,
            max_tokens=max_tokens,
            request_timeout=request_timeout,
            retries=retries,
            thinking_budget=thinking_budget,
        )

    def analyze(self, user_story_text: str, prompt: PromptTemplate) -> InvestAnalysis:
        structured = self._llm.with_structured_output(InvestAnalysis)
        return structured.invoke(prompt.format(user_story_text=user_story_text))


class GeminiReportGenerator:
    def __init__(
        self,
        model_name: str,
        temperature: float = 0.0,
        *,
        max_tokens: int | None = None,
        request_timeout: float | None = None,
        retries: int | None = None,
        thinking_budget: int | None = None,
    ) -> None:
        self.model_name = model_name
        self._llm = _build_gemini_chat_model(
            model_name,
            temperature,
            max_tokens=max_tokens,
            request_timeout=request_timeout,
            retries=retries,
            thinking_budget=thinking_budget,
        )

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
