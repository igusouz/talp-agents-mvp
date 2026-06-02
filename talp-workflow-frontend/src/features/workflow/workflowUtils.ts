import type { BddAnalysis, ComplianceAnalysis, InvestAnalysis, UserStory } from '@/api/models/workflow'
import { ApiError } from '@/api/errors'

export function normalizeText(value: string): string {
  return value.trim().replace(/\r\n/g, '\n')
}

export function splitAcceptanceCriteria(value: string): string[] {
  return value
    .split(/\n+/)
    .map((item) => item.replace(/^[-*]\s*/, '').trim())
    .filter((item) => item.length > 0)
}

export function formatAcceptanceCriteria(criteria: string[]): string {
  return criteria.map((item) => `- ${item}`).join('\n')
}

export function buildUserStoryDraft(params: {
  title: string
  description: string
  acceptanceCriteriaText: string
  additionalContext?: string
}): UserStory {
  return {
    title: normalizeText(params.title),
    description: normalizeText(params.description),
    acceptanceCriteria: splitAcceptanceCriteria(params.acceptanceCriteriaText),
    additionalContext: params.additionalContext ? normalizeText(params.additionalContext) : null,
  }
}

export function userStoryToDraftFields(story: UserStory): {
  title: string
  description: string
  acceptanceCriteriaText: string
  additionalContext: string
} {
  return {
    title: story.title,
    description: story.description,
    acceptanceCriteriaText: formatAcceptanceCriteria(story.acceptanceCriteria),
    additionalContext: story.additionalContext ?? '',
  }
}

export function isUserStoryEmpty(story: UserStory | null | undefined): boolean {
  if (!story) {
    return true
  }

  return (
    normalizeText(story.title).length === 0 ||
    normalizeText(story.description).length === 0 ||
    story.acceptanceCriteria.length === 0
  )
}

export function hasUserStoryChanged(baseStory: UserStory | null | undefined, currentStory: UserStory | null | undefined): boolean {
  if (!baseStory || !currentStory) {
    return false
  }

  return JSON.stringify(baseStory) !== JSON.stringify(currentStory)
}

export function toPrettyJson(value: unknown): string {
  return JSON.stringify(value, null, 2)
}

export function buildBddExportPayload(params: {
  workflowId: string
  originalStory: UserStory | null
  approvedStory: UserStory | null
  investAnalysis: InvestAnalysis | null
  complianceAnalysis: ComplianceAnalysis | null
  bddAnalysis: BddAnalysis
}): Record<string, unknown> {
  return {
    workflowId: params.workflowId,
    originalStory: params.originalStory,
    approvedStory: params.approvedStory,
    investAnalysis: params.investAnalysis,
    complianceAnalysis: params.complianceAnalysis,
    bddAnalysis: params.bddAnalysis,
    exportedAt: new Date().toISOString(),
  }
}

export function downloadJsonFile(filename: string, payload: unknown): void {
  const blob = new Blob([toPrettyJson(payload)], { type: 'application/json;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.rel = 'noreferrer'
  anchor.click()
  window.setTimeout(() => URL.revokeObjectURL(url), 0)
}

export function getApiErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message
  }

  if (error instanceof Error) {
    return error.message
  }

  return 'An unexpected error occurred.'
}

export function isStoryValid(story: UserStory | null | undefined): story is UserStory {
  return !isUserStoryEmpty(story)
}
