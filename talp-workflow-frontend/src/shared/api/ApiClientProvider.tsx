import { createContext, useContext, useMemo, type ReactNode } from 'react'

import { createOrchestratorApi, WorkflowOrchestratorApi } from '@/shared/api/orchestratorApi'
import { loadEnvironment } from '@/shared/config/env'

const ApiClientContext = createContext<WorkflowOrchestratorApi | null>(null)

interface ApiClientProviderProps {
  children: ReactNode
}

export function ApiClientProvider({ children }: ApiClientProviderProps) {
  const apiClient = useMemo(() => {
    const env = loadEnvironment()
    return createOrchestratorApi({
      baseUrl: env.orchestratorBaseUrl,
      timeoutMs: env.requestTimeoutMs,
    })
  }, [])

  return <ApiClientContext.Provider value={apiClient}>{children}</ApiClientContext.Provider>
}

export function useApiClient() {
  const client = useContext(ApiClientContext)
  if (!client) {
    throw new Error('useApiClient must be used within ApiClientProvider')
  }

  return client
}
