from pathlib import Path

from app.graph import build_agent


def test_agent_flow_writes_audit_log(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("TALP_AUDIT_LOG_DIR", str(tmp_path))
    agent = build_agent(backend="heuristic", project_root=Path(__file__).resolve().parents[1])

    output = agent.run("Como administrador, quero melhorar o sistema.")

    assert output.result.step_2_classification.category == "ruim"
    assert output.result.step_3_report is not None
    assert list(tmp_path.glob("agent_runs_*.jsonl"))
