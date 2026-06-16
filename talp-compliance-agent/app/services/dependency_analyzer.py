"""
Serviço: Dependency Analyzer - Analisar dependências entre regras de compliance
"""

from typing import Optional

from app.schemas.models import ComplianceGap, RuleDependency


class DependencyAnalyzer:
    """Analisar dependências entre regras de compliance."""

    # Definir dependências entre regras
    RULE_DEPENDENCIES = {
        "RULE_008": {
            "depends_on": ["RULE_007"],
            "description": "Validação CCIH depende de prescrição médica válida",
            "gap_description": "Antimicrobianos sem prescrição válida não podem ser validados pela CCIH",
        },
        "RULE_004": {
            "depends_on": ["RULE_005"],
            "description": "Diagnóstico deve ter conduta médica associada",
            "gap_description": "Diagnóstico (CID) deve estar acompanhado de conduta médica definida",
        },
    }

    @staticmethod
    def analyze(matched_rules: list) -> dict:
        """
        Analisar dependências entre regras detectadas.

        Args:
            matched_rules: Lista de regras detectadas (dict com rule_id, name, etc.)

        Returns:
            Dicionário com dependências e lacunas de dependência
        """
        detected_rule_ids = set(rule.get("rule_id") for rule in matched_rules)
        dependencies = []
        dependency_gaps = []

        # Verificar cada regra detectada para suas dependências
        for detected_rule in matched_rules:
            rule_id = detected_rule.get("rule_id")

            # Verificar se a regra tem dependências definidas
            if rule_id in DependencyAnalyzer.RULE_DEPENDENCIES:
                dep_info = DependencyAnalyzer.RULE_DEPENDENCIES[rule_id]
                depends_on = dep_info["depends_on"]

                # Criar objeto RuleDependency
                dependency = RuleDependency(
                    rule_id=rule_id,
                    depends_on=depends_on,
                    description=dep_info["description"],
                )
                dependencies.append(dependency)

                # Se a regra de dependência não foi detectada, criar uma lacuna
                for dep_rule_id in depends_on:
                    if dep_rule_id not in detected_rule_ids:
                        # Encontrar o nome da regra de dependência
                        #dep_rule_name = dep_info["description"].split(" depende de ")[1].split("(")[0].strip()

                        gap = ComplianceGap(
                            rule_id=rule_id,
                            rule_name=detected_rule.get("name", rule_id),
                            severity="high",
                            gap_description=dep_info["gap_description"],
                            remediation_suggestion=f"Detectar e validar {dep_rule_id}",
                            blocking=True,
                        )
                        dependency_gaps.append(gap)

        return {
            "dependencies": [
                dep.model_dump() if hasattr(dep, "model_dump") else dep
                for dep in dependencies
            ],
            "dependency_gaps": [
                gap.model_dump() if hasattr(gap, "model_dump") else gap
                for gap in dependency_gaps
            ],
        }
