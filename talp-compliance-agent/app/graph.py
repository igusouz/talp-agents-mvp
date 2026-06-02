"""
Grafo do LangGraph - Fluxo de Análise de Compliance
"""

import uuid
from datetime import datetime

from app.schemas.models import (
    ComplianceAnalysisRequest,
    ComplianceAnalysisResponse,
    ComplianceGap,
    ComplianceRequirement,
    DetectedRule,
)
from app.services.catalog_repository import CatalogRepository
from app.services.dependency_analyzer import DependencyAnalyzer
from app.services.gap_analyzer import GapAnalyzer
from app.services.invest_result_adapter import InvestResultAdapter
from app.services.persistence_service import PersistenceService
from app.services.rule_matcher import RuleMatcher


def validate_request(request: ComplianceAnalysisRequest) -> None:
    """
    Validar requisição de análise de compliance.

    Args:
        request: Requisição a validar

    Raises:
        ValueError: Se a requisição for inválida
    """
    if not request.investment_id or not isinstance(request.investment_id, str):
        raise ValueError("investment_id é obrigatório e deve ser uma string")

    if request.invest_result is None:
        raise ValueError("invest_result é obrigatório")


def determine_compliance_status(
    detected_rules: list[DetectedRule], compliance_gaps: list[ComplianceGap]
) -> str:
    """
    Determinar status geral de conformidade.

    Args:
        detected_rules: Regras detectadas
        compliance_gaps: Lacunas de conformidade

    Returns:
        Status: "compliant", "non_compliant" ou "partial"
    """
    # Se não há lacunas críticas, é compliant
    critical_gaps = [g for g in compliance_gaps if g.severity == "critical"]
    if not critical_gaps and compliance_gaps:
        return "partial"
    elif not compliance_gaps:
        return "compliant"
    else:
        return "non_compliant"


def can_continue_to_bdd(
    invest_context, detected_rules: list, compliance_gaps: list
) -> bool:
    """
    Determinar se pode continuar para BDD (Behavior-Driven Development).

    Deve ser false quando:
    - invest_result.overall_status = rejected
    - critério testable está failed
    - há dependência obrigatória não satisfeita
    - há lacuna crítica relacionada a regra bloqueante

    Args:
        invest_context: Contexto do investimento adaptado
        detected_rules: Regras detectadas
        compliance_gaps: Lacunas de conformidade

    Returns:
        True se pode continuar, False caso contrário
    """
    # Condição 1: overall_status = rejected
    if invest_context.overall_status == "rejected":
        return False

    # Condição 2: critério testable está failed
    if "Testable" in invest_context.failed:
        return False

    # Condição 3: há lacuna crítica relacionada a regra bloqueante
    critical_blocking_gaps = [
        g for g in compliance_gaps if g.severity == "critical" and g.blocking
    ]
    if critical_blocking_gaps:
        return False

    return True


def run_compliance_graph(request: ComplianceAnalysisRequest) -> ComplianceAnalysisResponse:
    """
    Função principal de análise de compliance.

    Orquestra o fluxo de análise sequencial:
    1. Validar input
    2. Adaptar invest_result
    3. Carregar catálogo
    4. Rodar rule_matcher
    5. Criar mandatory_rules
    6. Criar blocking_rules
    7. Criar compliance_requirements
    8. Criar dependências
    9. Criar lacunas
    10. Validar que nenhuma regra fora do catálogo aparece
    11. Gerar run_id UUID
    12. Retornar ComplianceAnalysisResponse

    Args:
        request: Requisição de análise de compliance

    Returns:
        ComplianceAnalysisResponse com resultados da análise
    """
    # 1. Validar input
    validate_request(request)

    # 2. Adaptar invest_result
    invest_context = InvestResultAdapter.adapt(
        request.investment_id, request.invest_result
    )

    # 3. Carregar catálogo
    catalog_repo = CatalogRepository()
    catalog_rules = catalog_repo.load_rules()

    # 4. Rodar rule_matcher
    # Para isso, precisamos do texto/descrição do investimento
    # Vamos usar invest_result.summary como base
    investment_text = request.invest_result.summary or ""
    for criterion in request.invest_result.criteria_results:
        investment_text += f" {criterion.criterion_name}"
        if criterion.evidence:
            investment_text += f": {criterion.evidence}"

    rule_matcher = RuleMatcher()
    matched_rules_objects = rule_matcher.match_rules(investment_text)

    # Converter para dict para facilitar o processamento
    matched_rules_dict = [
        {
            "rule_id": rule.rule_id,
            "name": rule.name,
            "domain": rule.domain,
            "matched": rule.matched,
            "confidence": rule.confidence,
            "evidence_found": rule.evidence_found,
            "mandatory": False,
            "blocking": False,
        }
        for rule in matched_rules_objects
    ]

    # Enriquecer informações das regras (mandatory, blocking) a partir do catálogo
    for matched_rule in matched_rules_dict:
        catalog_rule = catalog_repo.get_rule(matched_rule["rule_id"])
        if catalog_rule:
            matched_rule["mandatory"] = catalog_rule.mandatory
            matched_rule["blocking"] = catalog_rule.blocking

    # 5. Criar mandatory_rules
    mandatory_rules = [r for r in matched_rules_dict if r.get("mandatory", False)]

    # 6. Criar blocking_rules
    blocking_rules = [r for r in matched_rules_dict if r.get("blocking", False)]

    # 8. Analisar dependências
    dependency_analyzer = DependencyAnalyzer()
    dependency_analysis = dependency_analyzer.analyze(matched_rules_dict)

    # Extrair lacunas de dependência (já no formato ComplianceGap)
    dependency_gaps = dependency_analysis.get("dependency_gaps", [])

    # 9. Analisar lacunas
    gap_analyzer = GapAnalyzer()
    all_gaps = gap_analyzer.analyze(matched_rules_dict, catalog_rules, dependency_gaps)

    # 10. Validar que nenhuma regra fora do catálogo aparece
    catalog_rule_ids = set(rule.rule_id for rule in catalog_rules)
    detected_rule_ids = set(r["rule_id"] for r in matched_rules_dict)

    invalid_rules = detected_rule_ids - catalog_rule_ids
    if invalid_rules:
        raise ValueError(f"Regras detectadas fora do catálogo: {invalid_rules}")

    # Converter lacunas para ComplianceGap se necessário
    gaps_as_objects = []
    for gap in all_gaps:
        if isinstance(gap, dict):
            gaps_as_objects.append(ComplianceGap(**gap))
        else:
            gaps_as_objects.append(gap)

    # 7. Criar compliance_requirements
    compliance_requirements = []
    for rule in matched_rules_dict:
        req_status = "satisfied"
        if any(gap.rule_id == rule["rule_id"] for gap in gaps_as_objects):
            req_status = "gap"

        requirement = ComplianceRequirement(
            requirement_id=f"REQ-{rule['rule_id']}",
            description=rule["name"],
            status=req_status,
            rules_involved=[rule["rule_id"]],
        )
        compliance_requirements.append(requirement)

    # Converter regras detectadas para DetectedRule
    detected_rules = []
    for rule in matched_rules_dict:
        detected_rules.append(
            DetectedRule(
                rule_id=rule["rule_id"],
                name=rule["name"],
                domain=rule["domain"],
                matched=rule["matched"],
                confidence=rule["confidence"],
                evidence_found=rule["evidence_found"],
            )
        )

    # Determinar status geral
    compliance_status = determine_compliance_status(detected_rules, gaps_as_objects)

    # Determinar se pode continuar para BDD
    can_continue = can_continue_to_bdd(invest_context, detected_rules, gaps_as_objects)

    # 11. Gerar run_id UUID
    analysis_id = f"COMP-{uuid.uuid4().hex[:8].upper()}"

    # Gerar resumo
    summary = f"Análise de conformidade do investimento {request.investment_id}. "
    summary += f"Regras detectadas: {len(detected_rules)}. "
    summary += f"Lacunas identificadas: {len(gaps_as_objects)}. "
    summary += f"Status: {compliance_status}. "
    summary += f"Pode continuar para BDD: {can_continue}."

    # 12. Retornar ComplianceAnalysisResponse
    response = ComplianceAnalysisResponse(
        analysis_id=analysis_id,
        investment_id=request.investment_id,
        status=compliance_status,
        detected_rules=detected_rules,
        compliance_gaps=gaps_as_objects,
        requirements=compliance_requirements,
        summary=summary,
        timestamp=datetime.now(),
        metadata={
            "invest_context": {
                "overall_status": invest_context.overall_status,
                "score": invest_context.score,
                "warnings": invest_context.warnings,
                "failed": invest_context.failed,
            },
            "can_continue_to_bdd": can_continue,
            "mandatory_rules": [r["rule_id"] for r in mandatory_rules],
            "blocking_rules": [r["rule_id"] for r in blocking_rules],
        },
    )

    # --- Persistência da execução ---
    try:
        import json as _json

        invest_result_json = _json.dumps(request.invest_result.model_dump())
        PersistenceService.save_analysis(
            response=response,
            user_story=investment_text,
            invest_result_json=invest_result_json,
            can_continue_to_bdd=can_continue,
        )
    except Exception as e:
        print(f"[WARN] Não foi possível persistir análise: {e}")

    return response


def create_graph():
    """Criar grafo de agente."""
    # Implementação futura com LangGraph
    pass
