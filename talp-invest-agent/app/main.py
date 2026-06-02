from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.graph import build_agent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="talp-invest-agent",
        description="Evaluate a user story according to INVEST.",
    )
    parser.add_argument("user_story", help="User story text in natural language.")
    parser.add_argument(
        "--backend",
        choices=("llm", "heuristic"),
        default="llm",
        help="Execution backend. Default: llm.",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Project root. Defaults to the package root.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    agent = build_agent(
        backend=args.backend,
        project_root=Path(args.project_root) if args.project_root else None,
    )
    output = agent.run(args.user_story)
    print(json.dumps(output.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

