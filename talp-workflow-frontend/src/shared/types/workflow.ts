import type { BddAnalysis, ComplianceAnalysis, InvestAnalysis } from '@/shared/types/analysis'
import type { CorrelationId, TimestampedEntity, WorkflowId, WorkflowStage } from '@/shared/types/common'

export interface UserStoryDraft {
  title?: string
  storyText: string
  acceptanceCriteria: string[]
  context?: string
  metadata?: Record<string, unknown>
}

export interface WorkflowStorySnapshot extends TimestampedEntity {
  title?: string
  storyText: string
  acceptanceCriteria: string[]
  context?: string
  metadata: Record<string, unknown>
}

export interface CreateWorkflowRequest {
  userStoryText: string
  title?: string
  acceptanceCriteria?: string[]
  context?: string
  metadata?: Record<string, unknown>
  correlationId?: CorrelationId
}

export interface CreateWorkflowResponse {
  workflowId: WorkflowId
  stage: WorkflowStage
  originalStory: WorkflowStorySnapshot
  investAnalysis: InvestAnalysis
  complianceAnalysis: ComplianceAnalysis
  nextAction: 'review' | 'awaiting_review'
}

export interface WorkflowStatusResponse {
  workflowId: WorkflowId
  stage: WorkflowStage
  originalStory: WorkflowStorySnapshot
  approvedStory?: WorkflowStorySnapshot | null
  investAnalysis: InvestAnalysis
  complianceAnalysis: ComplianceAnalysis
  bddAnalysis?: BddAnalysis | null
}

export interface SubmitApprovedStoryRequest {
  approvedStoryText: string
  title?: string
  acceptanceCriteria?: string[]
  reviewerId?: string
  reviewNotes?: string
  metadata?: Record<string, unknown>
  correlationId?: CorrelationId
}

export interface SubmitApprovedStoryResponse {
  workflowId: WorkflowId
  stage: WorkflowStage
  approvedStory: WorkflowStorySnapshot
  bddAnalysis: BddAnalysis
}
