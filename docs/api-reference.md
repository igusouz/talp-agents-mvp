# API Reference

This document describes the available APIs in the repository.

## General Notes

- All payloads should be treated as typed JSON objects.
- Error responses typically include a `detail` field from FastAPI or a structured validation/transport error object.
- Base URLs below assume local development ports.

## Workflow Orchestrator API

This section documents the workflow contract consumed by the frontend and exposed by the orchestrator runtime server.

### Base URL

`http://localhost:8000/api/v1`

### Start Workflow

`POST /workflows`

Request payload:

```json
{
  "user_story": {
    "title": "As a customer, I want to reset my password",
    "description": "The user should be able to request a password reset link.",
    "acceptance_criteria": [
      "A reset link is sent to the registered email address",
      "The link expires after 30 minutes"
    ],
    "additional_context": "Security-sensitive flow"
  },
  "metadata": {
    "source": "frontend"
  }
}
```

Typical response payload:

```json
{
  "workflow_id": "wf_123",
  "stage": "waiting_for_review",
  "original_story": {
    "title": "As a customer, I want to reset my password",
    "description": "The user should be able to request a password reset link.",
    "acceptance_criteria": [
      "A reset link is sent to the registered email address",
      "The link expires after 30 minutes"
    ],
    "additional_context": "Security-sensitive flow"
  },
  "invest_analysis": {
    "independent": { "status": "pass", "evidence": [], "reason": "..." },
    "negotiable": { "status": "pass", "evidence": [], "reason": "..." },
    "valuable": { "status": "pass", "evidence": [], "reason": "..." },
    "estimable": { "status": "pass", "evidence": [], "reason": "..." },
    "small": { "status": "fail", "evidence": [], "reason": "..." },
    "testable": { "status": "pass", "evidence": [], "reason": "..." }
  },
  "compliance_analysis": {
    "analysis_id": "comp_456",
    "investment_id": "inv_123",
    "status": "partial",
    "summary": "...",
    "compliance_gaps": []
  },
  "next_action": "review",
  "correlation_id": "corr_789"
}
```

Status codes:

- `201 Created` for successful workflow creation.
- `422 Unprocessable Entity` for request validation failures.
- `4xx` or `5xx` forwarded when a downstream service fails.
- `502 Bad Gateway` for transport/runtime failures while calling downstream agents.

### Retrieve Workflow State

`GET /workflows/{workflow_id}`

Response payload:

```json
{
  "workflow_id": "wf_123",
  "stage": "waiting_for_review",
  "original_story": { "title": "...", "description": "...", "acceptance_criteria": [] },
  "approved_story": { "title": "...", "description": "...", "acceptance_criteria": [] },
  "invest_analysis": { "independent": { "status": "pass", "evidence": [], "reason": "..." } },
  "compliance_analysis": { "analysis_id": "comp_456", "investment_id": "inv_123", "status": "partial", "summary": "...", "compliance_gaps": [] },
  "bdd_analysis": null,
  "updated_at": "2026-06-11T10:30:00Z",
  "correlation_id": "corr_789"
}
```

Status codes:

- `200 OK`
- `404 Not Found`

### Submit Approved Story

`POST /workflows/{workflow_id}/approval`

Request payload:

```json
{
  "approved_story": {
    "title": "As a customer, I want to reset my password",
    "description": "I can request a password reset link and complete the reset securely.",
    "acceptance_criteria": [
      "A reset link is sent to the registered email address",
      "The link expires after 30 minutes"
    ],
    "additional_context": "Approved after human review"
  },
  "reviewer_id": "frontend-human-review",
  "review_notes": "Adjusted wording for clarity",
  "metadata": {
    "modified": true
  }
}
```

Typical response payload:

```json
{
  "workflow_id": "wf_123",
  "stage": "approved",
  "approved_story": { "title": "...", "description": "...", "acceptance_criteria": [] },
  "bdd_analysis": null,
  "updated_at": "2026-06-11T10:30:30Z",
  "correlation_id": "corr_789"
}
```

`POST /workflows/{workflow_id}/approval` is asynchronous. The API accepts the approved story and starts BDD generation in the background. Clients should poll `GET /workflows/{workflow_id}` until `stage` becomes `bdd_done` or `failed`.

Status codes:

- `202 Accepted`
- `404 Not Found`
- `422 Unprocessable Entity`

### Retrieve BDD Results

`GET /workflows/{workflow_id}/bdd-results`

Response payload:

```json
{
  "bdd_analysis": {
    "summary": "...",
    "bdd_scenarios": [],
    "negative_cases": [],
    "edge_cases": [],
    "ambiguities": [],
    "risks": [],
    "automation_suggestions": [],
    "questions_for_refinement": []
  }
}
```

Status codes:

- `200 OK`
- `404 Not Found`
- `409 Conflict` when BDD processing is not finished yet.

## Invest Agent APIs

### Base URL

`http://localhost:8001/api/v1/invest`

### Analyze Story

`POST /analyze`

Request payload:

```json
{
  "user_story_text": "Title: Password reset\n\nAs a customer, I want to reset my password.\n\nAcceptance criteria:\n- A reset link is sent to the email"
}
```

Response payload:

```json
{
  "execution_id": "...",
  "schema_version": "...",
  "input": {
    "user_story_text": "..."
  },
  "result": {
    "step_1_invest_analysis": {
      "independent": { "status": "pass", "evidence": [], "reason": "..." }
    },
    "step_2_classification": {
      "category": "boa",
      "rule_applied": "all criteria pass",
      "failed_criteria": []
    },
    "step_3_report": null
  },
  "audit": {
    "prompt_versions": {},
    "prompt_hashes": {},
    "model": {},
    "created_at_utc": "2026-06-11T10:30:00Z"
  }
}
```

### Health

`GET /health`

### CLI Interface

The Invest Agent also supports a direct CLI interface:

`python -m app.main <user_story> --backend llm|heuristic`

Typical output is a JSON serialized `FinalOutput` object that includes:

- `execution_id`
- `schema_version`
- `input`
- `result`
- `audit`

## Compliance Agent APIs

### Base URL

`http://localhost:8000/api/v1`

### Matching Notes

- The Compliance Agent performs keyword matching against the original rendered user story text when it is available in `invest_result.metadata.user_story_text`.
- The Workflow Orchestrator now forwards that original rendered story to the Compliance Agent to avoid false negatives caused by matching only against a reduced INVEST summary.
- When `invest_result.metadata.user_story_text` is absent, the Compliance Agent falls back to `invest_result.summary` and then enriches the text with `criteria_results` evidence.

### Health

`GET /health`

Returns a basic health object:

```json
{
  "status": "healthy",
  "service": "talp-compliance-agent",
  "version": "0.1.0"
}
```

### API v1 Health

`GET /api/v1/health`

Returns a typed `HealthResponse`.

### Analyze Compliance

`POST /api/v1/compliance/analyze`

Request payload:

```json
{
  "investment_id": "inv_123",
  "invest_result": {
    "investment_id": "inv_123",
    "status": "warning",
    "criteria_results": [
      {
        "criterion_id": "small",
        "criterion_name": "small",
        "result": false,
        "evidence": "Too much scope"
      }
    ],
    "summary": "...",
    "metadata": {}
  }
}
```

Response payload:

```json
{
  "analysis_id": "comp_456",
  "investment_id": "inv_123",
  "status": "partial",
  "detected_rules": [
    {
      "rule_id": "RULE-001",
      "name": "Password reset must be auditable",
      "domain": "security",
      "matched": true,
      "confidence": 0.92,
      "evidence_found": [],
      "dependencies": []
    }
  ],
  "compliance_gaps": [],
  "requirements": [],
  "summary": "...",
  "timestamp": "2026-06-11T10:30:00Z",
  "metadata": {}
}
```

### Analyze from File

`POST /api/v1/compliance/analyze-file`

Request payload:

```json
{
  "file_path": "data/samples/compliance_request_sample.json"
}
```

### List Runs

`GET /api/v1/compliance/runs?limit=100&offset=0`

### Retrieve Run

`GET /api/v1/compliance/runs/{run_id}`

### Catalog Rules

`GET /api/v1/catalog/rules`

### Sync Catalog

`POST /api/v1/catalog/sync`

Status codes across compliance endpoints:

- `200 OK`
- `400 Bad Request`
- `404 Not Found`
- `500 Internal Server Error`

## BDD QA Agent APIs

### Base URL

`http://localhost:8000/api/v1`

### Health

`GET /health`

### Analyze Story

`POST /api/v1/qa/analyze`

Request payload:

```json
{
  "story": "As a customer, I want to reset my password so that I can regain access."
}
```

Response payload:

```json
{
  "summary": "The story is suitable for BDD but needs clearer acceptance criteria.",
  "bdd_scenarios": [
    {
      "title": "Successful password reset",
      "scenario_type": "positive",
      "given": ["the user has a registered account"],
      "when": ["the user submits a valid reset request"],
      "then": ["the user receives a reset email"],
      "notes": ["Consider expiration handling"]
    }
  ],
  "negative_cases": ["invalid email address"],
  "edge_cases": ["expired reset token"],
  "ambiguities": ["The desired token lifetime is not specified"],
  "risks": ["Account takeover if reset flow is weak"],
  "automation_suggestions": ["Automate token expiry tests"],
  "questions_for_refinement": ["Should rate limiting apply?"]
}
```

Status codes:

- `200 OK`
- `429 Too Many Requests` when the upstream model rate limits requests.
- `400 Bad Request` for validation failures.

## Error Responses

Typical error formats:

- FastAPI validation errors with `detail` describing invalid fields.
- `404 Not Found` with a `detail` message for missing resources.
- `429 Too Many Requests` when the BDD model provider is throttled.
- `500 Internal Server Error` for unhandled failures.

For frontend and orchestration clients, treat all non-2xx responses as typed transport errors and preserve the response payload for debugging.
