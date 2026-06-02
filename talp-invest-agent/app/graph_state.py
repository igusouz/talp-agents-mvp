from __future__ import annotations

from typing import Any, TypedDict

from app.schemas.models import (
    AgentInput,
    BadStoryReport,
    Classification,
    FinalOutput,
    InvestAnalysis,
    PromptRecord,
)
from app.services.prompt_registry import PromptTemplate


class AgentState(TypedDict, total=False):
    execution_id: str
    user_story_text: str
    agent_input: AgentInput
    prompts: dict[str, PromptTemplate]
    prompt_records: dict[str, PromptRecord]
    invest_analysis: InvestAnalysis
    classification: Classification
    report: BadStoryReport | None
    final_output: FinalOutput
    errors: list[str]
    audit_log_path: str
    analysis_model_name: str
    report_model_name: str
    raw: dict[str, Any]

