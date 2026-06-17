# TALP Workflow Orchestrator

The orchestrator coordinates the TALP Invest, Compliance, and BDD QA agents through a reusable HTTPX-based communication layer.

This repository now contains a FastAPI runtime plus the transport and contract layer used to coordinate the TALP workflow.

## What is included

- FastAPI workflow endpoints for workflow creation, review-state retrieval, approval submission, and BDD result retrieval.
- Typed request and response contracts for the three downstream agents.
- A generic `AgentClient` abstraction with timeout and retry handling.
- A client registry and factory functions so new agents can be added without changing orchestration logic.
- Structured logging configuration for request tracing.
- Compliance request enrichment that forwards the original rendered user story text to preserve full keyword context for downstream rule matching.

## Runtime

Start the API locally with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Architecture

See [docs/communication-layer.md](docs/communication-layer.md) for the dependency flow, class responsibilities, and interface map.
