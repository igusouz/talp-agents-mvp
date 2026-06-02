from __future__ import annotations

from app.graph_state import AgentState
from app.schemas.models import Classification


def classification_node(state: AgentState) -> AgentState:
    failed = state["invest_analysis"].failed_criteria()
    state["classification"] = Classification(
        category="boa" if not failed else "ruim",
        rule_applied="boa when all INVEST criteria pass; ruim when at least one criterion fails",
        failed_criteria=failed,
    )
    return state

