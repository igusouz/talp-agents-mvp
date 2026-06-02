import type { TimestampedEntity } from '@/shared/types/common'

export type CriterionStatus = 'pass' | 'fail'
export type ComplianceSeverity = 'critical' | 'high' | 'medium' | 'low'
export type ComplianceRequirementStatus = 'satisfied' | 'gap' | 'pending'
export type BddScenarioType = 'positive' | 'negative' | 'edge'
export type BddAnalysisStatus = 'compliant' | 'non_compliant' | 'partial'

export interface CriterionAssessment {
  status: CriterionStatus
  evidence: string[]
  reason: string
}

export interface InvestAnalysis {
  independent: CriterionAssessment
  negotiable: CriterionAssessment
  valuable: CriterionAssessment
  estimable: CriterionAssessment
  small: CriterionAssessment
  testable: CriterionAssessment
}

export interface InvestCriterionResult {
  criterionId: string
  criterionName: string
  result: boolean
  evidence?: string | null
}

export interface InvestResult extends TimestampedEntity {
  investmentId: string
  status: string
  criteriaResults: InvestCriterionResult[]
  summary: string
  metadata: Record<string, unknown>
}

export interface DetectedRule {
  ruleId: string
  name: string
  domain: string
  matched: boolean
  confidence: number
  evidenceFound: string[]
  dependencies: RuleDependency[]
}

export interface RuleDependency {
  ruleId: string
  dependsOn: string[]
  description?: string | null
}

export interface ComplianceGap {
  ruleId: string
  ruleName: string
  severity: ComplianceSeverity
  gapDescription: string
  remediationSuggestion?: string | null
  blocking: boolean
}

export interface ComplianceRequirement {
  requirementId: string
  description: string
  status: ComplianceRequirementStatus
  rulesInvolved: string[]
}

export interface ComplianceAnalysis extends TimestampedEntity {
  analysisId: string
  investmentId: string
  status: BddAnalysisStatus
  detectedRules: DetectedRule[]
  complianceGaps: ComplianceGap[]
  requirements: ComplianceRequirement[]
  summary: string
  metadata: Record<string, unknown>
}

export type ScenarioType = BddScenarioType

export interface BddScenario {
  title: string
  scenarioType: ScenarioType
  given: string[]
  when: string[]
  then: string[]
  notes: string[]
  gherkin: string
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
