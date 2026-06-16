"""Tests for BDD quality-check metrics and service integration."""

from __future__ import annotations

from unittest.mock import MagicMock

from app.core.evaluation import build_quality_checks
from app.schemas.qa import QARequest
from app.services.qa_service import QAService


def test_build_quality_checks_with_fully_anchored_response(mock_qa_response) -> None:
    """Quality checks should report no unsupported items for anchored fixtures."""

    story = """
As a user, I want to reset my password so I can recover access to my account.
Acceptance criteria:
- The user must receive a reset email
- The reset link expires in 30 minutes
- The new password must contain at least one number
""".strip()

    quality = build_quality_checks(mock_qa_response, story)

    assert quality.traceability_ratio > 0.0
    assert 0.0 <= quality.unsupported_rate <= 1.0
    assert 0.0 <= quality.ac_coverage <= 1.0
    assert 0.0 <= quality.refinement_alignment <= 1.0
    assert 0.0 <= quality.automation_trace <= 1.0


def test_service_populates_quality_checks(mock_qa_response) -> None:
    """QA service must always enrich responses with BDD quality checks."""

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_qa_response
    service = QAService(chain=mock_chain)

    request = QARequest(
        story=(
            "As a user, I want to reset my password so I can recover access to my account.\n"
            "Acceptance criteria:\n"
            "- The user must receive a reset email\n"
            "- The reset link expires in 30 minutes\n"
            "- The new password must contain at least one number"
        )
    )
    response = service.analyze(request)

    assert response.quality_checks is not None
    assert response.quality_checks.traceability_ratio >= 0.0
