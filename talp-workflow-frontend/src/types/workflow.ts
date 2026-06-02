import type { ISODateString, UUID } from './common';

export type WorkflowStage =
  | 'draft'
  | 'invest_completed'
  | 'compliance_completed'
  | 'awaiting_review'
  | 'approved'
  | 'bdd_completed'
  | 'failed';

export interface UserStoryInput {
  title: string;
  description: string;
  acceptanceCriteria: string[];
  additionalContext?: string;
}

export interface WorkflowSummary {
  workflowId: UUID;
  stage: WorkflowStage;
  title: string;
  updatedAt: ISODateString;
}

export interface ReviewDraft {
  workflowId: UUID;
  approvedStory: UserStoryInput;
  reviewerId?: string;
  reviewNotes?: string;
}
