# Development Guide

This guide is written for contributors and maintainers of the TALP repository.

## Repository Structure

### `frontend/`

This repository currently uses [talp-workflow-frontend/](../talp-workflow-frontend/) as the frontend application folder.

Purpose:

- User story submission
- Analysis review
- Human review and approval
- Final BDD results presentation

### `workflow-orchestrator/`

The orchestrator lives in [talp-workflow-orchestrator/](../talp-workflow-orchestrator/).

Purpose:

- Typed communication layer
- HTTP client abstractions
- Retry and timeout handling
- Future workflow service boundary

### `talp-invest-agent/`

Purpose:

- INVEST analysis
- LangGraph-based story evaluation
- Deterministic output and audit metadata
- CLI execution entrypoint

### `talp-compliance-agent/`

Purpose:

- Compliance validation against a catalog
- FastAPI APIs for analysis and catalog access
- SQLite persistence and stored runs
- Streamlit review and administration interface

### `talp-bdd-agent/`

Purpose:

- BDD scenario generation
- QA-oriented user story analysis
- FastAPI API for `/api/v1/qa/analyze`
- Structured Pydantic response models

### `docs/`

Purpose:

- Architecture and workflow documentation
- Deployment and operations instructions
- API reference and troubleshooting guidance
- Diagram source material

## Testing Strategy

### Unit tests

Use unit tests for:

- Pure functions
- Schema validators
- Mapping and normalization logic
- State reducers
- Error conversion helpers

### Integration tests

Use integration tests for:

- Workflow Orchestrator HTTP client behavior
- FastAPI route contracts
- End-to-end service request/response consistency
- Frontend workflow page interactions

### Mocking strategy

- Mock HTTP calls to downstream services with `respx` or equivalent tools.
- Mock model-provider calls where the repo does not want live LLM traffic in tests.
- Mock browser/network state in frontend tests when validating UI flows.

### Evaluation tests

The repository already includes evaluation-oriented tests for agent behavior, especially in the BDD and INVEST subprojects.

Use them to validate:

- Prompt regressions
- Scenario quality
- Guardrail behavior
- Output schema stability

### Coverage expectations

For a production-grade proof of concept, aim to cover:

- All public API endpoints
- All typed DTO mappings
- Workflow state transitions
- Validation and error handling branches
- Critical prompt and evaluation paths

A pragmatic target is high coverage for pure logic and meaningful contract coverage for service boundaries.

## Contributor Workflow

1. Make small changes in one service boundary at a time.
2. Update the relevant docs file when behavior changes.
3. Run the nearest tests first, then the broader suite.
4. Keep agent contracts explicit and typed.
5. Preserve human-review semantics in the workflow.

## Repository Hygiene

The repository root contains a shared `.gitignore` for generated files across all services.

Do not commit:

- Python bytecode and caches such as `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.mypy_cache/`, and `.ruff_cache/`.
- Local virtual environments such as `.venv/`, `venv/`, and `env/`.
- Frontend dependency and build output such as `node_modules/`, `build/`, and `dist/`.
- Local runtime files such as `.env`, logs, JSONL audit logs, SQLite databases, and generated storage contents.

Keep versioned:

- `.env.example` files that document required configuration.
- `.gitkeep` placeholders used to preserve required empty runtime directories.

## Practical Notes

- The Invest Agent now supports both CLI and HTTP execution, so contract changes should be documented and tested carefully in both entrypoints.
- The Compliance Agent persists data and can be affected by local storage state, so reset or isolate the database in tests.
- The frontend should never talk to downstream agents directly; it should go through the orchestrator.
