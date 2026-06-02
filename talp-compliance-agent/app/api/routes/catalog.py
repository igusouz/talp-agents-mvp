"""
Rotas do catálogo de regras.
"""

from fastapi import APIRouter, HTTPException

from app.services.catalog_repository import CatalogRepository
from app.services.persistence_service import PersistenceService

router = APIRouter(prefix="/api/v1/catalog", tags=["catalog"])


def rule_to_dict(rule) -> dict:
    """Converte uma regra do banco ou Pydantic para dict."""
    keywords = rule.keywords

    return {
        "rule_id": rule.rule_id,
        "name": rule.name,
        "domain": rule.domain,
        "description": rule.description,
        "mandatory": rule.mandatory,
        "blocking": rule.blocking,
        "keywords": keywords,
        "evidence": rule.evidence,
    }


@router.get("/rules")
async def get_rules():
    """
    Lista as regras do catálogo.

    Primeiro tenta ler do banco.
    Se o banco estiver vazio, lê do CSV local.
    """
    db_rules = PersistenceService.list_rules()

    if db_rules:
        return [
            {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "domain": rule.domain,
                "description": rule.description,
                "mandatory": rule.mandatory,
                "blocking": rule.blocking,
                "keywords": rule.keywords,
                "evidence": rule.evidence,
            }
            for rule in db_rules
        ]

    try:
        csv_rules = CatalogRepository().load_rules()
        return [rule.model_dump() for rule in csv_rules]
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao carregar catálogo: {exc}",
        )


@router.post("/sync")
async def sync_catalog():
    """
    Sincroniza o arquivo data/catalog_rules_v1.csv com o banco SQLite.
    """
    try:
        count = CatalogRepository().sync_csv_to_db()
        return {
            "status": "ok",
            "synced_rules": count,
            "message": f"{count} regra(s) sincronizada(s).",
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao sincronizar catálogo: {exc}",
        )