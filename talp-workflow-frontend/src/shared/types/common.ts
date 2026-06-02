export type Brand<T, B extends string> = T & { readonly __brand: B }

export type WorkflowId = Brand<string, 'WorkflowId'>
export type CorrelationId = Brand<string, 'CorrelationId'>
export type RequestId = Brand<string, 'RequestId'>

export type WorkflowStage =
  | 'received'
  | 'invest_done'
  | 'compliance_done'
  | 'waiting_for_review'
  | 'approved'
  | 'bdd_done'
  | 'completed'
  | 'failed'

export interface TimestampedEntity {
  createdAt?: string
  updatedAt?: string
}

export interface ApiEnvelope<T> {
  data: T
  correlationId?: CorrelationId
}
