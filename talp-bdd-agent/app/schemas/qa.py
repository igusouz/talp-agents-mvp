"""Pydantic schemas for the BDD QA workflow."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.bdd import BDDScenario


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
