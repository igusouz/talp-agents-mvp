"""
Serviço: Invest Result Adapter - Normalizar resultado do talp-invest-agent
"""

from typing import Optional

from app.schemas.models import InvestContext, InvestResult


class InvestResultAdapter:
    """Adapter para converter e normalizar resultado do agente de investimentos."""

    @staticmethod
    def adapt(
        investment_id: str, invest_result: Optional[InvestResult] = None
    ) -> InvestContext:
        """
        Adaptar resultado do invest-agent para InvestContext.

        Args:
            investment_id: ID do investimento
            invest_result: Resultado do talp-invest-agent (pode ser None)

        Returns:
            InvestContext normalizado
        """
        if invest_result is None:
            # Se invest_result está vazio, retornar contexto com status "unknown"
            return InvestContext(
                investment_id=investment_id,
                overall_status="unknown",
                score=None,
                warnings=[],
                failed=[],
                detected_problems=["Resultado do invest-agent não disponível"],
                recommendations=["Aguardando resultado do talp-invest-agent"],
                invest_result=None,
            )

        # Extrair warnings e failed dos critérios
        warnings = []
        failed = []
        detected_problems = []

        for criterion in invest_result.criteria_results:
            if criterion.result is False:
                # Critério falhou
                failed.append(criterion.criterion_name)
                problem = f"{criterion.criterion_name}: {criterion.evidence or 'sem evidência'}"
                detected_problems.append(problem)
            elif hasattr(criterion, "status") and criterion.status == "warning":
                # Critério com warning
                warnings.append(criterion.criterion_name)
                if criterion.evidence:
                    detected_problems.append(f"AVISO em {criterion.criterion_name}: {criterion.evidence}")

        # Determinar overall_status
        if failed:
            overall_status = "rejected"
        elif warnings:
            overall_status = "warning"
        elif invest_result.status == "approved":
            overall_status = "approved"
        else:
            overall_status = invest_result.status.lower()

        # Calcular score baseado em critérios
        score = InvestResultAdapter._calculate_score(invest_result)

        # Gerar recomendações
        recommendations = InvestResultAdapter._generate_recommendations(failed, warnings)

        return InvestContext(
            investment_id=investment_id,
            overall_status=overall_status,
            score=score,
            warnings=warnings,
            failed=failed,
            detected_problems=detected_problems,
            recommendations=recommendations,
            invest_result=invest_result,
        )

    @staticmethod
    def _calculate_score(invest_result: InvestResult) -> float:
        """
        Calcular score baseado nos critérios avaliados.

        Args:
            invest_result: Resultado do invest-agent

        Returns:
            Score de 0 a 100
        """
        if not invest_result.criteria_results:
            return 0.0

        passed = sum(1 for c in invest_result.criteria_results if c.result is True)
        total = len(invest_result.criteria_results)

        score = (passed / total) * 100
        return round(score, 2)

    @staticmethod
    def _generate_recommendations(failed: list[str], warnings: list[str]) -> list[str]:
        """
        Gerar recomendações baseado em failures e warnings.

        Args:
            failed: Lista de critérios que falharam
            warnings: Lista de critérios com warning

        Returns:
            Lista de recomendações
        """
        recommendations = []

        if failed:
            recommendations.append(
                f"Resolver {len(failed)} critério(s) com falha antes de prosseguir"
            )
            for criterion in failed[:3]:  # Mostrar até 3
                recommendations.append(f"  - Revisar: {criterion}")

        if warnings:
            recommendations.append(f"Verificar {len(warnings)} critério(s) com warning")
            for criterion in warnings[:3]:  # Mostrar até 3
                recommendations.append(f"  - Analisar: {criterion}")

        if not recommendations:
            recommendations.append("Investimento aprovado - prosseguir com conformidade")

        return recommendations
