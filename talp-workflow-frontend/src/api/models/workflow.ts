import type {
  BddAnalysisDto,
  BddScenarioDto,
  ComplianceAnalysisDto,
  ComplianceGapDto,
  ComplianceRequirementDto,
  ComplianceSeverityDto,
  ComplianceStatusDto,
  ComplianceRequirementStatusDto,
  CriterionStatusDto,
  WorkflowStageDto,
} from '@/api/dto/workflow'

import type { ISODateString, UUID } from '@/types/common'

export type WorkflowStage = WorkflowStageDto

export interface UserStory {
  title: string
  description: string
  acceptanceCriteria: string[]
  additionalContext?: string | null
}

export interface WorkflowCreateRequest {
  userStory: UserStory
  metadata?: Record<string, unknown>
}

export interface WorkflowDraft {
  title?: string | null
  storyText: string
  acceptanceCriteria: string[]
  context?: string | null
  metadata?: Record<string, unknown>
}

export interface InvestCriterionAssessment {
  status: CriterionStatusDto | 'pass' | 'fail'
  evidence: string[]
  reason: string
}

export interface InvestAnalysis {
  independent: InvestCriterionAssessment
  negotiable: InvestCriterionAssessment
  valuable: InvestCriterionAssessment
  estimable: InvestCriterionAssessment
  small: InvestCriterionAssessment
  testable: InvestCriterionAssessment
}

export interface ComplianceGap {
  ruleId: string
  ruleName: string
  severity: ComplianceSeverityDto | 'critical' | 'high' | 'medium' | 'low'
  gapDescription: string
  remediationSuggestion?: string | null
  blocking: boolean
}

export interface ComplianceRequirement {
  requirementId: string
  description: string
  status: ComplianceRequirementStatusDto | 'satisfied' | 'gap' | 'pending'
  rulesInvolved: string[]
}

export interface ComplianceAnalysis {
  analysisId: string
  investmentId: string
  status: ComplianceStatusDto | 'compliant' | 'non_compliant' | 'partial'
  detectedRules: Array<Record<string, unknown>>
  complianceGaps: ComplianceGap[]
  requirements: ComplianceRequirement[]
  summary: string
  timestamp?: ISODateString | null
  metadata: Record<string, unknown>
}

export interface BddScenario {
  title: string
  scenarioType: BddScenarioDto['scenario_type']
  given: string[]
  when: string[]
  then: string[]
  notes: string[]
}

export interface BddAnalysis {
  summary: string
  bddScenarios: BddScenario[]
  negativeCases: string[]
  edgeCases: string[]
  ambiguities: string[]
  risks: string[]
  automationSuggestions: string[]
  questionsForRefinement: string[]
}

export interface WorkflowCreateResponse {
  workflowId: UUID
  stage: WorkflowStage
  originalStory: UserStory
  investAnalysis: InvestAnalysis | null
  complianceAnalysis: ComplianceAnalysis | null
  nextAction: 'review'
  correlationId?: string | null
}

export interface WorkflowStateResponse {
  workflowId: UUID
  stage: WorkflowStage
  originalStory: UserStory
  approvedStory?: UserStory | null
  investAnalysis?: InvestAnalysis | null
  complianceAnalysis?: ComplianceAnalysis | null
  bddAnalysis?: BddAnalysis | null
  updatedAt: ISODateString
  correlationId?: string | null
}

export interface ApproveStoryRequest {
  approvedStory: UserStory
  reviewerId?: string | null
  reviewNotes?: string | null
  metadata?: Record<string, unknown>
}

export interface FinalWorkflowResponse {
  workflowId: UUID
  stage: 'bdd_done' | 'completed'
  approvedStory: UserStory
  bddAnalysis: BddAnalysis
  correlationId?: string | null
}
