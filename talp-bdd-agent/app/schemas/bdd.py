"""Domain models for BDD scenarios."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, computed_field

ScenarioType = Literal["positive", "negative", "edge"]
EvidenceOrigin = Literal["explicit_in_story", "direct_inference", "unconfirmed_hypothesis"]


class BDDScenario(BaseModel):
    """Strongly typed BDD scenario model with structured steps."""

    id: str | None = Field(default=None, description="Optional scenario identifier (for traceability).")
    title: str = Field(description="Short scenario title.")
    scenario_type: ScenarioType = Field(description="Scenario classification for test planning.")
    given: list[str] = Field(default_factory=list, description="Preconditions for the scenario.")
    when: list[str] = Field(default_factory=list, description="Actions performed by the actor.")
    then: list[str] = Field(default_factory=list, description="Expected outcomes and assertions.")
    notes: list[str] = Field(default_factory=list, description="Useful implementation or validation notes.")
    ac_ids: list[str] = Field(
        default_factory=list,
        description="Acceptance-criteria IDs linked to this scenario (for example: AC1, AC2).",
    )
    evidence_us: str | None = Field(
        default=None,
        description="Literal snippet from the user story used as evidence for this scenario.",
    )
    origin: EvidenceOrigin | None = Field(
        default=None,
        description="How this scenario was derived from the user story.",
    )

    @computed_field(return_type=str)
    @property
    def gherkin(self) -> str:
        """Render the scenario as valid Gherkin text."""

        lines = [f"Scenario: {self.title}"]
        lines.extend(f"  Given {item}" for item in self.given)
        lines.extend(f"  When {item}" for item in self.when)
        lines.extend(f"  Then {item}" for item in self.then)
        return "\n".join(lines)
