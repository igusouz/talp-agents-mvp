import { createContext, useContext, useEffect, useMemo, useReducer, type ReactNode } from 'react'

import { clearWorkflowState, loadWorkflowState, saveWorkflowState } from './workflowPersistence'
import { selectIsActiveWorkflow, selectWorkflowProgress } from './workflowSelectors'
import { createInitialWorkflowState, workflowReducer, type WorkflowAction } from './workflowReducer'
import type { WorkflowContextValue, WorkflowErrorState } from './workflowTypes'

const WorkflowStateContext = createContext<WorkflowContextValue | null>(null)

interface WorkflowStateProviderProps {
  children: ReactNode
}

function dispatchWorkflowAction(dispatch: React.Dispatch<WorkflowAction>, action: WorkflowAction) {
  dispatch(action)
}

export function WorkflowStateProvider({ children }: WorkflowStateProviderProps) {
  const [state, dispatch] = useReducer(workflowReducer, undefined, () => loadWorkflowState() ?? createInitialWorkflowState())

  useEffect(() => {
    if (state.workflowId === null && state.stage === 'draft') {
      clearWorkflowState()
      return
    }

    saveWorkflowState(state)
  }, [state])

  const value = useMemo<WorkflowContextValue>(() => {
    const failWorkflow = (error: WorkflowErrorState, updatedAt?: string | null) =>
      dispatchWorkflowAction(dispatch, { type: 'workflow/fail', payload: { error, updatedAt } })

    return {
      state,
      progress: selectWorkflowProgress(),
      isActiveWorkflow: selectIsActiveWorkflow(state),
      hydrateWorkflow: ({
        workflowId,
        stage,
        originalStory,
        editedStory,
        approvedStory,
        investAnalysis,
        complianceAnalysis,
        bddAnalysis,
        updatedAt,
      }) =>
        dispatchWorkflowAction(dispatch, {
          type: 'workflow/hydrate',
          payload: {
            workflowId,
            stage,
            originalStory,
            editedStory: editedStory ?? null,
            approvedStory: approvedStory ?? null,
            investAnalysis: investAnalysis ?? null,
            complianceAnalysis: complianceAnalysis ?? null,
            bddAnalysis: bddAnalysis ?? null,
            updatedAt,
          },
        }),
      setDraftStory: (story) =>
        dispatchWorkflowAction(dispatch, { type: 'workflow/set-draft-story', payload: { editedStory: story } }),
      approveStory: (approvedStory, updatedAt) =>
        dispatchWorkflowAction(dispatch, {
          type: 'workflow/approve-story',
          payload: { approvedStory, updatedAt },
        }),
      startWorkflow: ({ workflowId, originalStory, investAnalysis, complianceAnalysis, updatedAt }) =>
        dispatchWorkflowAction(dispatch, {
          type: 'workflow/start',
          payload: { workflowId, originalStory, investAnalysis, complianceAnalysis, updatedAt },
        }),
      markInvestAnalysis: (investAnalysis, updatedAt) =>
        dispatchWorkflowAction(dispatch, {
          type: 'workflow/mark-invest-analysis',
          payload: { investAnalysis, updatedAt },
        }),
      markComplianceAnalysis: (complianceAnalysis, updatedAt) =>
        dispatchWorkflowAction(dispatch, {
          type: 'workflow/mark-compliance-analysis',
          payload: { complianceAnalysis, updatedAt },
        }),
      markAwaitingHumanReview: (updatedAt) =>
        dispatchWorkflowAction(dispatch, { type: 'workflow/mark-awaiting-human-review', payload: { updatedAt } }),
      markBddProcessing: (updatedAt) =>
        dispatchWorkflowAction(dispatch, { type: 'workflow/mark-bdd-processing', payload: { updatedAt } }),
      completeWorkflow: (bddAnalysis, updatedAt) =>
        dispatchWorkflowAction(dispatch, { type: 'workflow/complete', payload: { bddAnalysis, updatedAt } }),
      failWorkflow,
      resetWorkflow: () => {
        dispatch({ type: 'workflow/reset' })
        clearWorkflowState()
      },
    }
  }, [state])

  return <WorkflowStateContext.Provider value={value}>{children}</WorkflowStateContext.Provider>
}

export function useWorkflowState(): WorkflowContextValue {
  const context = useContext(WorkflowStateContext)
  if (context === null) {
    throw new Error('useWorkflowState must be used within WorkflowStateProvider')
  }

  return context
}
