"""
Testes: API Endpoints - Testes de integração dos endpoints FastAPI
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.models import (
    ComplianceAnalysisRequest,
    InvestCriterionResult,
    InvestResult,
)

client = TestClient(app)


class TestHealthEndpoints:
    """Testes dos endpoints de health check."""

    def test_get_health_returns_200(self):
        """Teste 1: GET /health retorna 200."""
        # Arrange & Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "talp-compliance-agent"
        assert data["version"] == "0.1.0"

    def test_get_api_v1_health_returns_200(self):
        """Teste: GET /api/v1/health retorna 200."""
        # Arrange & Act
        response = client.get("/api/v1/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "talp-compliance-agent"
        assert data["version"] == "0.1.0"

    def test_get_root_returns_200(self):
        """Teste: GET / retorna informações da aplicação."""
        # Arrange & Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data


class TestComplianceEndpoints:
    """Testes dos endpoints de análise de conformidade."""

    @pytest.fixture
    def invest_result_base(self):
        """Fixture: Resultado base do invest-agent."""
        return InvestResult(
            investment_id="INV-2026-API-TEST",
            status="warning",
            criteria_results=[
                InvestCriterionResult(
                    criterion_id="EST-001",
                    criterion_name="Estimable",
                    result=True,
                    evidence="Dados financeiros disponíveis",
                ),
                InvestCriterionResult(
                    criterion_id="TEST-001",
                    criterion_name="Testable",
                    result=True,
                    evidence="Histórico de performance",
                ),
            ],
            summary="Investimento em saúde",
        )

    def test_post_analyze_with_antibiotic_returns_rule_008(self, invest_result_base):
        """Teste 2: POST /api/v1/compliance/analyze com antibiótico retorna RULE_008."""
        # Arrange
        invest_result_base.summary = (
            "Paciente recebeu prescrição com antibiótico. "
            "Recomendação de usar medicamento antimicrobiano. "
            "CCIH deve validar o uso de antibióticos."
        )
        request_data = {
            "investment_id": invest_result_base.investment_id,
            "invest_result": {
                "investment_id": invest_result_base.investment_id,
                "status": invest_result_base.status,
                "criteria_results": [
                    {
                        "criterion_id": c.criterion_id,
                        "criterion_name": c.criterion_name,
                        "result": c.result,
                        "evidence": c.evidence,
                    }
                    for c in invest_result_base.criteria_results
                ],
                "summary": invest_result_base.summary,
                "metadata": invest_result_base.metadata,
            },
        }

        # Act
        response = client.post("/api/v1/compliance/analyze", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "detected_rules" in data
        rule_ids = [r["rule_id"] for r in data["detected_rules"]]
        assert "RULE_008" in rule_ids, "RULE_008 deve ser detectada em prescrição com antibiótico"

    def test_post_analyze_with_medication_returns_rule_007(self, invest_result_base):
        """Teste 3: POST /api/v1/compliance/analyze com medicamento retorna RULE_007."""
        # Arrange
        invest_result_base.summary = (
            "Paciente medicado com prescrição. "
            "Medicamento administrado conforme protocolo. "
            "Remédio: dipirona 500mg."
        )
        request_data = {
            "investment_id": invest_result_base.investment_id,
            "invest_result": {
                "investment_id": invest_result_base.investment_id,
                "status": invest_result_base.status,
                "criteria_results": [
                    {
                        "criterion_id": c.criterion_id,
                        "criterion_name": c.criterion_name,
                        "result": c.result,
                        "evidence": c.evidence,
                    }
                    for c in invest_result_base.criteria_results
                ],
                "summary": invest_result_base.summary,
                "metadata": invest_result_base.metadata,
            },
        }

        # Act
        response = client.post("/api/v1/compliance/analyze", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "detected_rules" in data
        rule_ids = [r["rule_id"] for r in data["detected_rules"]]
        assert "RULE_007" in rule_ids, "RULE_007 deve ser detectada em prescrição com medicamento"

    def test_post_analyze_invalid_request_returns_400(self):
        """Teste: POST /api/v1/compliance/analyze com requisição inválida retorna 400."""
        # Arrange
        invalid_request = {
            "investment_id": "",  # investment_id vazio
            "invest_result": None,  # invest_result None
        }

        # Act
        response = client.post("/api/v1/compliance/analyze", json=invalid_request)

        # Assert
        assert response.status_code in [400, 422]  # 400 para erro de validação, 422 para Pydantic

    def test_post_analyze_returns_complete_response(self, invest_result_base):
        """Teste: POST /api/v1/compliance/analyze retorna resposta completa."""
        # Arrange
        invest_result_base.summary = "Paciente com prescrição médica"
        request_data = {
            "investment_id": invest_result_base.investment_id,
            "invest_result": {
                "investment_id": invest_result_base.investment_id,
                "status": invest_result_base.status,
                "criteria_results": [
                    {
                        "criterion_id": c.criterion_id,
                        "criterion_name": c.criterion_name,
                        "result": c.result,
                        "evidence": c.evidence,
                    }
                    for c in invest_result_base.criteria_results
                ],
                "summary": invest_result_base.summary,
                "metadata": invest_result_base.metadata,
            },
        }

        # Act
        response = client.post("/api/v1/compliance/analyze", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "analysis_id" in data
        assert "investment_id" in data
        assert "status" in data
        assert "detected_rules" in data
        assert "compliance_gaps" in data
        assert "requirements" in data
        assert "summary" in data
        assert "timestamp" in data
        assert "metadata" in data
        assert data["analysis_id"].startswith("COMP-")

    def test_post_analyze_file_not_found_returns_404(self):
        """Teste: POST /api/v1/compliance/analyze-file com arquivo inexistente retorna 404."""
        # Arrange
        request_data = {"file_path": "data/samples/nonexistent_file.json"}

        # Act
        response = client.post("/api/v1/compliance/analyze-file", json=request_data)

        # Assert
        assert response.status_code == 404

    def test_post_analyze_file_with_valid_file(self):
        """Teste: POST /api/v1/compliance/analyze-file com arquivo válido."""
        # Arrange
        request_data = {"file_path": "data/samples/invest_result_sample.json"}

        # Act
        response = client.post("/api/v1/compliance/analyze-file", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "analysis_id" in data
        assert "investment_id" in data
        assert data["investment_id"] == "INV-2026-001"

    def test_post_analyze_response_has_correct_content_type(self, invest_result_base):
        """Teste: POST /api/v1/compliance/analyze retorna content-type application/json."""
        # Arrange
        request_data = {
            "investment_id": invest_result_base.investment_id,
            "invest_result": {
                "investment_id": invest_result_base.investment_id,
                "status": invest_result_base.status,
                "criteria_results": [
                    {
                        "criterion_id": c.criterion_id,
                        "criterion_name": c.criterion_name,
                        "result": c.result,
                        "evidence": c.evidence,
                    }
                    for c in invest_result_base.criteria_results
                ],
                "summary": invest_result_base.summary,
                "metadata": invest_result_base.metadata,
            },
        }

        # Act
        response = client.post("/api/v1/compliance/analyze", json=request_data)

        # Assert
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
