from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


CriterionName = Literal[
    "independent",
    "negotiable",
    "valuable",
    "estimable",
    "small",
    "testable",
]
CriterionStatus = Literal["pass", "fail"]
StoryCategory = Literal["boa", "ruim"]

CRITERIA: tuple[str, ...] = (
    "independent",
    "negotiable",
    "valuable",
    "estimable",
    "small",
    "testable",
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AgentInput(StrictModel):
    user_story_text: str = Field(min_length=1, max_length=10000)

    @field_validator("user_story_text")
    @classmethod
    def story_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("user_story_text must not be blank")
        return value.strip()


class CriterionAssessment(StrictModel):
    status: CriterionStatus
    evidence: list[str] = Field(default_factory=list)
    reason: str = Field(min_length=1)

    @field_validator("evidence")
    @classmethod
    def evidence_items_must_not_be_blank(cls, value: list[str]) -> list[str]:
        return [item for item in value if item.strip()]


class InvestAnalysis(StrictModel):
    independent: CriterionAssessment
    negotiable: CriterionAssessment
    valuable: CriterionAssessment
    estimable: CriterionAssessment
    small: CriterionAssessment
    testable: CriterionAssessment

    def failed_criteria(self) -> list[str]:
        return [
            criterion
            for criterion in CRITERIA
            if getattr(self, criterion).status == "fail"
        ]

    def as_criteria_dict(self) -> dict[str, CriterionAssessment]:
        return {criterion: getattr(self, criterion) for criterion in CRITERIA}


class Classification(StrictModel):
    category: StoryCategory
    rule_applied: str
    failed_criteria: list[CriterionName]


class ReportProblem(StrictModel):
    criterion: CriterionName
    problem: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)
    explanation: str = Field(min_length=1)


class BadStoryReport(StrictModel):
    problems: list[ReportProblem]


class PromptRecord(StrictModel):
    id: str
    version: str
    path: str
    sha256: str


class AuditInfo(StrictModel):
    prompt_versions: dict[str, str]
    prompt_hashes: dict[str, str]
    model: dict[str, Any]
    created_at_utc: datetime


class FinalResult(StrictModel):
    step_1_invest_analysis: InvestAnalysis
    step_2_classification: Classification
    step_3_report: BadStoryReport | None


class FinalOutput(StrictModel):
    execution_id: str
    schema_version: str
    input: AgentInput
    result: FinalResult
    audit: AuditInfo

