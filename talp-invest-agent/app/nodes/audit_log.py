from __future__ import annotations

import hashlib
import json

from app.graph_state import AgentState
from app.services.audit_logger import AuditLogger


def build_audit_log_node(logger: AuditLogger):
    def audit_log_node(state: AgentState) -> AgentState:
        story = state["agent_input"].user_story_text
        record = {
            "execution_id": state["execution_id"],
            "input_hash": hashlib.sha256(story.encode("utf-8")).hexdigest(),
            "input_text": story,
            "prompt_records": {
                name: prompt.model_dump()
                for name, prompt in state["prompt_records"].items()
            },
            "prompt_templates": {
                name: prompt.template for name, prompt in state["prompts"].items()
            },
            "rendered_prompts": {
                "invest_analysis": state["prompts"]["invest_analysis"].format(
                    user_story_text=story
                ),
                "bad_story_report": None
                if state["classification"].category == "boa"
                else state["prompts"]["bad_story_report"].format(
                    user_story_text=story,
                    invest_analysis_json=json.dumps(
                        state["invest_analysis"].model_dump(),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                ),
            },
            "validated_step_outputs": {
                "invest_analysis": state["invest_analysis"].model_dump(),
                "classification": state["classification"].model_dump(),
                "report": None if state["report"] is None else state["report"].model_dump(),
            },
            "final_output": state["final_output"].model_dump(mode="json"),
            "errors": state.get("errors", []),
        }
        state["audit_log_path"] = str(logger.append(record))
        return state

    return audit_log_node
