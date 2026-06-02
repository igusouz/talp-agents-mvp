from __future__ import annotations

import httpx

from app.clients.bdd import build_bdd_client
from app.clients.compliance import build_compliance_client
from app.clients.invest import build_invest_client
from app.clients.registry import AgentClientRegistry, build_registry
from app.core.config import Settings, build_timeout


def create_http_client(settings: Settings) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=build_timeout(settings),
        headers={"User-Agent": settings.user_agent},
    )


def create_agent_registry(
    *,
    http_client: httpx.AsyncClient,
    settings: Settings,
    logger=None,
) -> AgentClientRegistry:
    return build_registry(
        {
            "invest": build_invest_client(http_client=http_client, settings=settings, logger=logger),
            "compliance": build_compliance_client(
                http_client=http_client,
                settings=settings,
                logger=logger,
            ),
            "bdd": build_bdd_client(http_client=http_client, settings=settings, logger=logger),
        }
    )
