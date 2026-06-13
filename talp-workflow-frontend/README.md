# TALP Workflow Frontend

Frontend foundation for the TALP multi-agent platform built with React, TypeScript, and Vite.

## Included

- Routing skeleton for submission, review, and final result workflows.
- App shell and workflow shell layouts.
- Typed API client foundation for the Workflow Orchestrator.
- Environment configuration and error boundary strategy.
- Shared type contracts for future workflow pages.

## Development

1. Copy `.env.example` to `.env`.
2. Install dependencies with your preferred package manager.
3. Run `npm run dev`.

## Environment

- `VITE_ORCHESTRATOR_BASE_URL` is the primary API base URL.
- `VITE_ORCHESTRATOR_API_BASE_URL` remains supported as a legacy alias.
- `VITE_REQUEST_TIMEOUT_MS` controls frontend request timeout.
- `VITE_ENABLE_MOCKS` toggles mock behavior in local development.

## Scripts

- `npm run dev`
- `npm run build`
- `npm run preview`
- `npm run typecheck`
