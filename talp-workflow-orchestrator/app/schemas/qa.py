from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, computed_field, field_validator


ScenarioType = Literal["positive", "negative", "edge"]


class BDDScenario(BaseModel):
    title: str = Field(description="Short scenario title.")
    scenario_type: ScenarioType = Field(description="Scenario classification for test planning.")
    given: list[str] = Field(default_factory=list, description="Preconditions for the scenario.")
    when: list[str] = Field(default_factory=list, description="Actions performed by the actor.")
    then: list[str] = Field(default_factory=list, description="Expected outcomes and assertions.")
    notes: list[str] = Field(default_factory=list, description="Useful implementation or validation notes.")

    @computed_field(return_type=str)
    @property
    def gherkin(self) -> str:
        lines = [f"Scenario: {self.title}"]
        lines.extend(f"  Given {item}" for item in self.given)
        lines.extend(f"  When {item}" for item in self.when)
        lines.extend(f"  Then {item}" for item in self.then)
        return "\n".join(lines)


class QARequest(BaseModel):
    story: str = Field(min_length=1, description="User story to analyze.")

    @field_validator("story")
    @classmethod
    def story_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("story must not be blank")
        return cleaned


class QAAnalysisResponse(BaseModel):
    summary: str = Field(description="Concise analysis summary.")
    bdd_scenarios: list[BDDScenario] = Field(default_factory=list)
    negative_cases: list[str] = Field(default_factory=list)
    edge_cases: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    automation_suggestions: list[str] = Field(default_factory=list)
    questions_for_refinement: list[str] = Field(default_factory=list)
