"""
Configurações da aplicação
"""

from pydantic_settings import BaseSettings


from pydantic_settings import SettingsConfigDict

class Settings(BaseSettings):
    """Configurações da aplicação."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow",
    )

    # Ambiente
    environment: str = "development"
    debug: bool = True

    # FastAPI
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_title: str = "TALP Compliance Agent API"
    api_version: str = "0.1.0"

    # Banco de dados
    database_url: str = "sqlite:///./storage/db/compliance_agent.db"

    # Recursos de análise
    catalog_rules_path: str = "data/catalog_rules_v1.csv"
    audit_log_path: str = "storage/audit/compliance_runs.jsonl"
    agent_backend: str = "heuristic"

    # Logging
    log_level: str = "INFO"
    log_file: str = "./storage/logs/app.log"


settings = Settings()
