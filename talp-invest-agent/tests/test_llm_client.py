import pytest

from app.services.llm_client import _gemini_api_key


def test_google_api_key_is_used(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")

    assert _gemini_api_key() == "test-google-key"


def test_gemini_api_key_is_legacy_fallback(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")

    assert _gemini_api_key() == "test-gemini-key"


def test_placeholder_key_raises_validation_error(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    monkeypatch.setenv("GOOGLE_API_KEY", "your-google-api-key-here")

    with pytest.raises(ValueError, match="placeholder"):
        _gemini_api_key()


def test_missing_key_raises_validation_error(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GOOGLE_API_KEY or GEMINI_API_KEY"):
        _gemini_api_key()
