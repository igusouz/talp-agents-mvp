from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import Field, field_validator

from app.schemas.common import StrictModel
from app.schemas.compliance import ComplianceAnalysisResponse
from app.schemas.invest import InvestAnalysis
from app.schemas.qa import QAAnalysisResponse


WorkflowStage = Literal[
    "received",
    "invest_done",
    "compliance_done",
    "waiting_for_review",
    "approved",
    "bdd_done",
    "completed",
    "failed",
]


class UserStoryInput(StrictModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    acceptance_criteria: list[str] = Field(default_factory=list)
    additional_context: str | None = None

    @field_validator("title", "description")
    @classmethod
    def text_fields_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("field must not be blank")
        return cleaned

    @field_validator("acceptance_criteria")
    @classmethod
    def criteria_must_not_contain_blank_items(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if item.strip()]
        if not cleaned:
            raise ValueError("acceptance_criteria must have at least one item")
        return cleaned


class WorkflowCreateRequest(StrictModel):
    user_story: UserStoryInput
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowCreateResponse(StrictModel):
    workflow_id: str
    stage: WorkflowStage
    original_story: UserStoryInput
    invest_analysis: InvestAnalysis
    compliance_analysis: ComplianceAnalysisResponse
    next_action: Literal["review"] = "review"
    correlation_id: str | None = None


class WorkflowStateResponse(StrictModel):
    workflow_id: str
    stage: WorkflowStage
    original_story: UserStoryInput
    approved_story: UserStoryInput | None = None
    invest_analysis: InvestAnalysis | None = None
    compliance_analysis: ComplianceAnalysisResponse | None = None
    bdd_analysis: QAAnalysisResponse | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str | None = None


class ApprovedStoryRequest(StrictModel):
    approved_story: UserStoryInput
    reviewer_id: str | None = None
    review_notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class FinalWorkflowResponse(StrictModel):
    workflow_id: str
    stage: Literal["bdd_done", "completed"] = "bdd_done"
    approved_story: UserStoryInput
    bdd_analysis: QAAnalysisResponse
    correlation_id: str | None = None
