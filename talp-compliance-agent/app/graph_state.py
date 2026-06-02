"""
Estado do LangGraph
"""

from typing import Any


class GraphState:
    """Estado do grafo de agente."""

    investment_id: str
    invest_result: dict
    catalog_rules: list
    matched_rules: list
    dependencies: dict
    gaps: list
    analysis_result: dict
    audit_logs: list

    def __init__(self):
        """Inicializar estado."""
        self.investment_id = None
        self.invest_result = {}
        self.catalog_rules = []
        self.matched_rules = []
        self.dependencies = {}
        self.gaps = []
        self.analysis_result = {}
        self.audit_logs = []

    def to_dict(self) -> dict:
        """Converter para dicionário."""
        return {
            "investment_id": self.investment_id,
            "invest_result": self.invest_result,
            "catalog_rules": self.catalog_rules,
            "matched_rules": self.matched_rules,
            "dependencies": self.dependencies,
            "gaps": self.gaps,
            "analysis_result": self.analysis_result,
            "audit_logs": self.audit_logs,
        }
