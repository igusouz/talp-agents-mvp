import type { WorkflowProgress, WorkflowState } from './workflowTypes'

const workflowProgress: WorkflowProgress[] = [
  { stage: 'draft', label: 'Draft' },
  { stage: 'invest_done', label: 'Invest Analysis' },
  { stage: 'compliance_done', label: 'Compliance Analysis' },
  { stage: 'waiting_for_review', label: 'Awaiting Human Review' },
  { stage: 'approved', label: 'BDD Processing' },
  { stage: 'bdd_done', label: 'Completed' },
]

export function selectWorkflowProgress(): WorkflowProgress[] {
  return workflowProgress
}

export function selectIsActiveWorkflow(state: WorkflowState): boolean {
  return state.workflowId !== null && state.stage !== 'draft'
}
