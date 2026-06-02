from __future__ import annotations

from app.graph_state import AgentState
from app.schemas.models import BadStoryReport, ReportProblem
from app.services.evidence_checker import validate_report_guardrails
from app.services.llm_client import ReportGenerator


def _fallback_report(state: AgentState) -> BadStoryReport:
    problems: list[ReportProblem] = []
    for criterion, assessment in state["invest_analysis"].as_criteria_dict().items():
        if assessment.status == "fail":
            problems.append(
                ReportProblem(
                    criterion=criterion,
                    problem=f"The {criterion} criterion failed according to the INVEST rubric.",
                    evidence=assessment.evidence,
                    explanation=assessment.reason,
                )
            )
    return BadStoryReport(problems=problems)


def build_report_generation_node(generator: ReportGenerator):
    def report_generation_node(state: AgentState) -> AgentState:
        if state["classification"].category == "boa":
            state["report"] = None
            state["report_model_name"] = generator.model_name
            return state

        prompt = state["prompts"]["bad_story_report"]
        report = generator.generate(
            state["agent_input"].user_story_text,
            state["invest_analysis"],
            prompt,
        )
        errors = validate_report_guardrails(
            state["agent_input"].user_story_text,
            state["classification"].failed_criteria,
            report,
        )
        if errors:
            state.setdefault("errors", []).extend(errors)
            report = _fallback_report(state)
        state["report"] = report
        state["report_model_name"] = generator.model_name
        return state

    return report_generation_node

