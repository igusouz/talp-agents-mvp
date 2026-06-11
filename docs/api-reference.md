# API Reference

This document describes the available APIs in the repository.

## General Notes

- All payloads should be treated as typed JSON objects.
- Error responses typically include a `detail` field from FastAPI or a structured validation/transport error object.
- Base URLs below assume local development ports.

## Workflow Orchestrator API

This section documents the workflow contract consumed by the frontend and the orchestrator client layer. The current repository does not yet ship a standalone orchestrator runtime server, so treat these routes as the intended HTTP contract for the platform.

### Base URL

`http://localhost:8000/api/v1`

### Start Workflow

`POST /workflows/stories`

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

- `200 OK` or `201 Created` for successful workflow creation.
- `400 Bad Request` for validation failures.
- `429 Too Many Requests` for upstream throttling.
- `500 Internal Server Error` for unexpected failures.

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
  "stage": "bdd_done",
  "approved_story": { "title": "...", "description": "...", "acceptance_criteria": [] },
  "bdd_analysis": {
    "summary": "...",
    "bdd_scenarios": [],
    "negative_cases": [],
    "edge_cases": [],
    "ambiguities": [],
    "risks": [],
    "automation_suggestions": [],
    "questions_for_refinement": []
  },
  "correlation_id": "corr_789"
}
```

Status codes:

- `200 OK`
- `400 Bad Request`
- `404 Not Found`
- `500 Internal Server Error`

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

## Invest Agent APIs

### Base URL

The current repository does not expose an HTTP API for the Invest Agent.

### Available interface

The Invest Agent is currently a CLI-first service:

`python -m app.main <user_story> --backend llm|heuristic`

Typical output is a JSON serialized `FinalOutput` object that includes:

- `execution_id`
- `schema_version`
- `input`
- `result`
- `audit`

### Status

- No REST endpoints are implemented in the repository today.
- The Workflow Orchestrator currently documents an HTTP target for Invest Agent integration, but that route is not present in the Invest Agent codebase yet.

## Compliance Agent APIs

### Base URL

`http://localhost:8000/api/v1`

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
