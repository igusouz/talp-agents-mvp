from app.schemas.models import CriterionAssessment, InvestAnalysis
from app.services.evidence_checker import enforce_analysis_guardrails


def test_guardrail_removes_non_literal_evidence_and_fails_unsupported_pass():
    story = "Como cliente, quero redefinir minha senha para recuperar acesso."
    analysis = InvestAnalysis(
        independent=CriterionAssessment(status="pass", evidence=["texto inexistente"], reason="ok"),
        negotiable=CriterionAssessment(status="pass", evidence=["quero redefinir minha senha"], reason="ok"),
        valuable=CriterionAssessment(status="pass", evidence=["para recuperar acesso"], reason="ok"),
        estimable=CriterionAssessment(status="pass", evidence=["redefinir minha senha"], reason="ok"),
        small=CriterionAssessment(status="pass", evidence=["redefinir minha senha"], reason="ok"),
        testable=CriterionAssessment(status="pass", evidence=["recuperar acesso"], reason="ok"),
    )

    guarded, errors = enforce_analysis_guardrails(story, analysis)

    assert guarded.independent.status == "fail"
    assert guarded.independent.evidence == []
    assert errors

