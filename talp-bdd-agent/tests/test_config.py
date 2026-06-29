"""Tests for environment-based settings resolution."""

from __future__ import annotations

import pytest

from app.core.config import Settings


LLM_ENV_VARS = [
    "QA_LLM_PROVIDER",
    "QA_LLM_MODEL",
    "QA_LLM_BASE_URL",
    "QA_LLM_API_KEY",
    "QA_LLM_TEMPERATURE",
    "QA_LLM_TIMEOUT_SECONDS",
    "LLM_PROVIDER",
    "LLM_MODEL",
    "LLM_BASE_URL",
    "LLM_API_KEY",
    "LLM_TEMPERATURE",
    "LLM_TIMEOUT_SECONDS",
    "TALP_LLM_PROVIDER",
    "TALP_LLM_MODEL",
    "TALP_LLM_BASE_URL",
    "TALP_LLM_API_KEY",
    "TALP_LLM_TEMPERATURE",
    "TALP_LLM_TIMEOUT_SECONDS",
    "OPENROUTER_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
]


def _clear_llm_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in LLM_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def test_google_api_key_fallback_is_used(monkeypatch: pytest.MonkeyPatch) -> None:
    """GOOGLE_API_KEY should populate llm_api_key when shared keys are missing."""

    _clear_llm_env(monkeypatch)

    settings = Settings(
        _env_file=None,
        GOOGLE_API_KEY="test-google-key",
        QA_LLM_API_KEY=None,
    )

    assert settings.llm_api_key == "test-google-key"


def test_gemini_api_key_fallback_is_used(monkeypatch: pytest.MonkeyPatch) -> None:
    """GEMINI_API_KEY should be accepted as a legacy Gemini alias."""

    _clear_llm_env(monkeypatch)

    settings = Settings(
        _env_file=None,
        GEMINI_API_KEY="test-gemini-key",
        GOOGLE_API_KEY=None,
        QA_LLM_API_KEY=None,
    )

    assert settings.llm_api_key == "test-gemini-key"


def test_shared_llm_api_key_is_used_for_bdd(monkeypatch: pytest.MonkeyPatch) -> None:
    """LLM_API_KEY is the shared credential for LLM-backed agents."""

    _clear_llm_env(monkeypatch)

    settings = Settings(
        _env_file=None,
        LLM_API_KEY="test-shared-key",
        GOOGLE_API_KEY="test-google-key",
    )

    assert settings.llm_api_key == "test-shared-key"


def test_qa_llm_api_key_takes_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    """QA_LLM_API_KEY should remain available as a BDD-specific override."""

    _clear_llm_env(monkeypatch)

    settings = Settings(
        _env_file=None,
        QA_LLM_API_KEY="test-qa-key",
        LLM_API_KEY="test-shared-key",
        GOOGLE_API_KEY="test-google-key",
    )

    assert settings.llm_api_key == "test-qa-key"


def test_placeholder_key_raises_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Placeholder values should fail fast before any provider call."""

    _clear_llm_env(monkeypatch)

    with pytest.raises(ValueError, match="placeholder"):
        Settings(
            _env_file=None,
            GOOGLE_API_KEY="your-google-api-key-here",
            QA_LLM_API_KEY=None,
            GEMINI_API_KEY=None,
        )


def test_missing_keys_raise_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """At least one API key must be provided."""

    _clear_llm_env(monkeypatch)

    with pytest.raises(
        ValueError,
        match="QA_LLM_API_KEY, LLM_API_KEY, TALP_LLM_API_KEY, GOOGLE_API_KEY or GEMINI_API_KEY must be set",
    ):
        Settings(
            _env_file=None,
            QA_LLM_API_KEY=None,
            GOOGLE_API_KEY=None,
            GEMINI_API_KEY=None,
        )


def test_shared_openrouter_provider_configures_bdd(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_llm_env(monkeypatch)

    settings = Settings(
        _env_file=None,
        LLM_PROVIDER="openrouter",
        OPENROUTER_API_KEY="test-openrouter-key",
    )

    assert settings.llm_provider == "openrouter"
    assert settings.llm_model == "google/gemini-2.5-flash"
    assert settings.llm_base_url == "https://openrouter.ai/api/v1"
    assert settings.llm_api_key == "test-openrouter-key"


def test_shared_llm_api_key_is_accepted_for_bdd_openrouter(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_llm_env(monkeypatch)

    settings = Settings(
        _env_file=None,
        LLM_PROVIDER="openrouter",
        LLM_API_KEY="test-shared-key",
    )

    assert settings.llm_api_key == "test-shared-key"


def test_legacy_talp_settings_remain_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_llm_env(monkeypatch)

    settings = Settings(
        _env_file=None,
        TALP_LLM_PROVIDER="openrouter",
        TALP_LLM_API_KEY="test-legacy-key",
    )

    assert settings.llm_provider == "openrouter"
    assert settings.llm_api_key == "test-legacy-key"
