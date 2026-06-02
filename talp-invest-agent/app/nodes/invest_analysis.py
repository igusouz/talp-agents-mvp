from __future__ import annotations

from app.graph_state import AgentState
from app.services.llm_client import InvestAnalyzer


def build_invest_analysis_node(analyzer: InvestAnalyzer):
    def invest_analysis_node(state: AgentState) -> AgentState:
        prompt = state["prompts"]["invest_analysis"]
        state["invest_analysis"] = analyzer.analyze(
            state["agent_input"].user_story_text,
            prompt,
        )
        state["analysis_model_name"] = analyzer.model_name
        return state

    return invest_analysis_node

