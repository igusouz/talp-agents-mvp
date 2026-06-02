"""Lightweight semantic evaluations for QA response quality."""

from __future__ import annotations

import json
from pathlib import Path

from app.core.evaluation import build_response_corpus, contains_all_terms


def _load_eval_cases() -> list[dict[str, object]]:
    """Load semantic eval cases from the JSON fixture file."""

    cases_path = Path(__file__).with_name("qa_cases.json")
    return json.loads(cases_path.read_text(encoding="utf-8"))


def test_semantic_eval_cases(mock_qa_response) -> None:
    """Validate semantic coverage and regression-prone terms."""

    corpus = build_response_corpus(mock_qa_response)
    cases = _load_eval_cases()

    for case in cases:
        expected_contains = case.get("expected_contains", [])
        assert isinstance(expected_contains, list)
        assert contains_all_terms(corpus, expected_contains)

        min_counts = case.get("min_counts", {})
        assert isinstance(min_counts, dict)
        for field_name, minimum in min_counts.items():
            value = getattr(mock_qa_response, field_name)
            assert len(value) >= int(minimum)
