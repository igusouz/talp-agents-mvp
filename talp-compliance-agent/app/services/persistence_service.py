"""
Serviço de persistência em banco SQLite.
"""

import json
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import AnalysisRun, RuleCatalogEntry
from app.db.session import get_session
from app.schemas.models import ComplianceAnalysisRequest, ComplianceAnalysisResponse


class PersistenceService:
    """Serviço para persistir execuções e catálogo."""

    @staticmethod
    def save_analysis(
        response: ComplianceAnalysisResponse,
        request: ComplianceAnalysisRequest,
        session: Optional[Session] = None,
    ) -> AnalysisRun:
        """
        Salva uma execução de análise no banco.
        """
        should_close = False

        if session is None:
            session = get_session()
            should_close = True

        try:
            user_story = request.invest_result.summary or ""

            analysis_run = AnalysisRun(
                run_id=response.analysis_id,
                user_story=user_story,
                invest_result_json=request.invest_result.model_dump_json(),
                compliance_result_json=response.model_dump_json(),
                can_continue_to_bdd=response.metadata.get("can_continue_to_bdd", False),
            )

            session.add(analysis_run)
            session.commit()
            session.refresh(analysis_run)

            return analysis_run
        finally:
            if should_close:
                session.close()

    @staticmethod
    def get_analysis_run(
        run_id: str,
        session: Optional[Session] = None,
    ) -> Optional[AnalysisRun]:
        """Busca uma execução pelo run_id."""
        should_close = False

        if session is None:
            session = get_session()
            should_close = True

        try:
            return (
                session.query(AnalysisRun)
                .filter(AnalysisRun.run_id == run_id)
                .first()
            )
        finally:
            if should_close:
                session.close()

    @staticmethod
    def list_analysis_runs(
        limit: int = 100,
        offset: int = 0,
        session: Optional[Session] = None,
    ) -> list[AnalysisRun]:
        """Lista execuções salvas."""
        should_close = False

        if session is None:
            session = get_session()
            should_close = True

        try:
            return (
                session.query(AnalysisRun)
                .order_by(AnalysisRun.created_at.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )
        finally:
            if should_close:
                session.close()

    @staticmethod
    def save_rule_catalog(
        rules: list[dict],
        session: Optional[Session] = None,
    ) -> int:
        """
        Sincroniza regras no banco.

        Se a regra já existir, atualiza.
        Se não existir, cria.
        Retorna a quantidade total de regras processadas.
        """
        should_close = False

        if session is None:
            session = get_session()
            should_close = True

        try:
            count = 0

            for rule in rules:
                keywords = rule.get("keywords", [])

                if isinstance(keywords, list):
                    keywords_value = json.dumps(keywords, ensure_ascii=False)
                else:
                    keywords_value = str(keywords)

                existing = (
                    session.query(RuleCatalogEntry)
                    .filter(RuleCatalogEntry.rule_id == rule["rule_id"])
                    .first()
                )

                if existing:
                    existing.name = rule["name"]
                    existing.domain = rule["domain"]
                    existing.description = rule["description"]
                    existing.mandatory = rule["mandatory"]
                    existing.blocking = rule["blocking"]
                    existing.keywords = keywords_value
                    existing.evidence = rule["evidence"]
                else:
                    entry = RuleCatalogEntry(
                        rule_id=rule["rule_id"],
                        name=rule["name"],
                        domain=rule["domain"],
                        description=rule["description"],
                        mandatory=rule["mandatory"],
                        blocking=rule["blocking"],
                        keywords=keywords_value,
                        evidence=rule["evidence"],
                    )
                    session.add(entry)

                count += 1

            session.commit()
            return count
        finally:
            if should_close:
                session.close()

    @staticmethod
    def list_rules(session: Optional[Session] = None) -> list[RuleCatalogEntry]:
        """Lista regras persistidas no banco."""
        should_close = False

        if session is None:
            session = get_session()
            should_close = True

        try:
            return (
                session.query(RuleCatalogEntry)
                .order_by(RuleCatalogEntry.rule_id.asc())
                .all()
            )
        finally:
            if should_close:
                session.close()