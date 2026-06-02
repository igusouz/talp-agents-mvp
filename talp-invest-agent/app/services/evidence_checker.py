from __future__ import annotations

import re

from app.schemas.models import BadStoryReport, CRITERIA, InvestAnalysis


FORBIDDEN_REPORT_PATTERNS = (
    r"\brecomend",
    r"\bsuger",
    r"\bmelhor",
    r"\breescre",
    r"\bvers",
    r"\bdeve(ria)? incluir",
    r"\bpoderia incluir",
)


def literal_evidence_errors(user_story_text: str, evidence: list[str]) -> list[str]:
    errors: list[str] = []
    for item in evidence:
        if item not in user_story_text:
            errors.append(item)
    return errors


def enforce_analysis_guardrails(
    user_story_text: str,
    analysis: InvestAnalysis,
) -> tuple[InvestAnalysis, list[str]]:
    errors: list[str] = []
    data = analysis.model_dump()
    for criterion in CRITERIA:
        item = data[criterion]
        invalid = literal_evidence_errors(user_story_text, item["evidence"])
        if invalid:
            errors.append(f"{criterion}: evidence is not literal: {invalid}")
            item["evidence"] = [
                evidence for evidence in item["evidence"] if evidence in user_story_text
            ]
        if item["status"] == "pass" and not item["evidence"]:
            errors.append(f"{criterion}: pass without literal evidence")
            item["status"] = "fail"
            item["reason"] = (
                "The criterion was marked as fail because no literal evidence "
                "from the user story supported a pass decision."
            )
    return InvestAnalysis.model_validate(data), errors


def report_has_forbidden_content(report: BadStoryReport) -> bool:
    text = report.model_dump_json().lower()
    return any(re.search(pattern, text) for pattern in FORBIDDEN_REPORT_PATTERNS)


def validate_report_guardrails(
    user_story_text: str,
    failed_criteria: list[str],
    report: BadStoryReport,
) -> list[str]:
    errors: list[str] = []
    failed = set(failed_criteria)
    for problem in report.problems:
        if problem.criterion not in failed:
            errors.append(f"{problem.criterion}: report includes non-failed criterion")
        invalid = literal_evidence_errors(user_story_text, problem.evidence)
        if invalid:
            errors.append(f"{problem.criterion}: report evidence is not literal: {invalid}")
    if report_has_forbidden_content(report):
        errors.append("report contains recommendation or rewrite language")
    return errors
