from app.nodes.classification import classification_node
from app.schemas.models import CriterionAssessment, InvestAnalysis


def test_classification_good_when_all_criteria_pass():
    state = {
        "invest_analysis": InvestAnalysis(
            independent=CriterionAssessment(status="pass", evidence=["x"], reason="ok"),
            negotiable=CriterionAssessment(status="pass", evidence=["x"], reason="ok"),
            valuable=CriterionAssessment(status="pass", evidence=["x"], reason="ok"),
            estimable=CriterionAssessment(status="pass", evidence=["x"], reason="ok"),
            small=CriterionAssessment(status="pass", evidence=["x"], reason="ok"),
            testable=CriterionAssessment(status="pass", evidence=["x"], reason="ok"),
        )
    }

    result = classification_node(state)

    assert result["classification"].category == "boa"
    assert result["classification"].failed_criteria == []


def test_classification_bad_when_any_criterion_fails():
    state = {
        "invest_analysis": InvestAnalysis(
            independent=CriterionAssessment(status="pass", evidence=["x"], reason="ok"),
            negotiable=CriterionAssessment(status="fail", evidence=[], reason="missing"),
            valuable=CriterionAssessment(status="pass", evidence=["x"], reason="ok"),
            estimable=CriterionAssessment(status="pass", evidence=["x"], reason="ok"),
            small=CriterionAssessment(status="pass", evidence=["x"], reason="ok"),
            testable=CriterionAssessment(status="pass", evidence=["x"], reason="ok"),
        )
    }

    result = classification_node(state)

    assert result["classification"].category == "ruim"
    assert result["classification"].failed_criteria == ["negotiable"]

