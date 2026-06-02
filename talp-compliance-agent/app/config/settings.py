"""
Configurações da aplicação
"""

from pydantic_settings import BaseSettings


from pydantic import Extra

class Settings(BaseSettings):
    """Configurações da aplicação."""

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

    # Logging
    log_level: str = "INFO"
    log_file: str = "./storage/logs/app.log"


    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = Extra.allow


settings = Settings()
