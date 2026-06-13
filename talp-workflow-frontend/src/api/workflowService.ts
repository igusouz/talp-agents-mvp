import { createApiClient } from '@/api/client'
import type {
  ApprovedStoryRequestDto,
  BddAnalysisDto,
  BddScenarioDto,
  ComplianceAnalysisDto,
  ComplianceGapDto,
  ComplianceRequirementDto,
  FinalWorkflowResponseDto,
  InvestAnalysisDto,
  InvestCriterionAssessmentDto,
  UserStoryInputDto,
  WorkflowCreateRequestDto,
  WorkflowCreateResponseDto,
  WorkflowDraftDto,
  WorkflowStateResponseDto,
} from '@/api/dto/workflow'
import { normalizeApiError } from '@/api/errors'
import type {
  ApproveStoryRequest,
  BddAnalysis,
  BddScenario,
  ComplianceAnalysis,
  ComplianceGap,
  ComplianceRequirement,
  InvestAnalysis,
  InvestCriterionAssessment,
  UserStory,
  WorkflowCreateRequest,
  WorkflowCreateResponse,
  WorkflowDraft,
  WorkflowStateResponse,
  FinalWorkflowResponse,
} from '@/api/models/workflow'

const WORKFLOW_BASE_PATH = '/workflows'

function mapWorkflowStage(stage: WorkflowCreateResponseDto['stage'] | WorkflowStateResponseDto['stage']): WorkflowStateResponse['stage'] {
  return stage
}

function toUserStory(dto: UserStoryInputDto): UserStory {
  return {
    title: dto.title,
    description: dto.description,
    acceptanceCriteria: dto.acceptance_criteria,
    additionalContext: dto.additional_context ?? null,
  }
}

function toUserStoryDto(model: UserStory): UserStoryInputDto {
  return {
    title: model.title,
    description: model.description,
    acceptance_criteria: model.acceptanceCriteria,
    additional_context: model.additionalContext ?? null,
  }
}

function toWorkflowDraftDto(model: WorkflowDraft): WorkflowDraftDto {
  return {
    title: model.title ?? null,
    story_text: model.storyText,
    acceptance_criteria: model.acceptanceCriteria,
    context: model.context ?? null,
    metadata: model.metadata ?? {},
  }
}

function toInvestCriterion(model: InvestCriterionAssessmentDto): InvestCriterionAssessment {
  return {
    status: model.status,
    evidence: model.evidence,
    reason: model.reason,
  }
}

function toInvestAnalysis(model: InvestAnalysisDto): InvestAnalysis {
  return {
    independent: toInvestCriterion(model.independent),
    negotiable: toInvestCriterion(model.negotiable),
    valuable: toInvestCriterion(model.valuable),
    estimable: toInvestCriterion(model.estimable),
    small: toInvestCriterion(model.small),
    testable: toInvestCriterion(model.testable),
  }
}

function toComplianceGap(model: ComplianceGapDto): ComplianceGap {
  return {
    ruleId: model.rule_id,
    ruleName: model.rule_name,
    severity: model.severity,
    gapDescription: model.gap_description,
    remediationSuggestion: model.remediation_suggestion ?? null,
    blocking: model.blocking,
  }
}

function toComplianceRequirement(model: ComplianceRequirementDto): ComplianceRequirement {
  return {
    requirementId: model.requirement_id,
    description: model.description,
    status: model.status,
    rulesInvolved: model.rules_involved,
  }
}

function toComplianceAnalysis(model: ComplianceAnalysisDto): ComplianceAnalysis {
  return {
    analysisId: model.analysis_id,
    investmentId: model.investment_id,
    status: model.status,
    detectedRules: model.detected_rules,
    complianceGaps: model.compliance_gaps.map(toComplianceGap),
    requirements: model.requirements.map(toComplianceRequirement),
    summary: model.summary,
    timestamp: model.timestamp ?? null,
    metadata: model.metadata ?? {},
  }
}

function toBddScenario(model: BddScenarioDto): BddScenario {
  return {
    title: model.title,
    scenarioType: model.scenario_type,
    given: model.given,
    when: model.when,
    then: model.then,
    notes: model.notes,
  }
}

function toBddAnalysis(model: BddAnalysisDto): BddAnalysis {
  return {
    summary: model.summary,
    bddScenarios: model.bdd_scenarios.map(toBddScenario),
    negativeCases: model.negative_cases,
    edgeCases: model.edge_cases,
    ambiguities: model.ambiguities,
    risks: model.risks,
    automationSuggestions: model.automation_suggestions,
    questionsForRefinement: model.questions_for_refinement,
  }
}

function mapWorkflowCreateResponse(model: WorkflowCreateResponseDto): WorkflowCreateResponse {
  return {
    workflowId: model.workflow_id,
    stage: mapWorkflowStage(model.stage),
    originalStory: toUserStory(model.original_story),
    investAnalysis: model.invest_analysis ? toInvestAnalysis(model.invest_analysis) : null,
    complianceAnalysis: model.compliance_analysis ? toComplianceAnalysis(model.compliance_analysis) : null,
    nextAction: model.next_action,
    correlationId: model.correlation_id ?? null,
  }
}

function mapWorkflowStateResponse(model: WorkflowStateResponseDto): WorkflowStateResponse {
  return {
    workflowId: model.workflow_id,
    stage: mapWorkflowStage(model.stage),
    originalStory: toUserStory(model.original_story),
    approvedStory: model.approved_story ? toUserStory(model.approved_story) : null,
    investAnalysis: model.invest_analysis ? toInvestAnalysis(model.invest_analysis) : null,
    complianceAnalysis: model.compliance_analysis ? toComplianceAnalysis(model.compliance_analysis) : null,
    bddAnalysis: model.bdd_analysis ? toBddAnalysis(model.bdd_analysis) : null,
    updatedAt: model.updated_at,
    correlationId: model.correlation_id ?? null,
  }
}

function mapFinalWorkflowResponse(model: FinalWorkflowResponseDto): FinalWorkflowResponse {
  return {
    workflowId: model.workflow_id,
    stage: model.stage,
    approvedStory: toUserStory(model.approved_story),
    bddAnalysis: toBddAnalysis(model.bdd_analysis),
    correlationId: model.correlation_id ?? null,
  }
}

export class WorkflowService {
  constructor(private readonly apiClient = createApiClient()) {}

  async startWorkflow(request: WorkflowCreateRequest): Promise<WorkflowCreateResponse> {
    try {
      const response = await this.apiClient.request<WorkflowCreateResponseDto>(WORKFLOW_BASE_PATH, {
        method: 'POST',
        body: this.toCreateRequestDto(request),
      })

      return mapWorkflowCreateResponse(response)
    } catch (error) {
      throw normalizeApiError(error)
    }
  }

  async retrieveWorkflowState(workflowId: string): Promise<WorkflowStateResponse> {
    try {
      const response = await this.apiClient.request<WorkflowStateResponseDto>(`${WORKFLOW_BASE_PATH}/${workflowId}`)
      return mapWorkflowStateResponse(response)
    } catch (error) {
      throw normalizeApiError(error)
    }
  }

  async submitApprovedStory(workflowId: string, request: ApproveStoryRequest): Promise<FinalWorkflowResponse> {
    try {
      const response = await this.apiClient.request<FinalWorkflowResponseDto>(`${WORKFLOW_BASE_PATH}/${workflowId}/approval`, {
        method: 'POST',
        body: {
          approved_story: toUserStoryDto(request.approvedStory),
          reviewer_id: request.reviewerId ?? null,
          review_notes: request.reviewNotes ?? null,
          metadata: request.metadata ?? {},
        } satisfies ApprovedStoryRequestDto,
      })

      return mapFinalWorkflowResponse(response)
    } catch (error) {
      throw normalizeApiError(error)
    }
  }

  async retrieveBddResults(workflowId: string): Promise<BddAnalysis> {
    try {
      const response = await this.apiClient.request<{ bdd_analysis: BddAnalysisDto }>(`${WORKFLOW_BASE_PATH}/${workflowId}/bdd-results`)
      return toBddAnalysis(response.bdd_analysis)
    } catch (error) {
      throw normalizeApiError(error)
    }
  }

  private toCreateRequestDto(request: WorkflowCreateRequest): WorkflowCreateRequestDto {
    return {
      user_story: {
        title: request.userStory.title,
        description: request.userStory.description,
        acceptance_criteria: request.userStory.acceptanceCriteria,
        additional_context: request.userStory.additionalContext ?? null,
      },
      metadata: request.metadata ?? {},
    }
  }
}
