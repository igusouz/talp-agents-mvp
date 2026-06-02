import type { BddAnalysis, ComplianceAnalysis, InvestAnalysis, UserStory } from '@/api/models/workflow'

import type { WorkflowErrorState, WorkflowState } from './workflowTypes'

export type WorkflowAction =
  | {
      type: 'workflow/hydrate'
      payload: {
        workflowId: string
        stage: WorkflowState['stage']
        originalStory: UserStory
        editedStory?: UserStory | null
        approvedStory?: UserStory | null
        investAnalysis?: InvestAnalysis | null
        complianceAnalysis?: ComplianceAnalysis | null
        bddAnalysis?: BddAnalysis | null
        updatedAt?: string | null
      }
    }
  | {
      type: 'workflow/start'
      payload: {
        workflowId: string
        originalStory: UserStory
        investAnalysis: InvestAnalysis
        complianceAnalysis: ComplianceAnalysis
        updatedAt?: string | null
      }
    }
  | { type: 'workflow/set-draft-story'; payload: { editedStory: UserStory } }
  | { type: 'workflow/approve-story'; payload: { approvedStory: UserStory; updatedAt?: string | null } }
  | { type: 'workflow/mark-invest-analysis'; payload: { investAnalysis: InvestAnalysis; updatedAt?: string | null } }
  | { type: 'workflow/mark-compliance-analysis'; payload: { complianceAnalysis: ComplianceAnalysis; updatedAt?: string | null } }
  | { type: 'workflow/mark-awaiting-human-review'; payload: { updatedAt?: string | null } }
  | { type: 'workflow/mark-bdd-processing'; payload: { updatedAt?: string | null } }
  | { type: 'workflow/complete'; payload: { bddAnalysis: BddAnalysis; updatedAt?: string | null } }
  | { type: 'workflow/fail'; payload: { error: WorkflowErrorState; updatedAt?: string | null } }
  | { type: 'workflow/reset' }

export function createInitialWorkflowState(): WorkflowState {
  return {
    workflowId: null,
    stage: 'draft',
    originalStory: null,
    editedStory: null,
    approvedStory: null,
    investAnalysis: null,
    complianceAnalysis: null,
    bddAnalysis: null,
    isLoading: false,
    error: null,
    updatedAt: null,
  }
}

function updateCommonState(
  state: WorkflowState,
  updates: Partial<Pick<WorkflowState, 'workflowId' | 'stage' | 'originalStory' | 'editedStory' | 'approvedStory' | 'investAnalysis' | 'complianceAnalysis' | 'bddAnalysis' | 'error' | 'updatedAt'>>,
): WorkflowState {
  return {
    ...state,
    ...updates,
    isLoading: false,
  }
}

export function workflowReducer(state: WorkflowState, action: WorkflowAction): WorkflowState {
  switch (action.type) {
    case 'workflow/hydrate':
      return updateCommonState(state, {
        workflowId: action.payload.workflowId,
        stage: action.payload.stage,
        originalStory: action.payload.originalStory,
        editedStory: action.payload.editedStory ?? action.payload.originalStory,
        approvedStory: action.payload.approvedStory ?? action.payload.editedStory ?? action.payload.originalStory,
        investAnalysis: action.payload.investAnalysis ?? null,
        complianceAnalysis: action.payload.complianceAnalysis ?? null,
        bddAnalysis: action.payload.bddAnalysis ?? null,
        error: null,
        updatedAt: action.payload.updatedAt ?? new Date().toISOString(),
      })

    case 'workflow/start':
      return updateCommonState(state, {
        workflowId: action.payload.workflowId,
        stage: 'waiting_for_review',
        originalStory: action.payload.originalStory,
        editedStory: action.payload.originalStory,
        approvedStory: null,
        investAnalysis: action.payload.investAnalysis,
        complianceAnalysis: action.payload.complianceAnalysis,
        bddAnalysis: null,
        error: null,
        updatedAt: action.payload.updatedAt ?? new Date().toISOString(),
      })

    case 'workflow/set-draft-story':
      return updateCommonState(state, {
        editedStory: action.payload.editedStory,
        updatedAt: new Date().toISOString(),
      })

    case 'workflow/approve-story':
      return updateCommonState(state, {
        approvedStory: action.payload.approvedStory,
        editedStory: action.payload.approvedStory,
        stage: 'approved',
        updatedAt: action.payload.updatedAt ?? new Date().toISOString(),
        error: null,
      })

    case 'workflow/mark-invest-analysis':
      return updateCommonState(state, {
        investAnalysis: action.payload.investAnalysis,
        stage: 'invest_done',
        updatedAt: action.payload.updatedAt ?? new Date().toISOString(),
        error: null,
      })

    case 'workflow/mark-compliance-analysis':
      return updateCommonState(state, {
        complianceAnalysis: action.payload.complianceAnalysis,
        stage: 'compliance_done',
        updatedAt: action.payload.updatedAt ?? new Date().toISOString(),
        error: null,
      })

    case 'workflow/mark-awaiting-human-review':
      return updateCommonState(state, {
        stage: 'waiting_for_review',
        updatedAt: action.payload.updatedAt ?? new Date().toISOString(),
        error: null,
      })

    case 'workflow/mark-bdd-processing':
      return updateCommonState(state, {
        stage: 'approved',
        updatedAt: action.payload.updatedAt ?? new Date().toISOString(),
        error: null,
      })

    case 'workflow/complete':
      return updateCommonState(state, {
        stage: 'bdd_done',
        bddAnalysis: action.payload.bddAnalysis,
        updatedAt: action.payload.updatedAt ?? new Date().toISOString(),
        error: null,
      })

    case 'workflow/fail':
      return updateCommonState(state, {
        stage: 'failed',
        error: action.payload.error,
        updatedAt: action.payload.updatedAt ?? new Date().toISOString(),
      })

    case 'workflow/reset':
      return createInitialWorkflowState()

    default:
      return state
  }
}
