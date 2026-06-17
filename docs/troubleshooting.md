# Troubleshooting

This document collects the most common problems and the fastest ways to diagnose them.

## Frontend cannot reach the orchestrator

### Symptoms

- The submission page fails immediately.
- The browser console shows a network error.
- The workflow pages stay in a loading or empty state.

### Checks

- Confirm `VITE_ORCHESTRATOR_API_BASE_URL` points to the correct host and port.
- Confirm the orchestrator service is running.
- Verify CORS if the frontend and orchestrator are on different hosts.
- Open the orchestrator health endpoint in the browser or with `curl`.

## Compliance analysis fails

### Symptoms

- The workflow starts but compliance data never appears.
- The orchestrator returns a 4xx or 5xx response.
- The compliance service logs show validation or persistence errors.

### Checks

- Confirm the request matches `ComplianceAnalysisRequest`.
- Ensure the invest result contains the nested `invest_result` structure expected by the service.
- Verify the SQLite database path exists and is writable.
- Confirm the catalog CSV is present at `data/catalog_rules_v1.csv`.

## BDD analysis returns rate-limit errors

### Symptoms

- The BDD agent returns `429 Too Many Requests`.
- The frontend shows a retryable error.

### Checks

- Verify `GOOGLE_API_KEY` is set for the default Gemini configuration.
- If using a BDD-specific credential, verify `QA_LLM_API_KEY` is set.
- Confirm the configured Gemini model is available for the key and project.
- Check `QA_LLM_TIMEOUT_SECONDS` and `QA_LLM_TEMPERATURE`.
- Retry after a short delay if the provider is throttling.

## Invest Agent output looks wrong

### Symptoms

- INVEST classification does not match expectations.
- The final report is missing evidence.
- The output does not seem to align with the story content.

### Checks

- Confirm the story text is valid and not blank.
- Verify the chosen backend (`llm` or `heuristic`).
- Review the prompt registry and output validation logic.
- Check the audit logs for the execution id and prompt version.

## Docker startup problems

### Symptoms

- A container exits immediately.
- Compose reports port conflicts.
- Services cannot resolve each other by name.

### Checks

- Ensure the required ports are not already in use.
- Confirm the service names in Docker Compose match the orchestrator base URLs.
- If Compose reports `GOOGLE_API_KEY is required for Gemini agents`, create or update the root `.env` file with a valid `GOOGLE_API_KEY`.
- Replace placeholder credentials such as `replace-me` or `your-google-api-key-here`; the agents reject those values before provider calls.
- Rebuild after config changes.
- Inspect logs with `docker compose logs -f`.

## Frontend review state is stale

### Symptoms

- The review page still shows old content after navigation.
- The final page does not show the BDD result.

### Checks

- Confirm the workflow id in the route matches the persisted state.
- Reload the workflow from the orchestrator.
- Clear session storage if a local draft is corrupt.

## FastAPI validation errors

### Symptoms

- Requests fail with `422 Unprocessable Entity`.
- The response contains field-level validation details.

### Checks

- Compare the payload to the documented request models.
- Ensure all required fields are present.
- Check for snake_case versus camelCase mismatches.

## Common recovery actions

- Restart the affected service only.
- Clear browser session storage for the workflow state.
- Rebuild Docker images after dependency or config changes.
- Review the logs for correlation ids or request ids.
