"""Shared test fixtures and configuration."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from app.main import app
from app.schemas.qa import QAAnalysisResponse, BDDScenario


@pytest.fixture
def test_client() -> TestClient:
    """Provide a TestClient for FastAPI integration tests."""
    return TestClient(app)


@pytest.fixture
def mock_qa_response() -> QAAnalysisResponse:
    """Provide a realistic mock QA analysis response."""
    return QAAnalysisResponse(
        summary="The password reset story defines email delivery and link expiration. "
        "Gaps exist around account lookup, token invalidation, and error messaging.",
        ac_map=[
            "AC1: The user must receive a reset email",
            "AC2: The reset link expires in 30 minutes",
            "AC3: The new password must contain at least one number",
        ],
        bdd_scenarios=[
            BDDScenario(
                id="SC1",
                title="User receives reset email for valid account",
                scenario_type="positive",
                ac_ids=["AC1"],
                given=["a registered user with email john@example.com"],
                when=["the user requests a password reset"],
                then=["a reset email is sent to john@example.com"],
                notes=["Email should arrive within 5 minutes."],
                evidence_us="The user must receive a reset email",
                origin="explicit_in_story",
            ),
            BDDScenario(
                id="SC2",
                title="Reset link expires after 30 minutes",
                scenario_type="edge",
                ac_ids=["AC2"],
                given=["a valid reset link created 31 minutes ago"],
                when=["the user clicks the reset link"],
                then=["the system rejects the request with 'Link expired'"],
                notes=["Verify expiration timestamp in token."],
                evidence_us="The reset link expires in 30 minutes",
                origin="explicit_in_story",
            ),
            BDDScenario(
                id="SC3",
                title="Unregistered email is submitted",
                scenario_type="negative",
                ac_ids=["AC1"],
                given=["an email not registered in the system"],
                when=["the user requests a password reset"],
                then=["the system responds without revealing account status"],
                notes=["Prevent user enumeration."],
                evidence_us="The user must receive a reset email",
                origin="direct_inference",
            ),
        ],
        negative_cases=[
            "Submit reset request with SQL injection payload.",
            "Request multiple resets in rapid succession.",
            "Use an expired reset link.",
        ],
        edge_cases=[
            "Request reset immediately after account creation.",
            "Reset password while logged in.",
            "Request reset for email with special characters.",
        ],
        ambiguities=[
            "Should the system accept passwords that match the current password?",
            "Is a reset email required or optional?",
            "What is the exact token format and encoding?",
        ],
        risks=[
            "Token reuse could allow unauthorized password changes.",
            "Weak email validation could allow reset of admin accounts.",
        ],
        automation_suggestions=[
            "API test: verify reset email is sent within 5 minutes.",
            "API test: verify reset link expires after 30 minutes.",
            "E2E test: complete password reset flow via UI.",
        ],
        questions_for_refinement=[
            "Should users receive a confirmation email after password change?",
            "Can a user reset a password for another account?",
        ],
        negative_cases_trace=[
            {
                "text": "Use an expired reset link.",
                "evidence_us": "The reset link expires in 30 minutes",
                "origin": "explicit_in_story",
                "ac_ids": ["AC2"],
                "scenario_id": "SC2",
            }
        ],
        edge_cases_trace=[
            {
                "text": "Request reset immediately after account creation.",
                "evidence_us": "As a user, I want to reset my password",
                "origin": "direct_inference",
                "ac_ids": ["AC1"],
                "scenario_id": "SC1",
            }
        ],
        ambiguities_trace=[
            {
                "text": "Should the system accept passwords that match the current password?",
                "evidence_us": "The new password must contain at least one number",
                "origin": "direct_inference",
                "ambiguity_id": "AMB1",
            }
        ],
        risks_trace=[
            {
                "text": "Token reuse could allow unauthorized password changes.",
                "evidence_us": "reset my password",
                "origin": "direct_inference",
                "ac_ids": ["AC1", "AC2"],
            }
        ],
        automation_suggestions_trace=[
            {
                "text": "API test: verify reset link expires after 30 minutes.",
                "evidence_us": "The reset link expires in 30 minutes",
                "origin": "explicit_in_story",
                "ac_ids": ["AC2"],
                "scenario_id": "SC2",
            }
        ],
        questions_for_refinement_trace=[
            {
                "text": "Should users receive a confirmation email after password change?",
                "evidence_us": "As a user, I want to reset my password",
                "origin": "direct_inference",
                "ambiguity_id": "AMB1",
            }
        ],
        blocked_hypotheses=[],
    )


@pytest.fixture
def mock_llm_response(mock_qa_response: QAAnalysisResponse) -> AIMessage:
    """Provide a mock LLM response as an AIMessage."""
    import json

    return AIMessage(content=json.dumps(mock_qa_response.model_dump()))
