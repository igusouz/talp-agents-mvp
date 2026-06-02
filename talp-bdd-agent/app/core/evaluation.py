"""Helpers for lightweight semantic evaluation of QA responses."""

from __future__ import annotations

from collections.abc import Iterable

from app.schemas.qa import QAAnalysisResponse


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
