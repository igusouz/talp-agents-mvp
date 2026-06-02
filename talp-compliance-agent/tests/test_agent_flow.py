"""
Testes: Agent Flow - Fluxo completo de análise de compliance
"""

import pytest

from app.graph import can_continue_to_bdd, run_compliance_graph
from app.schemas.models import (
    ComplianceAnalysisRequest,
    ComplianceGap,
    DetectedRule,
    InvestCriterionResult,
    InvestResult,
)


class TestComplianceAnalysisFlow:
    """Testes do fluxo completo de análise de compliance."""

    @pytest.fixture
    def invest_result_base(self):
        """Fixture: Resultado base do invest-agent."""
        return InvestResult(
            investment_id="INV-2026-TEST",
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

    def test_us_with_antibiotic_detects_rule_008(self, invest_result_base):
        """Teste 1: US com antibiótico detecta RULE_008."""
        # Arrange
        invest_result_base.summary = (
            "Paciente recebeu prescrição com antibiótico. "
            "Recomendação de usar medicamento antimicrobiano. "
            "CCIH deve validar o uso de antibióticos."
        )
        request = ComplianceAnalysisRequest(
            investment_id="INV-2026-TEST",
            invest_result=invest_result_base,
        )

        # Act
        response = run_compliance_graph(request)

        # Assert
        rule_ids = [r.rule_id for r in response.detected_rules]
        assert "RULE_008" in rule_ids, "RULE_008 deve ser detectada em prescrição com antibiótico"

        # Verificar que a regra foi detectada corretamente
        rule_008 = next((r for r in response.detected_rules if r.rule_id == "RULE_008"), None)
        assert rule_008 is not None
        assert rule_008.matched is True
        assert rule_008.confidence > 0

    def test_us_with_medication_detects_rule_007(self, invest_result_base):
        """Teste 2: US com medicamento detecta RULE_007."""
        # Arrange
        invest_result_base.summary = (
            "Paciente medicado com prescrição. "
            "Medicamento administrado conforme protocolo. "
            "Remédio: dipirona 500mg."
        )
        request = ComplianceAnalysisRequest(
            investment_id="INV-2026-TEST",
            invest_result=invest_result_base,
        )

        # Act
        response = run_compliance_graph(request)

        # Assert
        rule_ids = [r.rule_id for r in response.detected_rules]
        assert "RULE_007" in rule_ids, "RULE_007 deve ser detectada em prescrição com medicamento"

    def test_us_with_antibiotic_without_prescription_creates_dependency_gap(
        self, invest_result_base
    ):
        """Teste 3: US com antibiótico sem prescrição gera dependência com RULE_007."""
        # Arrange
        # Detectar RULE_008 (antibiótico) mas NÃO RULE_007 (prescrição)
        invest_result_base.summary = "Paciente com antibiótico antimicrobiano detectado"
        request = ComplianceAnalysisRequest(
            investment_id="INV-2026-TEST",
            invest_result=invest_result_base,
        )

        # Act
        response = run_compliance_graph(request)

        # Assert
        # Verificar se RULE_008 foi detectada
        rule_008_detected = any(r.rule_id == "RULE_008" for r in response.detected_rules)
        rule_007_detected = any(r.rule_id == "RULE_007" for r in response.detected_rules)

        # Se RULE_008 detectada mas RULE_007 não, deve haver uma lacuna de dependência
        if rule_008_detected and not rule_007_detected:
            # Deve haver uma lacuna de dependência ou uma lacuna para RULE_007
            dependency_or_missing_gaps = [
                g
                for g in response.compliance_gaps
                if (
                    (
                        "prescrição" in g.gap_description.lower()
                        and "antimicrobianos" in g.gap_description.lower()
                    )
                    or g.rule_id == "RULE_007"
                )
            ]
            assert (
                len(dependency_or_missing_gaps) > 0
            ), "Deve haver lacuna de dependência para prescrição ou RULE_007 não satisfeita"

    def test_invest_rejected_makes_can_continue_to_bdd_false(self):
        """Teste 4: INVEST rejected faz can_continue_to_bdd ser false."""
        # Arrange
        invest_result = InvestResult(
            investment_id="INV-2026-REJECTED",
            status="rejected",  # Status rejected
            criteria_results=[
                InvestCriterionResult(
                    criterion_id="EST-001",
                    criterion_name="Estimable",
                    result=False,
                ),
            ],
            summary="Investimento rejeitado",
        )
        request = ComplianceAnalysisRequest(
            investment_id="INV-2026-REJECTED",
            invest_result=invest_result,
        )

        # Act
        response = run_compliance_graph(request)

        # Assert
        can_continue = response.metadata.get("can_continue_to_bdd", True)
        assert (
            can_continue is False
        ), "can_continue_to_bdd deve ser False quando invest_result.overall_status = rejected"

    def test_invest_testable_failed_makes_can_continue_to_bdd_false(self):
        """Teste 5: INVEST testable failed faz can_continue_to_bdd ser false."""
        # Arrange
        invest_result = InvestResult(
            investment_id="INV-2026-TESTABLE-FAILED",
            status="warning",
            criteria_results=[
                InvestCriterionResult(
                    criterion_id="TEST-001",
                    criterion_name="Testable",
                    result=False,  # Testable failed
                    evidence="Histórico insuficiente",
                ),
                InvestCriterionResult(
                    criterion_id="EST-001",
                    criterion_name="Estimable",
                    result=True,
                ),
            ],
            summary="Investimento com testable falho",
        )
        request = ComplianceAnalysisRequest(
            investment_id="INV-2026-TESTABLE-FAILED",
            invest_result=invest_result,
        )

        # Act
        response = run_compliance_graph(request)

        # Assert
        can_continue = response.metadata.get("can_continue_to_bdd", True)
        assert (
            can_continue is False
        ), "can_continue_to_bdd deve ser False quando critério Testable está failed"

    def test_compliance_analysis_response_structure(self, invest_result_base):
        """Teste adicional: Validar estrutura completa da response."""
        # Arrange
        invest_result_base.summary = (
            "Paciente com prescrição médica e medicamento"
        )
        request = ComplianceAnalysisRequest(
            investment_id="INV-2026-TEST",
            invest_result=invest_result_base,
        )

        # Act
        response = run_compliance_graph(request)

        # Assert
        # Validar campos obrigatórios
        assert response.analysis_id.startswith("COMP-")
        assert response.investment_id == "INV-2026-TEST"
        assert response.status in ["compliant", "non_compliant", "partial"]
        assert isinstance(response.detected_rules, list)
        assert isinstance(response.compliance_gaps, list)
        assert isinstance(response.requirements, list)
        assert response.summary is not None
        assert "can_continue_to_bdd" in response.metadata

    def test_invalid_request_raises_error(self):
        """Teste: Requisição inválida levanta erro."""
        # Arrange
        from pydantic_core import ValidationError as PydanticValidationError

        # Act & Assert
        # Primeiro teste: investment_id vazio levanta erro
        invest_result = InvestResult(
            investment_id="INV-2026-TEST",
            status="warning",
            criteria_results=[],
            summary="Test",
        )

        with pytest.raises(ValueError):
            request = ComplianceAnalysisRequest(
                investment_id="",  # investment_id vazio
                invest_result=invest_result,
            )
            run_compliance_graph(request)

        # Segundo teste: invest_result None levanta erro do Pydantic
        with pytest.raises(PydanticValidationError):
            ComplianceAnalysisRequest(
                investment_id="INV-2026-TEST",
                invest_result=None,  # invest_result None
            )

    def test_all_detected_rules_in_catalog(self, invest_result_base):
        """Teste: Todas as regras detectadas devem estar no catálogo."""
        # Arrange
        invest_result_base.summary = "Triagem com sinais vitais e Manchester"
        request = ComplianceAnalysisRequest(
            investment_id="INV-2026-TEST",
            invest_result=invest_result_base,
        )

        # Act
        response = run_compliance_graph(request)

        # Assert - Esta função já valida internamente, mas vamos verificar
        detected_rule_ids = set(r.rule_id for r in response.detected_rules)
        # Devem estar dentro das regras conhecidas
        known_rules = {
            "RULE_001",
            "RULE_002",
            "RULE_003",
            "RULE_004",
            "RULE_005",
            "RULE_006",
            "RULE_007",
            "RULE_008",
        }
        for rule_id in detected_rule_ids:
            assert (
                rule_id in known_rules
            ), f"Regra {rule_id} não está no catálogo conhecido"

    def test_mandatory_and_blocking_rules_classification(self, invest_result_base):
        """Teste: Regras mandatórias e bloqueantes são classificadas corretamente."""
        # Arrange
        invest_result_base.summary = (
            "Triagem com sinais vitais. "
            "Classificação Manchester. "
            "HDA registrada. "
            "CID e conduta médica."
        )
        request = ComplianceAnalysisRequest(
            investment_id="INV-2026-TEST",
            invest_result=invest_result_base,
        )

        # Act
        response = run_compliance_graph(request)

        # Assert
        mandatory_rules = response.metadata.get("mandatory_rules", [])
        blocking_rules = response.metadata.get("blocking_rules", [])

        # Todas as regras detectadas devem estar em uma das listas
        detected_rule_ids = set(r.rule_id for r in response.detected_rules)

        # RULE_001, RULE_002, RULE_003, RULE_004, RULE_005, RULE_007, RULE_008 são mandatórias
        expected_mandatory = {
            "RULE_001",
            "RULE_002",
            "RULE_003",
            "RULE_004",
            "RULE_005",
            "RULE_007",
            "RULE_008",
        }

        for rule_id in detected_rule_ids:
            if rule_id in expected_mandatory:
                assert (
                    rule_id in mandatory_rules
                ), f"{rule_id} deve estar em mandatory_rules"
