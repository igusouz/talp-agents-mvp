"""Pydantic schemas for the BDD QA workflow."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.bdd import BDDScenario, EvidenceOrigin


class TraceableItem(BaseModel):
    """Traceability metadata for free-text QA items."""

    text: str = Field(min_length=1, description="Original item text.")
    evidence_us: str | None = Field(
        default=None,
        description="Literal snippet from user story proving this item.",
    )
    origin: EvidenceOrigin | None = Field(
        default=None,
        description="How this item was derived from the user story.",
    )
    ac_ids: list[str] = Field(
        default_factory=list,
        description="Acceptance-criteria IDs linked to this item (for example: AC1).",
    )
    scenario_id: str | None = Field(default=None, description="Linked scenario ID, when applicable.")
    ambiguity_id: str | None = Field(default=None, description="Linked ambiguity ID, when applicable.")


class QualityChecks(BaseModel):
    """BDD quality metrics focused on traceability and anti-hallucination."""

    traceability_ratio: float = Field(ge=0.0, le=1.0)
    unsupported_rate: float = Field(ge=0.0, le=1.0)
    ac_coverage: float = Field(ge=0.0, le=1.0)
    refinement_alignment: float = Field(ge=0.0, le=1.0)
    automation_trace: float = Field(ge=0.0, le=1.0)
    observations: list[str] = Field(default_factory=list)


from pydantic import BaseModel, Field


class QARequest(BaseModel):
    """Incoming payload for story analysis."""
    story: str = Field(min_length=1, description="User story to analyze.")


class QAAnalysisResponse(BaseModel):
    """Structured response returned by the QA analysis chain."""

    summary: str = Field(description="Concise analysis summary.")
    bdd_scenarios: list[BDDScenario] = Field(default_factory=list)
    negative_cases: list[str] = Field(default_factory=list)
    edge_cases: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    automation_suggestions: list[str] = Field(default_factory=list)
    questions_for_refinement: list[str] = Field(default_factory=list)
    ac_map: list[str] = Field(
        default_factory=list,
        description="Optional acceptance-criteria map in format 'ACx: <criterion>'.",
    )
    negative_cases_trace: list[TraceableItem] = Field(default_factory=list)
    edge_cases_trace: list[TraceableItem] = Field(default_factory=list)
    ambiguities_trace: list[TraceableItem] = Field(default_factory=list)
    risks_trace: list[TraceableItem] = Field(default_factory=list)
    automation_suggestions_trace: list[TraceableItem] = Field(default_factory=list)
    questions_for_refinement_trace: list[TraceableItem] = Field(default_factory=list)
    blocked_hypotheses: list[str] = Field(
        default_factory=list,
        description="Optional non-scoreable hypotheses with insufficient evidence.",
    )
    quality_checks: QualityChecks | None = Field(
        default=None,
        description="Computed BDD quality metrics for traceability and discrimination.",
    )
