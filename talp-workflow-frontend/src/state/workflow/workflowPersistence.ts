import type { WorkflowState } from './workflowTypes'

const STORAGE_KEY = 'talp.workflow.state'

export function loadWorkflowState(): WorkflowState | null {
  if (typeof window === 'undefined') {
    return null
  }

  const raw = window.sessionStorage.getItem(STORAGE_KEY)
  if (!raw) {
    return null
  }

  try {
    return JSON.parse(raw) as WorkflowState
  } catch {
    window.sessionStorage.removeItem(STORAGE_KEY)
    return null
  }
}

export function saveWorkflowState(state: WorkflowState): void {
  if (typeof window === 'undefined') {
    return
  }

  window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

export function clearWorkflowState(): void {
  if (typeof window === 'undefined') {
    return
  }

  window.sessionStorage.removeItem(STORAGE_KEY)
}
