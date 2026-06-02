from __future__ import annotations


class OrchestratorError(Exception):
    """Base error for orchestrator infrastructure failures."""


class AgentClientError(OrchestratorError):
    def __init__(self, message: str, *, agent_name: str, url: str) -> None:
        super().__init__(message)
        self.agent_name = agent_name
        self.url = url


class AgentRequestValidationError(AgentClientError):
    pass


class AgentResponseValidationError(AgentClientError):
    pass


class AgentTransportError(AgentClientError):
    pass


class AgentTimeoutError(AgentClientError):
    pass


class AgentRetryExhaustedError(AgentClientError):
    def __init__(self, message: str, *, agent_name: str, url: str, attempts: int) -> None:
        super().__init__(message, agent_name=agent_name, url=url)
        self.attempts = attempts


class AgentUpstreamHttpError(AgentClientError):
    def __init__(self, message: str, *, agent_name: str, url: str, status_code: int) -> None:
        super().__init__(message, agent_name=agent_name, url=url)
        self.status_code = status_code
