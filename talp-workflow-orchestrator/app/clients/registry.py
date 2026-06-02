from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, cast

from app.clients.bdd import BddQaAgentClient
from app.clients.base import AgentClient, SupportsAgentClient
from app.clients.compliance import ComplianceAgentClient
from app.clients.invest import InvestAgentClient
from app.schemas.common import AgentName


@dataclass(frozen=True)
class AgentClientRegistry:
    clients: Mapping[AgentName, SupportsAgentClient[Any, Any]]

    def get(self, agent_name: AgentName) -> SupportsAgentClient[Any, Any]:
        try:
            return self.clients[agent_name]
        except KeyError as exc:
            raise KeyError(f"Unknown agent client: {agent_name}") from exc

    @property
    def invest(self) -> InvestAgentClient:
        return cast(InvestAgentClient, self.get("invest"))

    @property
    def compliance(self) -> ComplianceAgentClient:
        return cast(ComplianceAgentClient, self.get("compliance"))

    @property
    def bdd(self) -> BddQaAgentClient:
        return cast(BddQaAgentClient, self.get("bdd"))


def build_registry(clients: Mapping[AgentName, SupportsAgentClient[Any, Any]]) -> AgentClientRegistry:
    return AgentClientRegistry(clients=clients)
