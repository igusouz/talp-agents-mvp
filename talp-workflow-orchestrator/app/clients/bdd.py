from __future__ import annotations

import httpx

from app.clients.base import AgentClient
from app.core.config import Settings
from app.schemas.common import RequestContext
from app.schemas.qa import QAAnalysisResponse, QARequest


class BddQaAgentClient(AgentClient[QARequest, QAAnalysisResponse]):
    agent_name = "bdd"
    path = "/analyze"
    response_model = QAAnalysisResponse

    async def send(
        self,
        request: QARequest,
        *,
        context: RequestContext | None = None,
    ) -> QAAnalysisResponse:
        return await self._post(request, context=context)


def build_bdd_client(
    *,
    http_client: httpx.AsyncClient,
    settings: Settings,
    logger=None,
) -> BddQaAgentClient:
    return BddQaAgentClient(
        base_url=str(settings.bdd_agent_base_url),
        http_client=http_client,
        settings=settings,
        logger=logger,
    )
