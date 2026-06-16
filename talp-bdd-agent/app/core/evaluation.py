"""Helpers for lightweight semantic evaluation of QA responses."""

from __future__ import annotations

from collections.abc import Iterable

from app.schemas.qa import QAAnalysisResponse, QualityChecks, TraceableItem


def build_response_corpus(response: QAAnalysisResponse) -> str:
    """Flatten a structured response into searchable text for semantic checks."""

    parts: list[str] = [response.summary]

    for scenario in response.bdd_scenarios:
        parts.extend(
            [
                scenario.title,
                scenario.scenario_type,
                scenario.gherkin,
                *scenario.given,
                *scenario.when,
                *scenario.then,
                *scenario.notes,
            ]
        )

    parts.extend(
        [
            *response.negative_cases,
            *response.edge_cases,
            *response.ambiguities,
            *response.risks,
            *response.automation_suggestions,
            *response.questions_for_refinement,
        ]
    )

    return "\n".join(item.strip() for item in parts if item and item.strip())


def contains_all_terms(corpus: str, terms: Iterable[str]) -> bool:
    """Return True when every term exists in the corpus (case-insensitive)."""

    normalized_corpus = corpus.lower()
    return all(term.lower() in normalized_corpus for term in terms)


def _text_is_anchored(story: str, evidence: str | None) -> bool:
    """Return True when the evidence snippet appears in the user story."""

    if not evidence:
        return False
    return evidence.strip().lower() in story.lower()


def _parse_ac_ids(ac_map: list[str]) -> set[str]:
    """Extract AC identifiers from map entries like 'AC1: ...'."""

    ids: set[str] = set()
    for item in ac_map:
        token = item.split(":", maxsplit=1)[0].strip().upper()
        if token.startswith("AC"):
            ids.add(token)
    return ids


def _refinement_alignment(
    ambiguities_trace: list[TraceableItem],
    questions_trace: list[TraceableItem],
) -> float:
    """Compute ratio of questions linked to known ambiguities."""

    if not questions_trace:
        return 0.0
    known_ambiguity_ids = {item.ambiguity_id for item in ambiguities_trace if item.ambiguity_id}
    linked = sum(1 for item in questions_trace if item.ambiguity_id and item.ambiguity_id in known_ambiguity_ids)
    return linked / len(questions_trace)


def _automation_trace(automation_trace: list[TraceableItem]) -> float:
    """Compute ratio of automation suggestions linked to scenario and AC."""

    if not automation_trace:
        return 0.0
    linked = sum(1 for item in automation_trace if item.scenario_id and item.ac_ids)
    return linked / len(automation_trace)


def build_quality_checks(response: QAAnalysisResponse, story: str) -> QualityChecks:
    """Build BDD quality checks for anti-hallucination and discrimination analysis."""

    total_items = 0
    supported_items = 0

    for scenario in response.bdd_scenarios:
        total_items += 1
        if _text_is_anchored(story, scenario.evidence_us):
            supported_items += 1

    trace_groups = [
        response.negative_cases_trace,
        response.edge_cases_trace,
        response.ambiguities_trace,
        response.risks_trace,
        response.automation_suggestions_trace,
        response.questions_for_refinement_trace,
    ]

    for group in trace_groups:
        for item in group:
            total_items += 1
            if _text_is_anchored(story, item.evidence_us):
                supported_items += 1

    traceability_ratio = (supported_items / total_items) if total_items else 0.0
    unsupported_rate = 1.0 - traceability_ratio if total_items else 0.0

    ac_ids = _parse_ac_ids(response.ac_map)
    covered_ac_ids: set[str] = set()
    for scenario in response.bdd_scenarios:
        covered_ac_ids.update(ac_id.upper() for ac_id in scenario.ac_ids)
    ac_coverage = (len(covered_ac_ids & ac_ids) / len(ac_ids)) if ac_ids else 0.0

    refinement_alignment = _refinement_alignment(
        response.ambiguities_trace,
        response.questions_for_refinement_trace,
    )
    automation_trace = _automation_trace(response.automation_suggestions_trace)

    observations: list[str] = []
    if unsupported_rate > 0.0:
        observations.append("Items sem evidencia literal da User Story foram detectados.")
    if ac_ids and ac_coverage < 1.0:
        observations.append("Nem todos os criterios de aceitacao mapeados possuem cenario associado.")
    if response.questions_for_refinement_trace and refinement_alignment < 1.0:
        observations.append("Ha perguntas de refinamento nao vinculadas a ambiguidades identificadas.")
    if response.automation_suggestions_trace and automation_trace < 1.0:
        observations.append("Ha sugestoes de automacao sem vinculo completo com cenario e AC.")

    return QualityChecks(
        traceability_ratio=round(traceability_ratio, 4),
        unsupported_rate=round(unsupported_rate, 4),
        ac_coverage=round(ac_coverage, 4),
        refinement_alignment=round(refinement_alignment, 4),
        automation_trace=round(automation_trace, 4),
        observations=observations,
    )
