from __future__ import annotations

from app.graph_state import AgentState
from app.services.evidence_checker import enforce_analysis_guardrails


def evidence_validation_node(state: AgentState) -> AgentState:
    analysis, errors = enforce_analysis_guardrails(
        state["agent_input"].user_story_text,
        state["invest_analysis"],
    )
    state["invest_analysis"] = analysis
    state.setdefault("errors", []).extend(errors)
    return state

