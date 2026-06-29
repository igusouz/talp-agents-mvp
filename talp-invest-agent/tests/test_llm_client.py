import pytest

from app.services.llm_client import _gemini_api_key, _openrouter_api_key


API_KEY_ENV_VARS = [
    "INVEST_LLM_API_KEY",
    "LLM_API_KEY",
    "TALP_LLM_API_KEY",
    "OPENROUTER_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
]


def _clear_api_key_env(monkeypatch):
    for name in API_KEY_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def test_google_api_key_is_used(monkeypatch):
    _clear_api_key_env(monkeypatch)

    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")

    assert _gemini_api_key() == "test-google-key"


def test_shared_llm_api_key_is_used_for_gemini(monkeypatch):
    _clear_api_key_env(monkeypatch)

    monkeypatch.setenv("LLM_API_KEY", "test-shared-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")

    assert _gemini_api_key() == "test-shared-key"


def test_gemini_api_key_is_legacy_fallback(monkeypatch):
    _clear_api_key_env(monkeypatch)

    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")

    assert _gemini_api_key() == "test-gemini-key"


def test_placeholder_key_raises_validation_error(monkeypatch):
    _clear_api_key_env(monkeypatch)

    monkeypatch.setenv("GOOGLE_API_KEY", "your-google-api-key-here")

    with pytest.raises(ValueError, match="placeholder"):
        _gemini_api_key()


def test_missing_key_raises_validation_error(monkeypatch):
    _clear_api_key_env(monkeypatch)

    with pytest.raises(ValueError, match="INVEST_LLM_API_KEY, LLM_API_KEY"):
        _gemini_api_key()


def test_openrouter_api_key_is_used(monkeypatch):
    _clear_api_key_env(monkeypatch)

    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

    assert _openrouter_api_key() == "test-openrouter-key"


def test_shared_api_key_can_be_used_for_openrouter(monkeypatch):
    _clear_api_key_env(monkeypatch)

    monkeypatch.setenv("LLM_API_KEY", "test-shared-key")

    assert _openrouter_api_key() == "test-shared-key"


def test_invest_api_key_overrides_shared_for_openrouter(monkeypatch):
    _clear_api_key_env(monkeypatch)

    monkeypatch.setenv("INVEST_LLM_API_KEY", "test-invest-key")
    monkeypatch.setenv("LLM_API_KEY", "test-shared-key")

    assert _openrouter_api_key() == "test-invest-key"
