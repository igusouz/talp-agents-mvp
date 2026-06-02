# TALP Workflow Orchestrator

The orchestrator coordinates the TALP Invest, Compliance, and BDD QA agents through a reusable HTTPX-based communication layer.

This repository currently contains the transport and contract layer only. Business orchestration logic, persistence, and API endpoints are intentionally left for the next iteration.

## What is included

- Typed request and response contracts for the three downstream agents.
- A generic `AgentClient` abstraction with timeout and retry handling.
- A client registry and factory functions so new agents can be added without changing orchestration logic.
- Structured logging configuration for request tracing.

## Architecture

See [docs/communication-layer.md](docs/communication-layer.md) for the dependency flow, class responsibilities, and interface map.
