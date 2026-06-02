export type WorkflowStageDto =
  | 'received'
  | 'invest_done'
  | 'compliance_done'
  | 'waiting_for_review'
  | 'approved'
  | 'bdd_done'
  | 'completed'
  | 'failed'

export type CriterionStatusDto = 'pass' | 'fail'
export type ComplianceStatusDto = 'compliant' | 'non_compliant' | 'partial'
export type ComplianceSeverityDto = 'critical' | 'high' | 'medium' | 'low'
export type ComplianceRequirementStatusDto = 'satisfied' | 'gap' | 'pending'
export type BddScenarioTypeDto = 'positive' | 'negative' | 'edge'

export interface UserStoryInputDto {
  title: string
  description: string
  acceptance_criteria: string[]
  additional_context?: string | null
}

export interface WorkflowCreateRequestDto {
  user_story: UserStoryInputDto
  metadata?: Record<string, unknown>
}

export interface WorkflowDraftDto {
  title?: string | null
  story_text: string
  acceptance_criteria: string[]
  context?: string | null
  metadata?: Record<string, unknown>
}

export interface InvestCriterionAssessmentDto {
  status: CriterionStatusDto
  evidence: string[]
  reason: string
}

export interface InvestAnalysisDto {
  independent: InvestCriterionAssessmentDto
  negotiable: InvestCriterionAssessmentDto
  valuable: InvestCriterionAssessmentDto
  estimable: InvestCriterionAssessmentDto
  small: InvestCriterionAssessmentDto
  testable: InvestCriterionAssessmentDto
}

export interface ComplianceGapDto {
  rule_id: string
  rule_name: string
  severity: ComplianceSeverityDto
  gap_description: string
  remediation_suggestion?: string | null
  blocking: boolean
}

export interface ComplianceRequirementDto {
  requirement_id: string
  description: string
  status: ComplianceRequirementStatusDto
  rules_involved: string[]
}

export interface ComplianceAnalysisDto {
  analysis_id: string
  investment_id: string
  status: ComplianceStatusDto
  detected_rules: Array<Record<string, unknown>>
  compliance_gaps: ComplianceGapDto[]
  requirements: ComplianceRequirementDto[]
  summary: string
  timestamp?: string | null
  metadata?: Record<string, unknown>
}

export interface BddScenarioDto {
  title: string
  scenario_type: BddScenarioTypeDto
  given: string[]
  when: string[]
  then: string[]
  notes: string[]
}

export interface BddAnalysisDto {
  summary: string
  bdd_scenarios: BddScenarioDto[]
  negative_cases: string[]
  edge_cases: string[]
  ambiguities: string[]
  risks: string[]
  automation_suggestions: string[]
  questions_for_refinement: string[]
}

export interface WorkflowCreateResponseDto {
  workflow_id: string
  stage: WorkflowStageDto
  original_story: UserStoryInputDto
  invest_analysis: InvestAnalysisDto
  compliance_analysis: ComplianceAnalysisDto
  next_action: 'review'
  correlation_id?: string | null
}

export interface WorkflowStateResponseDto {
  workflow_id: string
  stage: WorkflowStageDto
  original_story: UserStoryInputDto
  approved_story?: UserStoryInputDto | null
  invest_analysis?: InvestAnalysisDto | null
  compliance_analysis?: ComplianceAnalysisDto | null
  bdd_analysis?: BddAnalysisDto | null
  updated_at: string
  correlation_id?: string | null
}

export interface ApprovedStoryRequestDto {
  approved_story: UserStoryInputDto
  reviewer_id?: string | null
  review_notes?: string | null
  metadata?: Record<string, unknown>
}

export interface FinalWorkflowResponseDto {
  workflow_id: string
  stage: 'bdd_done' | 'completed'
  approved_story: UserStoryInputDto
  bdd_analysis: BddAnalysisDto
  correlation_id?: string | null
}
