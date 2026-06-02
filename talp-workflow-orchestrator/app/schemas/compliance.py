from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import ConfigDict, Field, field_validator

from app.schemas.common import StrictModel


class InvestCriterionResult(StrictModel):
    criterion_id: str
    criterion_name: str
    result: bool
    evidence: str | None = None


class InvestResult(StrictModel):
    investment_id: str
    status: str
    criteria_results: list[InvestCriterionResult]
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class InvestContext(StrictModel):
    investment_id: str
    overall_status: str
    score: float | None = None
    warnings: list[str] = Field(default_factory=list)
    failed: list[str] = Field(default_factory=list)
    detected_problems: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    invest_result: InvestResult | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CatalogRule(StrictModel):
    rule_id: str
    name: str
    domain: str
    description: str
    mandatory: bool
    blocking: bool
    keywords: list[str]
    evidence: str

    model_config = ConfigDict(from_attributes=True)


class RuleDependency(StrictModel):
    rule_id: str
    depends_on: list[str]
    description: str | None = None


class DetectedRule(StrictModel):
    rule_id: str
    name: str
    domain: str
    matched: bool
    confidence: float = Field(ge=0, le=1)
    evidence_found: list[str] = Field(default_factory=list)
    dependencies: list[RuleDependency] = Field(default_factory=list)


class ComplianceGap(StrictModel):
    rule_id: str
    rule_name: str
    severity: Literal["critical", "high", "medium", "low"]
    gap_description: str
    remediation_suggestion: str | None = None
    blocking: bool


class ComplianceRequirement(StrictModel):
    requirement_id: str
    description: str
    status: Literal["satisfied", "gap", "pending"]
    rules_involved: list[str]


class ComplianceAnalysisRequest(StrictModel):
    investment_id: str
    invest_result: InvestResult

    @field_validator("investment_id")
    @classmethod
    def investment_id_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("investment_id must not be blank")
        return cleaned


class ComplianceAnalysisResponse(StrictModel):
    analysis_id: str
    investment_id: str
    status: Literal["compliant", "non_compliant", "partial"]
    detected_rules: list[DetectedRule]
    compliance_gaps: list[ComplianceGap]
    requirements: list[ComplianceRequirement]
    summary: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)
