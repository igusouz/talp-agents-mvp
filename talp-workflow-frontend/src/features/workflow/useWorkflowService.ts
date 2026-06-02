import { useMemo } from 'react'

import { WorkflowService } from '@/api/workflowService'

export function useWorkflowService(): WorkflowService {
  return useMemo(() => new WorkflowService(), [])
}
