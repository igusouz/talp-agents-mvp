"""Tests for environment-based settings resolution."""

from __future__ import annotations

import pytest

from app.core.config import Settings


def test_google_api_key_fallback_is_used(monkeypatch: pytest.MonkeyPatch) -> None:
    """GOOGLE_API_KEY should populate llm_api_key when QA_LLM_API_KEY is missing."""

    monkeypatch.delenv("QA_LLM_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    settings = Settings(
        _env_file=None,
        GOOGLE_API_KEY="test-google-key",
        QA_LLM_API_KEY=None,
    )

    assert settings.llm_api_key == "test-google-key"


def test_gemini_api_key_fallback_is_used(monkeypatch: pytest.MonkeyPatch) -> None:
    """GEMINI_API_KEY should be accepted as a legacy Gemini alias."""

    monkeypatch.delenv("QA_LLM_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    settings = Settings(
        _env_file=None,
        GEMINI_API_KEY="test-gemini-key",
        GOOGLE_API_KEY=None,
        QA_LLM_API_KEY=None,
    )

    assert settings.llm_api_key == "test-gemini-key"


def test_qa_llm_api_key_takes_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    """QA_LLM_API_KEY should remain available as a BDD-specific override."""

    monkeypatch.delenv("QA_LLM_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    settings = Settings(
        _env_file=None,
        QA_LLM_API_KEY="test-qa-key",
        GOOGLE_API_KEY="test-google-key",
        GEMINI_API_KEY="test-gemini-key",
    )

    assert settings.llm_api_key == "test-qa-key"


def test_placeholder_key_raises_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Placeholder values should fail fast before any provider call."""

    monkeypatch.delenv("QA_LLM_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="placeholder"):
        Settings(
            _env_file=None,
            GOOGLE_API_KEY="your-google-api-key-here",
            QA_LLM_API_KEY=None,
            GEMINI_API_KEY=None,
        )


def test_missing_keys_raise_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """At least one API key must be provided."""

    monkeypatch.delenv("QA_LLM_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(
        ValueError,
        match="QA_LLM_API_KEY, GOOGLE_API_KEY or GEMINI_API_KEY must be set",
    ):
        Settings(
            _env_file=None,
            QA_LLM_API_KEY=None,
            GOOGLE_API_KEY=None,
            GEMINI_API_KEY=None,
        )
