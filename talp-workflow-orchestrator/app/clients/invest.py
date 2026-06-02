from __future__ import annotations

import httpx

from app.clients.base import AgentClient
from app.core.config import Settings
from app.schemas.common import RequestContext
from app.schemas.invest import InvestAgentRequest, InvestAgentResponse


class InvestAgentClient(AgentClient[InvestAgentRequest, InvestAgentResponse]):
    agent_name = "invest"
    path = "/analyze"
    response_model = InvestAgentResponse

    async def send(
        self,
        request: InvestAgentRequest,
        *,
        context: RequestContext | None = None,
    ) -> InvestAgentResponse:
        return await self._post(request, context=context)


def build_invest_client(
    *,
    http_client: httpx.AsyncClient,
    settings: Settings,
    logger=None,
) -> InvestAgentClient:
    return InvestAgentClient(
        base_url=str(settings.invest_agent_base_url),
        http_client=http_client,
        settings=settings,
        logger=logger,
    )
