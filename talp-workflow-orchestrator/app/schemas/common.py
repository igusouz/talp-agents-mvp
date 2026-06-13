from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


AgentName = Literal["invest", "compliance", "bdd"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class RequestContext(StrictModel):
    request_id: str = Field(default_factory=lambda: uuid4().hex)
    correlation_id: str | None = None
    source: str = Field(default="workflow-orchestrator")
    created_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)
