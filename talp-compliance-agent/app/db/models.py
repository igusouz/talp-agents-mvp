"""
Modelos do banco de dados
"""

from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean
from sqlalchemy.sql import func

from app.db.base import Base


class ComplianceAnalysis(Base):
    """Modelo para análise de conformidade."""

    __tablename__ = "compliance_analysis"

    id = Column(Integer, primary_key=True, index=True)
    investment_id = Column(String, index=True)
    status = Column(String, default="pending")
    result = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AuditLog(Base):
    """Modelo para log de auditoria."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String)
    analysis_id = Column(Integer)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AnalysisRun(Base):
    """Modelo para execução de análise de conformidade."""

    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True)
    user_story = Column(Text)
    invest_result_json = Column(Text)
    compliance_result_json = Column(Text)
    can_continue_to_bdd = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RuleCatalogEntry(Base):
    """Modelo para entradas do catálogo de regras."""

    __tablename__ = "rule_catalog_entries"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String, unique=True, index=True)
    name = Column(String)
    domain = Column(String, index=True)
    description = Column(Text)
    mandatory = Column(Boolean, default=False)
    blocking = Column(Boolean, default=False)
    keywords = Column(Text)  # JSON string
    evidence = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
