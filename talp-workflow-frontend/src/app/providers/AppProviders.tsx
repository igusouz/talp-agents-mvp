import type { ReactNode } from 'react'

import { ApiClientProvider } from '@/shared/api/ApiClientProvider'
import { WorkflowStateProvider } from '@/state/workflow'

interface AppProvidersProps {
  children: ReactNode
}

export function AppProviders({ children }: AppProvidersProps) {
  return (
    <ApiClientProvider>
      <WorkflowStateProvider>{children}</WorkflowStateProvider>
    </ApiClientProvider>
  )
}
