import { HttpClient } from '@/shared/api/httpClient'
import type {
  CreateWorkflowRequest,
  CreateWorkflowResponse,
  SubmitApprovedStoryRequest,
  SubmitApprovedStoryResponse,
  WorkflowStatusResponse,
} from '@/shared/types/workflow'

export interface OrchestratorApiConfig {
  baseUrl: string
  timeoutMs: number
}

export class WorkflowOrchestratorApi {
  constructor(private readonly httpClient: HttpClient) {}

  createWorkflow(payload: CreateWorkflowRequest) {
    return this.httpClient.post<CreateWorkflowResponse>('/workflows/stories', payload)
  }

  getWorkflow(workflowId: string) {
    return this.httpClient.get<WorkflowStatusResponse>(`/workflows/${workflowId}`)
  }

  submitApprovedStory(workflowId: string, payload: SubmitApprovedStoryRequest) {
    return this.httpClient.post<SubmitApprovedStoryResponse>(
      `/workflows/${workflowId}/approval`,
      payload,
    )
  }
}

export function createOrchestratorApi(config: OrchestratorApiConfig) {
  return new WorkflowOrchestratorApi(
    new HttpClient({
      baseUrl: config.baseUrl,
      timeoutMs: config.timeoutMs,
      defaultHeaders: {
        'X-Client': 'talp-workflow-orchestrator-ui',
      },
    }),
  )
}
