from __future__ import annotations

import httpx

from app.clients.base import AgentClient
from app.core.config import Settings
from app.schemas.common import RequestContext
from app.schemas.compliance import ComplianceAnalysisRequest, ComplianceAnalysisResponse


class ComplianceAgentClient(AgentClient[ComplianceAnalysisRequest, ComplianceAnalysisResponse]):
    agent_name = "compliance"
    path = "/analyze"
    response_model = ComplianceAnalysisResponse

    async def send(
        self,
        request: ComplianceAnalysisRequest,
        *,
        context: RequestContext | None = None,
    ) -> ComplianceAnalysisResponse:
        return await self._post(request, context=context)


def build_compliance_client(
    *,
    http_client: httpx.AsyncClient,
    settings: Settings,
    logger=None,
) -> ComplianceAgentClient:
    return ComplianceAgentClient(
        base_url=str(settings.compliance_agent_base_url),
        http_client=http_client,
        settings=settings,
        logger=logger,
    )
