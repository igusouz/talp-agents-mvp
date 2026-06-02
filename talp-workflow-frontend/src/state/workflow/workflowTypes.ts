import type {
  BddAnalysis,
  ComplianceAnalysis,
  InvestAnalysis,
  UserStory,
  WorkflowStage,
} from '@/api/models/workflow'

export type WorkflowErrorKind = 'network' | 'timeout' | 'upstream' | 'validation' | 'unexpected'

export interface WorkflowErrorState {
  kind: WorkflowErrorKind
  message: string
  retriable: boolean
  details?: unknown
}

export interface WorkflowProgress {
  stage: WorkflowStage
  label: string
}

export interface WorkflowState {
  workflowId: string | null
  stage: WorkflowStage
  originalStory: UserStory | null
  editedStory: UserStory | null
  approvedStory: UserStory | null
  investAnalysis: InvestAnalysis | null
  complianceAnalysis: ComplianceAnalysis | null
  bddAnalysis: BddAnalysis | null
  isLoading: boolean
  error: WorkflowErrorState | null
  updatedAt: string | null
}

export interface WorkflowContextValue {
  state: WorkflowState
  progress: WorkflowProgress[]
  isActiveWorkflow: boolean
  hydrateWorkflow: (params: {
    workflowId: string
    stage: WorkflowStage
    originalStory: UserStory
    editedStory?: UserStory | null
    approvedStory?: UserStory | null
    investAnalysis?: InvestAnalysis | null
    complianceAnalysis?: ComplianceAnalysis | null
    bddAnalysis?: BddAnalysis | null
    updatedAt?: string | null
  }) => void
  setDraftStory: (story: UserStory) => void
  startWorkflow: (params: {
    workflowId: string
    originalStory: UserStory
    investAnalysis: InvestAnalysis
    complianceAnalysis: ComplianceAnalysis
    updatedAt?: string | null
  }) => void
  approveStory: (approvedStory: UserStory, updatedAt?: string | null) => void
  markInvestAnalysis: (investAnalysis: InvestAnalysis, updatedAt?: string | null) => void
  markComplianceAnalysis: (complianceAnalysis: ComplianceAnalysis, updatedAt?: string | null) => void
  markAwaitingHumanReview: (updatedAt?: string | null) => void
  markBddProcessing: (updatedAt?: string | null) => void
  completeWorkflow: (bddAnalysis: BddAnalysis, updatedAt?: string | null) => void
  failWorkflow: (error: WorkflowErrorState, updatedAt?: string | null) => void
  resetWorkflow: () => void
}
