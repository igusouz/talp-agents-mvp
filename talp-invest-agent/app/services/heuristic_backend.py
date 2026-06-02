from __future__ import annotations

from app.schemas.models import BadStoryReport, CriterionAssessment, InvestAnalysis, ReportProblem
from app.services.prompt_registry import PromptTemplate


class HeuristicInvestAnalyzer:
    """Deterministic backend for local tests and offline development."""

    model_name = "heuristic-v1"

    def analyze(self, user_story_text: str, prompt: PromptTemplate) -> InvestAnalysis:
        lower = user_story_text.lower()
        has_role = any(token in lower for token in ("como ", "as a "))
        has_need = any(token in lower for token in ("quero", "preciso", "i want", "i need"))
        has_value = any(token in lower for token in (" para ", " so that ", "a fim de"))
        broad_terms = ("melhorar", "otimizar", "sistema", "tudo", "gerenciar")
        multiple = any(token in lower for token in (" e ", ";", "tambem"))
        external = any(token in lower for token in ("conforme", "segundo", "ticket", "epico", "documento"))
        technical = any(token in lower for token in ("api", "sql", "redis", "kafka", "tabela", "endpoint"))

        def ev(*needles: str) -> list[str]:
            found = []
            for needle in needles:
                index = lower.find(needle)
                if index >= 0:
                    found.append(user_story_text[index : index + len(needle)])
            return found

        return InvestAnalysis(
            independent=CriterionAssessment(
                status="fail" if external else "pass",
                evidence=ev("conforme", "ticket", "documento") if external else [user_story_text],
                reason="The story is evaluated only from explicit dependency language.",
            ),
            negotiable=CriterionAssessment(
                status="fail" if technical and not has_need else "pass",
                evidence=ev("api", "sql", "redis", "kafka", "tabela", "endpoint") if technical else [user_story_text],
                reason="The story is checked for closed technical specification.",
            ),
            valuable=CriterionAssessment(
                status="pass" if has_value or (has_role and has_need) else "fail",
                evidence=ev(" para ", " so that ", "a fim de") or ([user_story_text] if has_role and has_need else []),
                reason="The story must explicitly show value, benefit, objective, or beneficiary.",
            ),
            estimable=CriterionAssessment(
                status="fail" if any(term in lower for term in broad_terms) else "pass",
                evidence=ev(*broad_terms) if any(term in lower for term in broad_terms) else [user_story_text],
                reason="The story is checked for initial scope clarity.",
            ),
            small=CriterionAssessment(
                status="fail" if multiple or any(term in lower for term in broad_terms) else "pass",
                evidence=ev(" e ", ";", "tambem", *broad_terms)
                if multiple or any(term in lower for term in broad_terms)
                else [user_story_text],
                reason="The story is checked for one small unit of delivery.",
            ),
            testable=CriterionAssessment(
                status="pass" if has_need and not any(term in lower for term in ("melhorar", "otimizar")) else "fail",
                evidence=[user_story_text] if has_need and "melhorar" not in lower and "otimizar" not in lower else ev("melhorar", "otimizar"),
                reason="The story must include observable behavior, result, or condition.",
            ),
        )


class HeuristicReportGenerator:
    model_name = "heuristic-v1"

    def generate(
        self,
        user_story_text: str,
        analysis: InvestAnalysis,
        prompt: PromptTemplate,
    ) -> BadStoryReport:
        problems = []
        for criterion, item in analysis.as_criteria_dict().items():
            if item.status == "fail":
                problems.append(
                    ReportProblem(
                        criterion=criterion,
                        problem=f"The {criterion} criterion failed.",
                        evidence=item.evidence,
                        explanation=item.reason,
                    )
                )
        return BadStoryReport(problems=problems)
