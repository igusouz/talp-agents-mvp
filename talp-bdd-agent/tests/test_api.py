"""Test FastAPI routes and HTTP contract."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.core.exceptions import UpstreamRateLimitError
from app.main import app
from app.schemas.qa import QAAnalysisResponse


class TestHealthCheck:
    """Test the health endpoint."""

    def test_health_check_returns_ok(self) -> None:
        """Health check returns 200 with service info."""
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
        assert "version" in data


class TestQAAnalysisEndpoint:
    """Test the QA analysis endpoint."""

    @patch("app.services.qa_service.get_qa_chain")
    def test_analyze_endpoint_success(
        self, mock_chain_factory: MagicMock, mock_qa_response: QAAnalysisResponse
    ) -> None:
        """POST /api/v1/qa/analyze returns structured QA response."""
        # Setup mock chain
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_qa_response
        mock_chain_factory.return_value = mock_chain

        client = TestClient(app)
        payload = {
            "story": "As a user, I want to reset my password",
        }

        response = client.post("/api/v1/qa/analyze", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "bdd_scenarios" in data
        assert "negative_cases" in data
        assert "risks" in data

    def test_analyze_endpoint_missing_story(self) -> None:
        """POST without story returns validation error."""
        client = TestClient(app)
        payload = {}

        response = client.post("/api/v1/qa/analyze", json=payload)

        assert response.status_code == 422  # Unprocessable Entity

    def test_analyze_endpoint_empty_story(self) -> None:
        """POST with empty story returns validation error."""
        client = TestClient(app)
        payload = {"story": ""}

        response = client.post("/api/v1/qa/analyze", json=payload)

        assert response.status_code == 422

    @patch("app.services.qa_service.get_qa_chain")
    def test_analyze_endpoint_rate_limited_returns_429(self, mock_chain_factory: MagicMock) -> None:
        """Provider rate limits are translated into HTTP 429 for clients."""
        mock_chain = MagicMock()
        mock_chain.invoke.side_effect = UpstreamRateLimitError(
            "LLM provider is rate-limited right now. Please retry in a few seconds."
        )
        mock_chain_factory.return_value = mock_chain

        client = TestClient(app)
        payload = {
            "story": "As a user, I want to reset my password",
        }

        response = client.post("/api/v1/qa/analyze", json=payload)

        assert response.status_code == 429
        assert "rate-limited" in response.json()["detail"]

    def test_analyze_endpoint_valid_minimal_request(self) -> None:
        """POST with only story (no criteria) is accepted."""
        client = TestClient(app)
        payload = {"story": "As a user, I want to login"}

        # Mock the chain to avoid actual LLM call
        with patch("app.services.qa_service.get_qa_chain") as mock_chain_factory:
            mock_chain = MagicMock()
            mock_response = QAAnalysisResponse(
                summary="Minimal test response",
                bdd_scenarios=[],
            )
            mock_chain.invoke.return_value = mock_response
            mock_chain_factory.return_value = mock_chain

            response = client.post("/api/v1/qa/analyze", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["summary"] == "Minimal test response"

    @patch("app.services.qa_service.get_qa_chain")
    def test_analyze_endpoint_response_structure(
        self, mock_chain_factory: MagicMock, mock_qa_response: QAAnalysisResponse
    ) -> None:
        """Response contains all expected fields with correct types."""
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_qa_response
        mock_chain_factory.return_value = mock_chain

        client = TestClient(app)
        payload = {
            "story": "As a user, I want to reset my password",
        }

        response = client.post("/api/v1/qa/analyze", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Verify all expected fields exist
        assert isinstance(data["summary"], str)
        assert isinstance(data["bdd_scenarios"], list)
        assert isinstance(data["negative_cases"], list)
        assert isinstance(data["edge_cases"], list)
        assert isinstance(data["ambiguities"], list)
        assert isinstance(data["risks"], list)
        assert isinstance(data["automation_suggestions"], list)
        assert isinstance(data["questions_for_refinement"], list)

        # Verify BDD scenario structure
        if data["bdd_scenarios"]:
            scenario = data["bdd_scenarios"][0]
            assert "title" in scenario
            assert "scenario_type" in scenario
            assert "given" in scenario
            assert "when" in scenario
            assert "then" in scenario
            assert "gherkin" in scenario
            assert scenario["scenario_type"] in ["positive", "negative", "edge"]
