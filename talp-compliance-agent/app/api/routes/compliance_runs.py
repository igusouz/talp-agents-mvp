"""
Rotas para consulta de execuções de compliance salvas.
"""

import json

from fastapi import APIRouter, HTTPException

from app.services.persistence_service import PersistenceService

router = APIRouter(prefix="/api/v1/compliance", tags=["compliance-runs"])


@router.get("/runs")
async def list_analysis_runs(limit: int = 100, offset: int = 0):
    """Lista execuções de análise salvas no banco."""
    runs = PersistenceService.list_analysis_runs(limit=limit, offset=offset)

    return [
        {
            "run_id": run.run_id,
            "created_at": run.created_at,
            "can_continue_to_bdd": run.can_continue_to_bdd,
            "user_story": run.user_story,
        }
        for run in runs
    ]


@router.get("/runs/{run_id}")
async def get_analysis_run(run_id: str):
    """Busca uma execução específica pelo run_id."""
    run = PersistenceService.get_analysis_run(run_id)

    if not run:
        raise HTTPException(status_code=404, detail="Execução não encontrada.")

    try:
        return {
            "run_id": run.run_id,
            "created_at": run.created_at,
            "can_continue_to_bdd": run.can_continue_to_bdd,
            "user_story": run.user_story,
            "invest_result": json.loads(run.invest_result_json),
            "compliance_result": json.loads(run.compliance_result_json),
        }
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao ler JSON salvo no banco: {exc}",
        )