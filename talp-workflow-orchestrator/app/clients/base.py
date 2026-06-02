from __future__ import annotations

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from time import perf_counter
from typing import Any, ClassVar, Generic, Protocol, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from app.core.config import Settings, build_timeout
from app.core.exceptions import (
    AgentRequestValidationError,
    AgentResponseValidationError,
    AgentRetryExhaustedError,
    AgentTimeoutError,
    AgentTransportError,
    AgentUpstreamHttpError,
)
from app.schemas.common import RequestContext


RequestT = TypeVar("RequestT", bound=BaseModel)
ResponseT = TypeVar("ResponseT", bound=BaseModel)


class SupportsAgentClient(Protocol[RequestT, ResponseT]):
    agent_name: str

    async def send(self, request: RequestT, *, context: RequestContext | None = None) -> ResponseT:
        ...


class AgentClient(ABC, Generic[RequestT, ResponseT]):
    agent_name: ClassVar[str]
    path: ClassVar[str]
    response_model: ClassVar[type[ResponseT]]

    def __init__(
        self,
        *,
        base_url: str,
        http_client: httpx.AsyncClient,
        settings: Settings,
        logger: logging.Logger | logging.LoggerAdapter | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._http_client = http_client
        self._settings = settings
        self._timeout = build_timeout(settings)
        self._logger = logger or logging.getLogger(f"app.clients.{self.agent_name}")

    @abstractmethod
    async def send(self, request: RequestT, *, context: RequestContext | None = None) -> ResponseT:
        raise NotImplementedError

    def _url(self) -> str:
        return f"{self._base_url}/{self.path.lstrip('/')}"

    def _headers(self, context: RequestContext | None) -> dict[str, str]:
        headers = {
            "User-Agent": self._settings.user_agent,
            "X-Agent-Name": self.agent_name,
        }
        if context is not None:
            headers["X-Request-ID"] = context.request_id
            if context.correlation_id:
                headers["X-Correlation-ID"] = context.correlation_id
        return headers

    def _retry_delay(self, attempt: int) -> float:
        backoff = min(
            self._settings.retry_max_backoff_seconds,
            self._settings.retry_backoff_seconds * (2 ** max(attempt - 1, 0)),
        )
        jitter = random.uniform(0.0, self._settings.retry_jitter_seconds)
        return backoff + jitter

    def _should_retry_status(self, status_code: int) -> bool:
        return status_code == 429 or status_code >= 500

    async def _post(
        self,
        request: RequestT,
        *,
        context: RequestContext | None = None,
    ) -> ResponseT:
        url = self._url()

        try:
            payload = request.model_dump(mode="json", exclude_none=True)
        except ValidationError as exc:
            raise AgentRequestValidationError(
                "Request model validation failed",
                agent_name=self.agent_name,
                url=url,
            ) from exc

        last_error: Exception | None = None
        max_attempts = self._settings.retry_attempts + 1

        for attempt in range(1, max_attempts + 1):
            start = perf_counter()
            try:
                response = await self._http_client.post(
                    url,
                    json=payload,
                    headers=self._headers(context),
                    timeout=self._timeout,
                )
                duration_ms = (perf_counter() - start) * 1000
                response.raise_for_status()
                try:
                    response_payload = response.json()
                except ValueError as exc:
                    raise AgentResponseValidationError(
                        "Agent response body is not valid JSON",
                        agent_name=self.agent_name,
                        url=url,
                    ) from exc

                try:
                    parsed = self.response_model.model_validate(response_payload)
                except ValidationError as exc:
                    raise AgentResponseValidationError(
                        "Agent response did not match the expected schema",
                        agent_name=self.agent_name,
                        url=url,
                    ) from exc

                self._logger.info(
                    "agent_call_succeeded",
                    extra={
                        "agent_name": self.agent_name,
                        "url": url,
                        "attempt": attempt,
                        "status_code": response.status_code,
                        "duration_ms": round(duration_ms, 2),
                    },
                )
                return parsed

            except httpx.TimeoutException as exc:
                last_error = AgentTimeoutError(
                    "Agent request timed out",
                    agent_name=self.agent_name,
                    url=url,
                )
                should_retry = attempt < max_attempts
                self._logger.warning(
                    "agent_call_timeout",
                    extra={
                        "agent_name": self.agent_name,
                        "url": url,
                        "attempt": attempt,
                        "max_attempts": max_attempts,
                    },
                    exc_info=exc,
                )
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if self._should_retry_status(status_code) and attempt < max_attempts:
                    last_error = AgentUpstreamHttpError(
                        "Agent returned a retryable status code",
                        agent_name=self.agent_name,
                        url=url,
                        status_code=status_code,
                    )
                    should_retry = True
                else:
                    raise AgentUpstreamHttpError(
                        "Agent returned an unexpected HTTP status",
                        agent_name=self.agent_name,
                        url=url,
                        status_code=status_code,
                    ) from exc
                self._logger.warning(
                    "agent_call_http_status",
                    extra={
                        "agent_name": self.agent_name,
                        "url": url,
                        "attempt": attempt,
                        "status_code": status_code,
                        "max_attempts": max_attempts,
                    },
                    exc_info=exc,
                )
            except httpx.RequestError as exc:
                last_error = AgentTransportError(
                    "Transport error while calling agent",
                    agent_name=self.agent_name,
                    url=url,
                )
                should_retry = attempt < max_attempts
                self._logger.warning(
                    "agent_call_transport_error",
                    extra={
                        "agent_name": self.agent_name,
                        "url": url,
                        "attempt": attempt,
                        "max_attempts": max_attempts,
                    },
                    exc_info=exc,
                )
            else:
                should_retry = False

            if should_retry:
                await asyncio.sleep(self._retry_delay(attempt))
                continue

            if last_error is not None:
                raise AgentRetryExhaustedError(
                    "Retry attempts exhausted while calling agent",
                    agent_name=self.agent_name,
                    url=url,
                    attempts=attempt,
                ) from last_error

        raise AgentRetryExhaustedError(
            "Retry attempts exhausted while calling agent",
            agent_name=self.agent_name,
            url=url,
            attempts=max_attempts,
        )
