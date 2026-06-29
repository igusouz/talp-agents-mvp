from app.config.settings import load_settings


LLM_ENV_VARS = [
    "INVEST_LLM_PROVIDER",
    "INVEST_LLM_MODEL",
    "INVEST_LLM_BASE_URL",
    "INVEST_LLM_API_KEY",
    "INVEST_LLM_TEMPERATURE",
    "INVEST_LLM_MAX_TOKENS",
    "INVEST_LLM_TIMEOUT_SECONDS",
    "INVEST_LLM_RETRIES",
    "INVEST_LLM_THINKING_BUDGET",
    "LLM_PROVIDER",
    "LLM_MODEL",
    "LLM_BASE_URL",
    "LLM_API_KEY",
    "LLM_TEMPERATURE",
    "LLM_MAX_TOKENS",
    "LLM_TIMEOUT_SECONDS",
    "LLM_RETRIES",
    "LLM_THINKING_BUDGET",
    "TALP_LLM_PROVIDER",
    "TALP_LLM_MODEL",
    "TALP_LLM_BASE_URL",
    "TALP_LLM_API_KEY",
    "TALP_LLM_TEMPERATURE",
    "TALP_LLM_MAX_TOKENS",
    "TALP_LLM_TIMEOUT_SECONDS",
    "TALP_LLM_RETRIES",
    "TALP_LLM_THINKING_BUDGET",
]


def _clear_llm_env(monkeypatch):
    for name in LLM_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def test_default_llm_model_is_gemini_flash(monkeypatch):
    _clear_llm_env(monkeypatch)

    settings = load_settings()

    assert settings.llm_provider == "gemini"
    assert settings.llm_model == "gemini-2.5-flash"
    assert settings.llm_base_url is None
    assert settings.llm_temperature == 0.0
    assert settings.llm_max_tokens == 1024
    assert settings.llm_timeout_seconds == 45.0
    assert settings.llm_retries == 1
    assert settings.llm_thinking_budget == 0


def test_shared_llm_settings_configure_invest(monkeypatch):
    _clear_llm_env(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")
    monkeypatch.setenv("LLM_API_KEY", "test-shared-key")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.1")
    monkeypatch.setenv("LLM_MAX_TOKENS", "512")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "12.5")
    monkeypatch.setenv("LLM_RETRIES", "0")
    monkeypatch.setenv("LLM_THINKING_BUDGET", "128")

    settings = load_settings()

    assert settings.llm_provider == "openrouter"
    assert settings.llm_model == "google/gemini-2.5-flash"
    assert settings.llm_base_url == "https://openrouter.ai/api/v1"
    assert settings.llm_api_key == "test-shared-key"
    assert settings.llm_temperature == 0.1
    assert settings.llm_max_tokens == 512
    assert settings.llm_timeout_seconds == 12.5
    assert settings.llm_retries == 0
    assert settings.llm_thinking_budget == 128


def test_invest_specific_settings_override_shared(monkeypatch):
    _clear_llm_env(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("LLM_MODEL", "gemini-2.5-flash")
    monkeypatch.setenv("INVEST_LLM_PROVIDER", "openrouter")
    monkeypatch.setenv("INVEST_LLM_MODEL", "openrouter/custom")

    settings = load_settings()

    assert settings.llm_provider == "openrouter"
    assert settings.llm_model == "openrouter/custom"


def test_legacy_talp_llm_settings_remain_supported(monkeypatch):
    _clear_llm_env(monkeypatch)
    monkeypatch.setenv("TALP_LLM_MAX_TOKENS", "256")
    monkeypatch.setenv("TALP_LLM_TIMEOUT_SECONDS", "15")

    settings = load_settings()

    assert settings.llm_max_tokens == 256
    assert settings.llm_timeout_seconds == 15.0
