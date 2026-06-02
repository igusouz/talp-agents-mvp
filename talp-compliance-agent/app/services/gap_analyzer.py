"""
Serviço: Gap Analyzer - Analisar gaps de conformidade
"""

from app.schemas.models import ComplianceGap


class GapAnalyzer:
    """Analisar gaps de conformidade."""

    @staticmethod
    def analyze(
        matched_rules: list, all_catalog_rules: list, dependency_gaps: list
    ) -> list:
        """
        Analisar gaps de conformidade.

        Uma lacuna é identificada quando uma regra mandatória ou de bloqueio
        não foi detectada, ou quando há dependências não satisfeitas.

        Args:
            matched_rules: Lista de regras detectadas (dict com rule_id, name, etc.)
            all_catalog_rules: Lista de todas as regras do catálogo
            dependency_gaps: Lacunas de dependência (já criadas)

        Returns:
            Lista de ComplianceGap com todas as lacunas identificadas
        """
        gaps = list(dependency_gaps)  # Começar com as lacunas de dependência

        detected_rule_ids = set(rule.get("rule_id") for rule in matched_rules)

        # Verificar cada regra do catálogo
        for catalog_rule in all_catalog_rules:
            rule_id = catalog_rule.rule_id
            is_mandatory = catalog_rule.mandatory
            is_blocking = catalog_rule.blocking

            # Se a regra é mandatória ou bloqueante e não foi detectada, criar lacuna
            if (is_mandatory or is_blocking) and rule_id not in detected_rule_ids:
                severity = "critical" if is_blocking else "high"

                gap = ComplianceGap(
                    rule_id=rule_id,
                    rule_name=catalog_rule.name,
                    severity=severity,
                    gap_description=f"Regra mandatória não detectada: {catalog_rule.description}",
                    remediation_suggestion=f"Verificar se {catalog_rule.keywords} estão presentes",
                    blocking=is_blocking,
                )
                gaps.append(gap)

        return gaps
