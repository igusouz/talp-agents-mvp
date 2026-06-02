# BDD QA Agent

An MVP QA agent focused on analyzing user stories and generating structured BDD artifacts.

## Goal

This project delivers a structured, non-autonomous LLM workflow to analyze a user story and return:

- BDD scenarios in Gherkin
- Acceptance criteria validation
- Negative test cases
- Edge cases
- Ambiguities and missing requirements
- Functional risks
- Automation suggestions
- Questions for refinement

## Why this architecture

The first version needs to be fast to implement, predictable, and easy to evolve into a multi-agent system later. That's why the foundation uses:

- FastAPI to expose the HTTP endpoint
- LangChain as the orchestration layer
- Pydantic for input and output contracts
- Versioned prompts outside business code
- A simple service layer between route and chain to facilitate future multi-agent orchestration

## Project structure

```text
app/
  api/
    routes/
  chains/
  core/
  prompts/
    few_shots/
    system/
    templates/
    versions/
  schemas/
  services/
tests/
  evals/
```

## Initial dependencies

- fastapi
- uvicorn[standard]
- pydantic
- pydantic-settings
- langchain
- langchain-core
- langchain-openai

Dev:

- pytest
- httpx
- ruff

## How the workflow operates

1. The API receives a story. If acceptance criteria are present they should be
  embedded inside the story text (for example under an "Acceptance criteria:" header
  or as list items starting with "-"). The service will extract them automatically.
2. The service normalizes the input and calls the chain.
3. The chain uses a system prompt and few-shot examples to guide the model.
4. The model responds with structured JSON via a Pydantic schema.
5. The route returns the payload without additional transformation.

## Expected contract

Input (single-field):

```json
{
  "story": "As a user, I want to reset my password so I can recover access to my account.\n\nAcceptance criteria:\n- The user must receive a reset email\n- The reset link expires in 30 minutes\n- The new password must contain at least one number"
}
```

Output:

```json
{
  "summary": "",
  "bdd_scenarios": [],
  "negative_cases": [],
  "edge_cases": [],
  "ambiguities": [],
  "risks": [],
  "automation_suggestions": [],
  "questions_for_refinement": []
}
```

## Quick setup

1. Create a virtual environment.
2. Install dependencies from `pyproject.toml`.
3. Copy `.env.example` to `.env` and configure credentials.
4. Run the API with `uvicorn app.main:app --reload`.

## Prompt organization

Prompt content is now separated into dedicated folders so each behavior can evolve independently:

- `app/prompts/system/` for system rules
- `app/prompts/few_shots/` for examples
- `app/prompts/templates/` for human prompt templates
- `app/prompts/versions/` for prompt release tracking

This layout makes it easier to test prompt changes, A/B variants, and future agent-specific prompt bundles.

## Evaluation layer

The repository includes a lightweight semantic evaluation layer under `tests/evals/`.

The goal is to validate quality signals such as:

- edge case coverage
- ambiguity detection
- negative scenario generation
- requirement completeness
- regression prevention during prompt updates

The evals intentionally remain small and JSON-backed so they are easy to extend without introducing additional infrastructure.

## Testing

This project includes comprehensive unit and integration tests that mock external dependencies, allowing you to validate the application without requiring OpenAI API credentials.

### Test Structure

- **tests/conftest.py**: Shared pytest fixtures and mock LLM responses.
- **tests/test_schemas.py**: Pydantic contract validation tests.
- **tests/test_chains.py**: LangChain workflow tests with mocked LLM.
- **tests/test_api.py**: FastAPI route tests with mocked service layer.
- **tests/evals/**: JSON-backed semantic regression checks.

### Running Tests

Install test dependencies:

```bash
pip install -e ".[dev]"
```

Run all tests:

```bash
pytest
```

Run specific test file:

```bash
pytest tests/test_schemas.py
```

Run with coverage:

```bash
pip install pytest-cov
pytest --cov=app tests/
```

### Test Mocking Strategy

Tests use `unittest.mock.patch` to replace the real `ChatOpenAI` client with a mock that returns structured JSON responses without calling OpenAI's API. This keeps tests fast and dependency-free.

The `conftest.py` provides reusable fixtures:

- `test_client`: FastAPI TestClient for route testing.
- `mock_qa_response`: Realistic QA analysis response for validation.
- `mock_llm_response`: Mock LLM response as AIMessage.

### Coverage

Tests validate:

1. **Schema contracts** — Request validation (story required, criteria optional), response completeness, field types.
2. **Chain workflows** — Initialization, prompt loading, acceptance criteria formatting, mock LLM invocation.
3. **API routes** — Health check endpoint, QA analysis with valid/invalid payloads, response structure.

### Continuous Integration

Tests are designed to run in any environment without external dependencies. All tests must pass and coverage should stay above 80%:

```bash
pytest --cov=app tests/
```

## Docker

This project includes Docker support for easier integration and local development. The repository contains a `Dockerfile`, `.dockerignore`, and a `docker-compose.yml` for quick startup.

Basic build and run commands:

```bash
# Build the image locally
docker build -t bdd-qa-agent .

# Run the container (provide your .env with real credentials)
docker run -p 8000:8000 --env-file .env bdd-qa-agent

# Or using docker-compose
docker compose up --build
```

Notes:
- Provide a valid `QA_LLM_API_KEY` (via `.env` or environment) before calling endpoints that use the LLM.
- For production images prefer a multi-stage build that installs only runtime dependencies (remove `.[dev]`).
- Consider using a secret manager for API keys instead of embedding in `.env` for CI/CD.
