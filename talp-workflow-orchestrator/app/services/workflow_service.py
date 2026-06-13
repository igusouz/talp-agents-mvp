from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.clients.registry import AgentClientRegistry
from app.schemas.common import RequestContext
from app.schemas.compliance import ComplianceAnalysisRequest, InvestCriterionResult, InvestResult
from app.schemas.invest import InvestAgentRequest, InvestAgentResponse
from app.schemas.qa import QARequest
from app.schemas.workflow import (
    ApprovedStoryRequest,
    UserStoryInput,
    WorkflowCreateRequest,
    WorkflowCreateResponse,
    WorkflowStateResponse,
)


@dataclass
class WorkflowRecord:
    workflow_id: str
    stage: str
    original_story: UserStoryInput
    approved_story: UserStoryInput | None
    invest_response: InvestAgentResponse | None
    compliance_response: Any | None
    bdd_response: Any | None
    correlation_id: str
    updated_at: datetime


class WorkflowService:
    def __init__(self, registry: AgentClientRegistry) -> None:
        self._registry = registry
        self._workflows: dict[str, WorkflowRecord] = {}
        self._approval_tasks: dict[str, asyncio.Task[None]] = {}
        self._logger = logging.getLogger(__name__)

    async def start_workflow(self, request: WorkflowCreateRequest) -> WorkflowCreateResponse:
        workflow_id = uuid4().hex
        correlation_id = uuid4().hex

        context = RequestContext(correlation_id=correlation_id)

        story_text = self._render_story_text(request.user_story)
        invest_request = InvestAgentRequest(user_story_text=story_text)
        invest_response = await self._registry.invest.send(invest_request, context=context)

        compliance_request = self._build_compliance_request(invest_response)
        compliance_response = await self._registry.compliance.send(compliance_request, context=context)

        record = WorkflowRecord(
            workflow_id=workflow_id,
            stage="waiting_for_review",
            original_story=request.user_story,
            approved_story=None,
            invest_response=invest_response,
            compliance_response=compliance_response,
            bdd_response=None,
            correlation_id=correlation_id,
            updated_at=datetime.now(timezone.utc),
        )
        self._workflows[workflow_id] = record

        return WorkflowCreateResponse(
            workflow_id=workflow_id,
            stage="waiting_for_review",
            original_story=request.user_story,
            invest_analysis=invest_response.result.step_1_invest_analysis,
            compliance_analysis=compliance_response,
            correlation_id=correlation_id,
        )

    def get_workflow_state(self, workflow_id: str) -> WorkflowStateResponse:
        record = self._require_workflow(workflow_id)
        return WorkflowStateResponse(
            workflow_id=record.workflow_id,
            stage=record.stage,
            original_story=record.original_story,
            approved_story=record.approved_story,
            invest_analysis=(
                record.invest_response.result.step_1_invest_analysis
                if record.invest_response is not None
                else None
            ),
            compliance_analysis=record.compliance_response,
            bdd_analysis=record.bdd_response,
            updated_at=record.updated_at,
            correlation_id=record.correlation_id,
        )

    async def submit_approval(
        self,
        workflow_id: str,
        request: ApprovedStoryRequest,
    ) -> WorkflowStateResponse:
        record = self._require_workflow(workflow_id)

        running_task = self._approval_tasks.get(workflow_id)
        if running_task is not None and not running_task.done():
            return self.get_workflow_state(workflow_id)

        if record.stage == "bdd_done" and record.bdd_response is not None:
            return self.get_workflow_state(workflow_id)

        record.approved_story = request.approved_story
        record.bdd_response = None
        record.stage = "approved"
        record.updated_at = datetime.now(timezone.utc)
        self._schedule_bdd_analysis(workflow_id)

        return self.get_workflow_state(workflow_id)

    def _schedule_bdd_analysis(self, workflow_id: str) -> None:
        running_task = self._approval_tasks.get(workflow_id)
        if running_task is not None and not running_task.done():
            return

        task = asyncio.create_task(self._run_bdd_analysis(workflow_id))
        self._approval_tasks[workflow_id] = task

    async def _run_bdd_analysis(self, workflow_id: str) -> None:
        try:
            record = self._require_workflow(workflow_id)
            if record.approved_story is None:
                raise ValueError(f"Workflow '{workflow_id}' has no approved story")

            story_text = self._render_story_text(record.approved_story)
            context = RequestContext(correlation_id=record.correlation_id)
            bdd_response = await self._registry.bdd.send(QARequest(story=story_text), context=context)

            record = self._require_workflow(workflow_id)
            record.bdd_response = bdd_response
            record.stage = "bdd_done"
            record.updated_at = datetime.now(timezone.utc)
        except Exception:
            record = self._workflows.get(workflow_id)
            if record is not None:
                record.stage = "failed"
                record.updated_at = datetime.now(timezone.utc)
            self._logger.exception("bdd_analysis_failed", extra={"workflow_id": workflow_id})
        finally:
            self._approval_tasks.pop(workflow_id, None)

    def get_bdd_results(self, workflow_id: str) -> dict[str, Any]:
        record = self._require_workflow(workflow_id)
        if record.bdd_response is None:
            raise KeyError("BDD results not available yet")
        return {"bdd_analysis": record.bdd_response}

    def _require_workflow(self, workflow_id: str) -> WorkflowRecord:
        record = self._workflows.get(workflow_id)
        if record is None:
            raise KeyError(f"Workflow '{workflow_id}' not found")
        return record

    @staticmethod
    def _render_story_text(story: UserStoryInput) -> str:
        lines = [f"Title: {story.title}", "", story.description.strip(), "", "Acceptance criteria:"]
        lines.extend(f"- {item}" for item in story.acceptance_criteria)
        if story.additional_context:
            lines.extend(["", "Additional context:", story.additional_context.strip()])
        return "\n".join(lines).strip()

    @staticmethod
    def _build_compliance_request(invest_response: InvestAgentResponse) -> ComplianceAnalysisRequest:
        analysis = invest_response.result.step_1_invest_analysis

        criteria_results = [
            InvestCriterionResult(
                criterion_id=name,
                criterion_name=name,
                result=criterion.status == "pass",
                evidence=(criterion.evidence[0] if criterion.evidence else None),
            )
            for name, criterion in analysis.as_criteria_dict().items()
        ]

        classification = invest_response.result.step_2_classification.category
        status = "approved" if classification == "boa" else "rejected"

        return ComplianceAnalysisRequest(
            investment_id=invest_response.execution_id,
            invest_result=InvestResult(
                investment_id=invest_response.execution_id,
                status=status,
                criteria_results=criteria_results,
                summary=f"INVEST classification: {classification}",
                metadata={
                    "schema_version": invest_response.schema_version,
                    "rule_applied": invest_response.result.step_2_classification.rule_applied,
                },
            ),
        )
