"""
Rotas de análise de compliance.
"""

import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.graph import run_compliance_graph
from app.schemas.models import (
    ComplianceAnalysisRequest,
    ComplianceAnalysisResponse,
    InvestCriterionResult,
    InvestResult,
)
from app.services.file_loader import FileLoader
from app.services.persistence_service import PersistenceService

router = APIRouter(prefix="/api/v1/compliance", tags=["compliance"])


def _persist_analysis_safely(response: ComplianceAnalysisResponse, request: ComplianceAnalysisRequest) -> None:
    try:
        PersistenceService.save_analysis(response=response, request=request)
    except Exception as exc:
        print(f"[WARN] Não foi possível persistir análise: {exc}")


class AnalyzeFileRequest(BaseModel):
    """Payload para análise a partir de arquivo JSON local."""

    file_path: str


@router.post("/analyze", response_model=ComplianceAnalysisResponse)
async def analyze_compliance(
    request: ComplianceAnalysisRequest,
) -> ComplianceAnalysisResponse:
    """
    Executa análise de compliance via JSON direto.
    """
    try:
        response = run_compliance_graph(request)
        _persist_analysis_safely(response=response, request=request)
        return response
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {exc}")


@router.post("/analyze-file", response_model=ComplianceAnalysisResponse)
async def analyze_compliance_file(
    request: AnalyzeFileRequest,
) -> ComplianceAnalysisResponse:
    """
    Executa análise de compliance lendo um arquivo JSON local.

    Aceita dois formatos:
    1. compliance_request_sample.json:
       {
         "investment_id": "...",
         "invest_result": {...}
       }

    2. invest_result_sample.json:
       {
         "investment_id": "...",
         "status": "...",
         "criteria_results": [...],
         "summary": "...",
         "metadata": {...}
       }
    """
    try:
        data = FileLoader.load_json(request.file_path)

        if data is None:
            raise ValueError("Arquivo JSON vazio.")

        if "invest_result" in data:
            analysis_request = ComplianceAnalysisRequest(**data)
        else:
            criteria = [
                InvestCriterionResult(**criterion)
                for criterion in data.get("criteria_results", [])
            ]

            invest_result = InvestResult(
                investment_id=data.get("investment_id", ""),
                status=data.get("status", "unknown"),
                criteria_results=criteria,
                summary=data.get("summary", ""),
                metadata=data.get("metadata", {}),
            )

            analysis_request = ComplianceAnalysisRequest(
                investment_id=invest_result.investment_id,
                invest_result=invest_result,
            )

        response = run_compliance_graph(analysis_request)
        _persist_analysis_safely(response=response, request=analysis_request)

        return response

    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"JSON inválido: {exc}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro na análise por arquivo: {exc}")