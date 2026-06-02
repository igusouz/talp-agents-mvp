from __future__ import annotations

from functools import lru_cache

from app.clients.factory import create_agent_registry, create_http_client
from app.core.config import Settings, get_settings


@lru_cache(maxsize=1)
def get_app_settings() -> Settings:
    return get_settings()


def build_clients():
    settings = get_app_settings()
    http_client = create_http_client(settings)
    registry = create_agent_registry(http_client=http_client, settings=settings)
    return http_client, registry
