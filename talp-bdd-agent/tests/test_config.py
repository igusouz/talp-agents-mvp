"""Tests for environment-based settings resolution."""

from __future__ import annotations

import pytest

from app.core.config import Settings


def test_google_api_key_fallback_is_used(monkeypatch: pytest.MonkeyPatch) -> None:
    """GOOGLE_API_KEY should populate llm_api_key when QA_LLM_API_KEY is missing."""

    monkeypatch.delenv("QA_LLM_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    settings = Settings(
        _env_file=None,
        GOOGLE_API_KEY="test-google-key",
        QA_LLM_API_KEY=None,
    )

    assert settings.llm_api_key == "test-google-key"


def test_missing_keys_raise_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """At least one API key must be provided."""

    monkeypatch.delenv("QA_LLM_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    with pytest.raises(ValueError, match="QA_LLM_API_KEY or GOOGLE_API_KEY must be set"):
        Settings(
            _env_file=None,
            QA_LLM_API_KEY=None,
            GOOGLE_API_KEY=None,
        )
