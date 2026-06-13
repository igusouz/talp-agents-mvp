export interface AppEnvironment {
  appName: string
  appVersion: string
  orchestratorBaseUrl: string
  requestTimeoutMs: number
}

function parseTimeout(value: string | undefined, fallback: number): number {
  if (value == null || value.trim() === '') {
    return fallback
  }

  const parsed = Number(value)
  if (!Number.isFinite(parsed) || parsed <= 0) {
    throw new Error(`Invalid VITE_REQUEST_TIMEOUT_MS value: ${value}`)
  }

  return parsed
}

function normalizeBaseUrl(value: string | undefined): string {
  if (value == null || value.trim() === '') {
    throw new Error('VITE_ORCHESTRATOR_BASE_URL (or VITE_ORCHESTRATOR_API_BASE_URL) is required')
  }

  const url = new URL(value)
  return url.toString().replace(/\/$/, '')
}

export function loadEnvironment(env: ImportMetaEnv = import.meta.env): AppEnvironment {
  const orchestratorBaseUrl = env.VITE_ORCHESTRATOR_BASE_URL ?? env.VITE_ORCHESTRATOR_API_BASE_URL

  return {
    appName: env.VITE_APP_NAME ?? 'TALP Workflow Orchestrator UI',
    appVersion: env.VITE_APP_VERSION ?? '0.1.0',
    orchestratorBaseUrl: normalizeBaseUrl(orchestratorBaseUrl),
    requestTimeoutMs: parseTimeout(env.VITE_REQUEST_TIMEOUT_MS, 30000),
  }
}
