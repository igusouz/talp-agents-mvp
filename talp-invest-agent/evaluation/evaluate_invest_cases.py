from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from time import sleep
from typing import Any

from app.config.settings import load_settings
from app.graph import InvestAgent, build_agent
from app.services.heuristic_backend import HeuristicInvestAnalyzer, HeuristicReportGenerator
from app.services.llm_client import GeminiInvestAnalyzer


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = Path(__file__).with_name("invest_ehr_problem_cases.json")
DEFAULT_OUTPUT_JSON = Path(__file__).with_name("invest_ehr_problem_results.json")
DEFAULT_OUTPUT_MD = Path(__file__).with_name("invest_ehr_problem_results.md")


def load_cases(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_evaluation_agent(backend: str) -> Any:
    if backend == "llm-analysis":
        settings = load_settings(ROOT)
        return InvestAgent(
            settings=settings,
            analyzer=GeminiInvestAnalyzer(
                settings.llm_model,
                temperature=0.0,
                max_tokens=settings.llm_max_tokens,
                request_timeout=settings.llm_timeout_seconds,
                retries=settings.llm_retries,
                thinking_budget=settings.llm_thinking_budget,
            ),
            report_generator=HeuristicReportGenerator(),
        )
    if backend == "heuristic-analysis":
        settings = load_settings(ROOT)
        return InvestAgent(
            settings=settings,
            analyzer=HeuristicInvestAnalyzer(),
            report_generator=HeuristicReportGenerator(),
        )
    return build_agent(backend=backend, project_root=ROOT)


def _base_result(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": case["id"],
        "group": case["group"],
        "expected_failed_criterion": case["expected_failed_criterion"],
        "known_problem": case["known_problem"],
        "story": case["story"],
    }


def evaluate_case(agent: Any, case: dict[str, Any], max_attempts: int) -> dict[str, Any]:
    expected = case["expected_failed_criterion"]
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            output = agent.run(case["story"])
            classification = output.result.step_2_classification
            failed = list(classification.failed_criteria)
            detected = expected in failed
            return {
                **_base_result(case),
                "attempts": attempt,
                "execution_status": "ok",
                "detected_expected_problem": detected,
                "false_negative": not detected,
                "agent_category": classification.category,
                "agent_failed_criteria": failed,
                "extra_failed_criteria": [
                    criterion for criterion in failed if criterion != expected
                ],
                "execution_id": output.execution_id,
                "model": output.audit.model,
            }
        except Exception as exc:  # noqa: BLE001 - evaluation must record agent failures.
            last_error = exc
            if attempt < max_attempts:
                sleep(1)

    error_type = type(last_error).__name__ if last_error else "UnknownError"
    error_message = str(last_error).splitlines()[0] if last_error else ""
    return {
        **_base_result(case),
        "attempts": max_attempts,
        "execution_status": "error",
        "detected_expected_problem": False,
        "false_negative": True,
        "agent_category": "execution_error",
        "agent_failed_criteria": [],
        "extra_failed_criteria": [],
        "execution_id": None,
        "model": {},
        "error_type": error_type,
        "error_message": error_message[:500],
    }


def markdown_table(results: list[dict[str, Any]]) -> str:
    header = [
        "| ID | Grupo | Problema esperado | Detectou? | Falso negativo? | Criterios falhos pelo agente | Extras |",
        "|---|---|---|---|---|---|---|",
    ]
    rows = []
    for result in results:
        rows.append(
            "| {id} | {group} | {expected} | {detected} | {false_negative} | {failed} | {extras} |".format(
                id=result["id"],
                group=result["group"],
                expected=result["expected_failed_criterion"],
                detected="erro"
                if result["execution_status"] == "error"
                else ("sim" if result["detected_expected_problem"] else "nao"),
                false_negative="sim" if result["false_negative"] else "nao",
                failed=", ".join(result["agent_failed_criteria"]) or "-",
                extras=", ".join(result["extra_failed_criteria"]) or "-",
            )
        )
    return "\n".join(header + rows) + "\n"


def write_outputs(
    backend: str,
    results: list[dict[str, Any]],
    output_json: Path,
    output_md: Path,
) -> None:
    payload = {
        "backend": backend,
        "summary": summary(results),
        "results": results,
    }
    output_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    output_md.write_text(markdown_table(results), encoding="utf-8")


def summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    false_negatives = [result for result in results if result["false_negative"]]
    execution_errors = [
        result for result in results if result["execution_status"] == "error"
    ]
    by_group = {}
    for group in sorted({result["group"] for result in results}):
        group_results = [result for result in results if result["group"] == group]
        by_group[group] = {
            "total": len(group_results),
            "detected": sum(result["detected_expected_problem"] for result in group_results),
            "false_negatives": sum(result["false_negative"] for result in group_results),
        }
    return {
        "total_cases": len(results),
        "detected_expected_problem": sum(result["detected_expected_problem"] for result in results),
        "false_negatives": len(false_negatives),
        "false_negative_ids": [result["id"] for result in false_negatives],
        "execution_errors": len(execution_errors),
        "execution_error_ids": [result["id"] for result in execution_errors],
        "by_group": by_group,
        "agent_categories": dict(Counter(result["agent_category"] for result in results)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend",
        choices=["llm", "heuristic", "llm-analysis", "heuristic-analysis"],
        default="llm",
    )
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--start-index", type=int, default=1)
    args = parser.parse_args()

    cases = load_cases(args.cases)
    if args.case_id:
        selected = set(args.case_id)
        cases = [case for case in cases if case["id"] in selected]
    elif args.start_index > 1:
        cases = cases[args.start_index - 1 :]
    if args.max_cases:
        cases = cases[: args.max_cases]
    agent = build_evaluation_agent(args.backend)
    results = []
    for index, case in enumerate(cases, start=1):
        result = evaluate_case(agent, case, args.max_attempts)
        results.append(result)
        write_outputs(args.backend, results, args.output_json, args.output_md)
        status = result["execution_status"]
        detected = "yes" if result["detected_expected_problem"] else "no"
        print(f"{index:02d}/{len(cases)} {case['id']} status={status} detected={detected}", flush=True)
    print(json.dumps(summary(results), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
