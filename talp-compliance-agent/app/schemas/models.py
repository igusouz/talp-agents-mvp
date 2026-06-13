"""
Schemas de requisição e resposta - Pydantic V2
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Schema para resposta de health check."""

    status: str
    service: str
    version: str


# ============================================================================
# Schemas do Resultado de Investimento (Entrada do pipeline)
# ============================================================================


class InvestCriterionResult(BaseModel):
    """Resultado de um critério de investimento."""

    criterion_id: str
    criterion_name: str
    result: bool
    evidence: Optional[str] = None


class InvestResult(BaseModel):
    """Resultado completo do agente de investimento."""

    investment_id: str
    status: str
    criteria_results: list[InvestCriterionResult]
    summary: str
    metadata: dict = Field(default_factory=dict)


class InvestContext(BaseModel):
    """Contexto do investimento a ser analisado - normalizando resultado do talp-invest-agent."""

    investment_id: str
    overall_status: str  # "unknown", "approved", "warning", "rejected"
    score: Optional[float] = None  # 0-100
    warnings: list[str] = Field(default_factory=list)
    failed: list[str] = Field(default_factory=list)
    detected_problems: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    invest_result: Optional[InvestResult] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================================================
# Schemas do Catálogo de Regras
# ============================================================================


class CatalogRule(BaseModel):
    """Modelo de uma regra de compliance do catálogo."""

    rule_id: str
    name: str
    domain: str
    description: str
    mandatory: bool
    blocking: bool
    keywords: list[str]
    evidence: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Schemas de Detecção e Análise de Regras
# ============================================================================


class RuleDependency(BaseModel):
    """Dependência entre regras."""

    rule_id: str
    depends_on: list[str]
    description: Optional[str] = None


class DetectedRule(BaseModel):
    """Regra detectada no investimento."""

    rule_id: str
    name: str
    domain: str
    matched: bool
    confidence: float = Field(ge=0, le=1)
    evidence_found: list[str] = Field(default_factory=list)
    dependencies: list[RuleDependency] = Field(default_factory=list)


class ComplianceGap(BaseModel):
    """Gap de conformidade identificado."""

    rule_id: str
    rule_name: str
    severity: str  # "critical", "high", "medium", "low"
    gap_description: str
    remediation_suggestion: Optional[str] = None
    blocking: bool


class ComplianceRequirement(BaseModel):
    """Requisito de compliance."""

    requirement_id: str
    description: str
    status: str  # "satisfied", "gap", "pending"
    rules_involved: list[str]


# ============================================================================
# Schemas de Requisição e Resposta
# ============================================================================


class ComplianceAnalysisRequest(BaseModel):
    """Schema para requisição de análise de conformidade."""

    investment_id: str
    invest_result: InvestResult


class ComplianceAnalysisResponse(BaseModel):
    """Schema para resposta de análise de conformidade."""

    analysis_id: str
    investment_id: str
    status: str  # "compliant", "non_compliant", "partial"
    detected_rules: list[DetectedRule]
    compliance_gaps: list[ComplianceGap]
    requirements: list[ComplianceRequirement]
    summary: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)
