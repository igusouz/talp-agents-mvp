"""
Testes para o adapter de resultado do invest-agent
"""

import json
from pathlib import Path

import pytest

from app.schemas.models import InvestCriterionResult, InvestResult
from app.services.file_loader import FileLoader
from app.services.invest_result_adapter import InvestResultAdapter


class TestInvestResultAdapter:
    """Testes para o adapter que normaliza resultado do invest-agent."""

    @pytest.fixture
    def invest_result_with_failures(self):
        """Fixture com um InvestResult contendo failures."""
        return InvestResult(
            investment_id="INV-001",
            status="warning",
            criteria_results=[
                InvestCriterionResult(
                    criterion_id="EST-001",
                    criterion_name="Estimable",
                    result=True,
                    evidence="Dados disponíveis",
                ),
                InvestCriterionResult(
                    criterion_id="TEST-001",
                    criterion_name="Testable",
                    result=False,
                    evidence="Histórico insuficiente",
                ),
                InvestCriterionResult(
                    criterion_id="VERIF-001",
                    criterion_name="Verificável",
                    result=True,
                    evidence="Documentação completa",
                ),
            ],
            summary="Alguns critérios falharam",
        )

    # =========================================================================
    # TESTES OBRIGATÓRIOS
    # =========================================================================

    def test_invest_result_with_estimable_warning_returns_warnings(self):
        """Deve retornar warnings contendo 'Estimable' (ou similar)."""
        invest_result = InvestResult(
            investment_id="INV-TEST",
            status="warning",
            criteria_results=[
                InvestCriterionResult(
                    criterion_id="EST-001",
                    criterion_name="Estimable",
                    result=False,
                    evidence="Dados não disponíveis",
                )
            ],
            summary="Teste",
        )

        context = InvestResultAdapter.adapt("INV-TEST", invest_result)

        assert "Estimable" in context.failed, "Estimable deveria estar em failed"

    def test_invest_result_with_testable_failed_returns_failed(self):
        """Deve retornar failed contendo 'Testable'."""
        invest_result = InvestResult(
            investment_id="INV-TEST",
            status="rejected",
            criteria_results=[
                InvestCriterionResult(
                    criterion_id="TEST-001",
                    criterion_name="Testable",
                    result=False,
                    evidence="Histórico insuficiente",
                )
            ],
            summary="Teste",
        )

        context = InvestResultAdapter.adapt("INV-TEST", invest_result)

        assert "Testable" in context.failed, "Testable deveria estar em failed"
        assert context.overall_status == "rejected"

    def test_absent_invest_result_returns_unknown_status(self):
        """Deve retornar overall_status 'unknown' quando invest_result é None."""
        context = InvestResultAdapter.adapt("INV-TEST", None)

        assert context.overall_status == "unknown"
        assert context.invest_result is None
        assert len(context.failed) == 0
        assert "Resultado do invest-agent não disponível" in context.detected_problems

    def test_file_loader_loads_json_sample(self):
        """Deve carregar o JSON de exemplo."""
        file_path = "data/samples/invest_result_sample.json"

        data = FileLoader.load_json(file_path)

        assert data is not None
        assert isinstance(data, dict)
        assert "investment_id" in data
        assert "criteria_results" in data

    # =========================================================================
    # TESTES ADICIONAIS
    # =========================================================================

    def test_adapt_with_valid_invest_result(self, invest_result_with_failures):
        """Deve adaptar um InvestResult válido."""
        context = InvestResultAdapter.adapt("INV-001", invest_result_with_failures)

        assert context.investment_id == "INV-001"
        assert context.invest_result is not None
        assert context.overall_status in ["approved", "warning", "rejected"]

    def test_adapt_extracts_failed_criteria(self, invest_result_with_failures):
        """Deve extrair critérios que falharam."""
        context = InvestResultAdapter.adapt("INV-001", invest_result_with_failures)

        assert "Testable" in context.failed
        assert len(context.failed) == 1

    def test_adapt_calculates_score(self, invest_result_with_failures):
        """Deve calcular score baseado em critérios."""
        context = InvestResultAdapter.adapt("INV-001", invest_result_with_failures)

        # 2 de 3 critérios passaram = 66.67%
        assert context.score is not None
        assert 60 < context.score < 70, f"Score esperado ~66%, recebido {context.score}"

    def test_adapt_generates_recommendations(self, invest_result_with_failures):
        """Deve gerar recomendações."""
        context = InvestResultAdapter.adapt("INV-001", invest_result_with_failures)

        assert len(context.recommendations) > 0
        assert any("Testable" in rec for rec in context.recommendations)

    def test_adapt_with_all_passed_criteria(self):
        """Deve retornar overall_status 'approved' quando todos passam."""
        invest_result = InvestResult(
            investment_id="INV-APPROVED",
            status="approved",
            criteria_results=[
                InvestCriterionResult(
                    criterion_id="EST-001",
                    criterion_name="Estimable",
                    result=True,
                ),
                InvestCriterionResult(
                    criterion_id="TEST-001",
                    criterion_name="Testable",
                    result=True,
                ),
            ],
            summary="Todos os critérios passaram",
        )

        context = InvestResultAdapter.adapt("INV-APPROVED", invest_result)

        assert context.overall_status == "approved"
        assert len(context.failed) == 0
        assert len(context.warnings) == 0
        assert context.score == 100.0

    def test_adapt_with_all_failed_criteria(self):
        """Deve retornar overall_status 'rejected' quando todos falham."""
        invest_result = InvestResult(
            investment_id="INV-REJECTED",
            status="rejected",
            criteria_results=[
                InvestCriterionResult(
                    criterion_id="EST-001",
                    criterion_name="Estimable",
                    result=False,
                ),
                InvestCriterionResult(
                    criterion_id="TEST-001",
                    criterion_name="Testable",
                    result=False,
                ),
            ],
            summary="Todos os critérios falharam",
        )

        context = InvestResultAdapter.adapt("INV-REJECTED", invest_result)

        assert context.overall_status == "rejected"
        assert len(context.failed) == 2
        assert context.score == 0.0

    def test_file_loader_loads_compliance_request_sample(self):
        """Deve carregar compliance_request_sample.json."""
        file_path = "data/samples/compliance_request_sample.json"

        data = FileLoader.load_json(file_path)

        assert data is not None
        assert "investment_id" in data
        assert "invest_result" in data

    def test_file_loader_raises_on_missing_file(self):
        """Deve lançar FileNotFoundError se arquivo não existe."""
        with pytest.raises(FileNotFoundError):
            FileLoader.load_json("data/nonexistent/file.json")

    def test_file_loader_raises_on_invalid_json(self, tmp_path):
        """Deve lançar JSONDecodeError se JSON é inválido."""
        invalid_json_file = tmp_path / "invalid.json"
        invalid_json_file.write_text("{invalid json}")

        with pytest.raises(json.JSONDecodeError):
            FileLoader.load_json(str(invalid_json_file))

    def test_adapt_preserves_investment_id(self, invest_result_with_failures):
        """Deve preservar o investment_id."""
        context = InvestResultAdapter.adapt("INV-CUSTOM-ID", invest_result_with_failures)

        assert context.investment_id == "INV-CUSTOM-ID"

    def test_adapt_with_empty_criteria_results(self):
        """Deve lidar com criteria_results vazio."""
        invest_result = InvestResult(
            investment_id="INV-EMPTY",
            status="unknown",
            criteria_results=[],
            summary="Sem critérios",
        )

        context = InvestResultAdapter.adapt("INV-EMPTY", invest_result)

        assert context.overall_status == "unknown"
        assert context.score == 0.0
        assert len(context.failed) == 0

    def test_adapt_generates_detected_problems(self, invest_result_with_failures):
        """Deve gerar lista de problemas detectados."""
        context = InvestResultAdapter.adapt("INV-001", invest_result_with_failures)

        assert len(context.detected_problems) > 0
        assert any("Testable" in problem for problem in context.detected_problems)

    def test_file_loader_returns_dict_not_list(self):
        """FileLoader.load_json deve retornar dict, não list."""
        file_path = "data/samples/invest_result_sample.json"

        data = FileLoader.load_json(file_path)

        assert isinstance(data, dict), "load_json deve retornar dict"

    def test_file_loader_load_csv_returns_list(self):
        """FileLoader.load_csv deve retornar list de dicts."""
        file_path = "data/catalog_rules_v1.csv"

        data = FileLoader.load_csv(file_path)

        assert isinstance(data, list)
        assert len(data) == 8

    def test_score_calculation_one_of_three(self):
        """Score de 1/3 deve ser ~33%."""
        invest_result = InvestResult(
            investment_id="INV-SCORE",
            status="warning",
            criteria_results=[
                InvestCriterionResult(
                    criterion_id="C1", criterion_name="Critério 1", result=True
                ),
                InvestCriterionResult(
                    criterion_id="C2", criterion_name="Critério 2", result=False
                ),
                InvestCriterionResult(
                    criterion_id="C3", criterion_name="Critério 3", result=False
                ),
            ],
            summary="Teste",
        )

        context = InvestResultAdapter.adapt("INV-SCORE", invest_result)

        assert 32 < context.score < 34, f"Score esperado ~33%, recebido {context.score}"

    def test_invest_context_has_timestamp(self):
        """InvestContext deve ter timestamp."""
        context = InvestResultAdapter.adapt("INV-001", None)

        assert context.timestamp is not None

    def test_adapt_does_not_modify_original_invest_result(self, invest_result_with_failures):
        """Adapter não deve modificar o InvestResult original."""
        original_failed_count = sum(1 for c in invest_result_with_failures.criteria_results if not c.result)

        context = InvestResultAdapter.adapt("INV-001", invest_result_with_failures)

        # Verificar que original não mudou
        assert sum(1 for c in invest_result_with_failures.criteria_results if not c.result) == original_failed_count
