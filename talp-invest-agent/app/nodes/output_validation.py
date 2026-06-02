from __future__ import annotations

from datetime import UTC, datetime

from app.graph_state import AgentState
from app.schemas.models import FinalOutput


SCHEMA_VERSION = "1.0.0"


def output_validation_node(state: AgentState) -> AgentState:
    records = state["prompt_records"]
    final = FinalOutput.model_validate(
        {
            "execution_id": state["execution_id"],
            "schema_version": SCHEMA_VERSION,
            "input": state["agent_input"].model_dump(),
            "result": {
                "step_1_invest_analysis": state["invest_analysis"].model_dump(),
                "step_2_classification": state["classification"].model_dump(),
                "step_3_report": None
                if state["report"] is None
                else state["report"].model_dump(),
            },
            "audit": {
                "prompt_versions": {
                    name: record.version for name, record in records.items()
                },
                "prompt_hashes": {
                    name: record.sha256 for name, record in records.items()
                },
                "model": {
                    "analysis": state.get("analysis_model_name"),
                    "report": state.get("report_model_name"),
                    "temperature": 0,
                },
                "created_at_utc": datetime.now(UTC),
            },
        }
    )
    state["final_output"] = final
    return state

