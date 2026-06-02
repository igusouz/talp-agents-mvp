from app.config.settings import load_settings


def test_default_llm_model_is_gemini_flash(monkeypatch):
    monkeypatch.delenv("TALP_LLM_MODEL", raising=False)

    settings = load_settings()

    assert settings.llm_model == "gemini-2.5-flash"

