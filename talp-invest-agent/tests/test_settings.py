from app.config.settings import load_settings


def test_default_llm_model_is_gemini_flash(monkeypatch):
    monkeypatch.delenv("TALP_LLM_MODEL", raising=False)
    monkeypatch.delenv("TALP_LLM_MAX_TOKENS", raising=False)
    monkeypatch.delenv("TALP_LLM_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("TALP_LLM_RETRIES", raising=False)
    monkeypatch.delenv("TALP_LLM_THINKING_BUDGET", raising=False)

    settings = load_settings()

    assert settings.llm_model == "gemini-2.5-flash"
    assert settings.llm_max_tokens == 1024
    assert settings.llm_timeout_seconds == 45.0
    assert settings.llm_retries == 1
    assert settings.llm_thinking_budget == 0


def test_llm_execution_limits_can_be_configured(monkeypatch):
    monkeypatch.setenv("TALP_LLM_MAX_TOKENS", "512")
    monkeypatch.setenv("TALP_LLM_TIMEOUT_SECONDS", "12.5")
    monkeypatch.setenv("TALP_LLM_RETRIES", "0")
    monkeypatch.setenv("TALP_LLM_THINKING_BUDGET", "128")

    settings = load_settings()

    assert settings.llm_max_tokens == 512
    assert settings.llm_timeout_seconds == 12.5
    assert settings.llm_retries == 0
    assert settings.llm_thinking_budget == 128
