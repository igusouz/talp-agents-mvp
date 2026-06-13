from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.exceptions import AgentClientError, AgentUpstreamHttpError
from app.schemas.workflow import (
    ApprovedStoryRequest,
    WorkflowCreateRequest,
    WorkflowCreateResponse,
    WorkflowStateResponse,
)
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["workflows"])


def get_workflow_service(request: Request) -> WorkflowService:
    return request.app.state.workflow_service


@router.post("", response_model=WorkflowCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    payload: WorkflowCreateRequest,
    service: WorkflowService = Depends(get_workflow_service),
) -> WorkflowCreateResponse:
    try:
        return await service.start_workflow(payload)
    except AgentUpstreamHttpError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except AgentClientError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/{workflow_id}", response_model=WorkflowStateResponse)
def get_workflow_state(
    workflow_id: str,
    service: WorkflowService = Depends(get_workflow_service),
) -> WorkflowStateResponse:
    try:
        return service.get_workflow_state(workflow_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/{workflow_id}/approval",
    response_model=WorkflowStateResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_approval(
    workflow_id: str,
    payload: ApprovedStoryRequest,
    service: WorkflowService = Depends(get_workflow_service),
) -> WorkflowStateResponse:
    try:
        return await service.submit_approval(workflow_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{workflow_id}/bdd-results")
def get_bdd_results(
    workflow_id: str,
    service: WorkflowService = Depends(get_workflow_service),
) -> dict:
    try:
        return service.get_bdd_results(workflow_id)
    except KeyError as exc:
        message = str(exc)
        if "not available" in message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message) from exc
