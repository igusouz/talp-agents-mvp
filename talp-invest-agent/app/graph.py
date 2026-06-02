from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.config.settings import Settings, load_settings
from app.graph_state import AgentState
from app.nodes.audit_log import build_audit_log_node
from app.nodes.classification import classification_node
from app.nodes.evidence_validation import evidence_validation_node
from app.nodes.input_validation import input_validation_node
from app.nodes.invest_analysis import build_invest_analysis_node
from app.nodes.output_validation import output_validation_node
from app.nodes.prompt_loader import build_prompt_loader_node
from app.nodes.report_generation import build_report_generation_node
from app.schemas.models import FinalOutput
from app.services.audit_logger import AuditLogger
from app.services.heuristic_backend import HeuristicInvestAnalyzer, HeuristicReportGenerator
from app.services.llm_client import (
    GeminiInvestAnalyzer,
    GeminiReportGenerator,
    InvestAnalyzer,
    ReportGenerator,
)
from app.services.prompt_registry import PromptRegistry


class InvestAgent:
    def __init__(
        self,
        settings: Settings,
        analyzer: InvestAnalyzer,
        report_generator: ReportGenerator,
    ) -> None:
        self.settings = settings
        self.registry = PromptRegistry(settings.prompt_dir)
        self.audit_logger = AuditLogger(settings.audit_log_dir)
        self.analyzer = analyzer
        self.report_generator = report_generator
        self._compiled = self._build_graph()

    def _build_graph(self):
        try:
            from langgraph.graph import END, StateGraph
        except ImportError:
            return None

        graph = StateGraph(AgentState)
        graph.add_node("input_validation", input_validation_node)
        graph.add_node("prompt_loader", build_prompt_loader_node(self.registry))
        graph.add_node("invest_analysis", build_invest_analysis_node(self.analyzer))
        graph.add_node("evidence_validation", evidence_validation_node)
        graph.add_node("classification", classification_node)
        graph.add_node("report_generation", build_report_generation_node(self.report_generator))
        graph.add_node("output_validation", output_validation_node)
        graph.add_node("audit_log", build_audit_log_node(self.audit_logger))

        graph.set_entry_point("input_validation")
        graph.add_edge("input_validation", "prompt_loader")
        graph.add_edge("prompt_loader", "invest_analysis")
        graph.add_edge("invest_analysis", "evidence_validation")
        graph.add_edge("evidence_validation", "classification")
        graph.add_edge("classification", "report_generation")
        graph.add_edge("report_generation", "output_validation")
        graph.add_edge("output_validation", "audit_log")
        graph.add_edge("audit_log", END)
        return graph.compile()

    def run(self, user_story_text: str) -> FinalOutput:
        state: AgentState = {
            "execution_id": str(uuid4()),
            "user_story_text": user_story_text,
            "errors": [],
        }
        if self._compiled is not None:
            result = self._compiled.invoke(state)
        else:
            result = self._run_sequential(state)
        return result["final_output"]

    def _run_sequential(self, state: AgentState) -> AgentState:
        state = input_validation_node(state)
        state = build_prompt_loader_node(self.registry)(state)
        state = build_invest_analysis_node(self.analyzer)(state)
        state = evidence_validation_node(state)
        state = classification_node(state)
        state = build_report_generation_node(self.report_generator)(state)
        state = output_validation_node(state)
        state = build_audit_log_node(self.audit_logger)(state)
        return state


def build_agent(
    backend: str = "llm",
    project_root: Path | None = None,
) -> InvestAgent:
    settings = load_settings(project_root)
    if backend == "heuristic":
        analyzer = HeuristicInvestAnalyzer()
        report_generator = HeuristicReportGenerator()
    elif backend == "llm":
        analyzer = GeminiInvestAnalyzer(settings.llm_model, temperature=0.0)
        report_generator = GeminiReportGenerator(settings.llm_model, temperature=0.0)
    else:
        raise ValueError("backend must be 'llm' or 'heuristic'")
    return InvestAgent(settings, analyzer, report_generator)
