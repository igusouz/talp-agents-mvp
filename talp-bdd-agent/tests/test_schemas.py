"""Test Pydantic schemas for request and response validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.qa import QARequest, BDDScenario, QAAnalysisResponse


class TestQARequest:
    """Test input request validation."""

    def test_valid_request_with_story_only(self) -> None:
        """Story alone is sufficient for a valid request."""
        request = QARequest(story="As a user, I want to login")
        assert request.story == "As a user, I want to login"


    def test_missing_story_raises_validation_error(self) -> None:
        """Story is required and cannot be empty."""
        with pytest.raises(ValidationError):
            QARequest(story="")

    def test_story_field_is_required(self) -> None:
        """Story field is mandatory."""
        with pytest.raises(ValidationError):
            QARequest()


class TestBDDScenario:
    """Test BDD scenario structure."""

    def test_valid_scenario(self) -> None:
        """A complete scenario with title and structured steps is valid."""
        scenario = BDDScenario(
            title="User logs in successfully",
            scenario_type="positive",
            given=["the user is on the login page"],
            when=["the user submits valid credentials"],
            then=["the dashboard is displayed"],
        )
        assert scenario.title == "User logs in successfully"
        assert scenario.scenario_type == "positive"
        assert scenario.notes == []
        assert "Given the user is on the login page" in scenario.gherkin

    def test_scenario_with_notes(self) -> None:
        """Scenario can include implementation notes."""
        scenario = BDDScenario(
            title="User logs in",
            scenario_type="positive",
            given=["the user is on the login page"],
            when=["the user logs in"],
            then=["the session is created"],
            notes=["Use test@example.com", "Password: TestPass123"],
        )
        assert len(scenario.notes) == 2

    def test_invalid_scenario_type_raises_error(self) -> None:
        """Scenario type must be one of: positive, negative, edge."""
        with pytest.raises(ValidationError):
            BDDScenario(
                title="Test",
                scenario_type="invalid",  # type: ignore
                given=["a precondition"],
                when=["an action occurs"],
                then=["an outcome happens"],
            )


class TestQAAnalysisResponse:
    """Test output response validation."""

    def test_minimal_valid_response(self) -> None:
        """Response with only summary is valid."""
        response = QAAnalysisResponse(summary="Analysis complete.")
        assert response.summary == "Analysis complete."
        assert response.bdd_scenarios == []
        assert response.negative_cases == []

    def test_complete_response(self) -> None:
        """Full response with all fields populated."""
        response = QAAnalysisResponse(
            summary="Full analysis",
            bdd_scenarios=[
                BDDScenario(
                    title="Test",
                    scenario_type="positive",
                    given=["a precondition"],
                    when=["an action occurs"],
                    then=["an outcome happens"],
                )
            ],
            negative_cases=["Invalid input"],
            edge_cases=["Boundary value"],
            ambiguities=["Unclear requirement"],
            risks=["Security risk"],
            automation_suggestions=["Automate login"],
            questions_for_refinement=["Who are the users?"],
        )
        assert len(response.bdd_scenarios) == 1
        assert len(response.negative_cases) == 1
        assert len(response.ambiguities) == 1

    def test_summary_is_required(self) -> None:
        """Summary field is mandatory in response."""
        with pytest.raises(ValidationError):
            QAAnalysisResponse()  # type: ignore

    def test_empty_list_fields_default_to_empty(self) -> None:
        """Optional list fields initialize as empty lists."""
        response = QAAnalysisResponse(summary="Test")
        assert isinstance(response.bdd_scenarios, list)
        assert isinstance(response.negative_cases, list)
        assert isinstance(response.risks, list)
