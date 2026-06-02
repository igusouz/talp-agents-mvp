from __future__ import annotations

from app.graph_state import AgentState
from app.schemas.models import AgentInput


def input_validation_node(state: AgentState) -> AgentState:
    parsed = AgentInput.model_validate({"user_story_text": state["user_story_text"]})
    state["agent_input"] = parsed
    state.setdefault("errors", [])
    return state

