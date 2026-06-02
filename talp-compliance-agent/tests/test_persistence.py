"""
Testes de persistência e banco de dados
"""
import os
import pytest
from sqlalchemy import inspect
from app.db.init_db import init_db
from app.db.base import engine
from app.services.catalog_repository import CatalogRepository
from app.services.persistence_service import PersistenceService
from app.schemas.models import (
    ComplianceAnalysisRequest,
    InvestCriterionResult,
    InvestResult,
)
from app.graph import run_compliance_graph

DB_PATH = "./storage/db/compliance_agent.db"


def test_init_db_creates_tables():
    """Testa se python -m app.db.init_db cria as tabelas."""
    # Remove DB se existir
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    insp = inspect(engine)
    tables = insp.get_table_names()
    assert "analysis_runs" in tables
    assert "rule_catalog_entries" in tables


def test_catalog_sync_saves_rules():
    """Testa se o sync do catálogo salva 8 regras no banco."""
    repo = CatalogRepository()
    count = repo.sync_csv_to_db()
    assert count == 8
    rules = PersistenceService.list_rules()
    assert len(rules) == 8


def test_analysis_run_is_persisted():
    """Testa se uma execução de análise é persistida."""
    invest_result = InvestResult(
        investment_id="INV-2026-PERSIST",
        status="warning",
        criteria_results=[
            InvestCriterionResult(
                criterion_id="EST-001",
                criterion_name="Estimable",
                result=True,
                evidence="Dados financeiros disponíveis",
            ),
            InvestCriterionResult(
                criterion_id="TEST-001",
                criterion_name="Testable",
                result=True,
                evidence="Histórico de performance",
            ),
        ],
        summary="Paciente com antibiótico antimicrobiano detectado",
    )
    request = ComplianceAnalysisRequest(
        investment_id="INV-2026-PERSIST",
        invest_result=invest_result,
    )
    response = run_compliance_graph(request)
    # Buscar no banco
    run = PersistenceService.get_analysis_run(response.analysis_id)
    assert run is not None
    assert run.run_id == response.analysis_id
    assert "antibiótico" in run.user_story or "antibiotico" in run.user_story
