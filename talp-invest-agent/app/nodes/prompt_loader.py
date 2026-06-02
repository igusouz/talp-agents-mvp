from __future__ import annotations

from app.graph_state import AgentState
from app.services.prompt_registry import PromptRegistry


def build_prompt_loader_node(registry: PromptRegistry):
    def prompt_loader_node(state: AgentState) -> AgentState:
        invest_prompt = registry.load("invest_analysis", "1.0.0")
        report_prompt = registry.load("bad_story_report", "1.0.0")
        state["prompts"] = {
            "invest_analysis": invest_prompt,
            "bad_story_report": report_prompt,
        }
        state["prompt_records"] = {
            "invest_analysis": invest_prompt.record,
            "bad_story_report": report_prompt.record,
        }
        return state

    return prompt_loader_node

