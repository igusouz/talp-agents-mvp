import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { WorkflowService } from '@/api/workflowService'
import { EmptyState } from '@/components/ui/EmptyState'
import { LoadingState } from '@/components/ui/LoadingState'
import { PageHeader } from '@/components/ui/PageHeader'
import { useWorkflowState } from '@/state/workflow'
import { buildUserStoryDraft, getApiErrorMessage, hasUserStoryChanged, isStoryValid, splitAcceptanceCriteria, userStoryToDraftFields } from '@/features/workflow/workflowUtils'

type StoryFieldErrors = Partial<Record<'title' | 'description' | 'acceptanceCriteriaText', string>>

function toWorkflowError(error: unknown) {
  return {
    kind: 'unexpected' as const,
    message: getApiErrorMessage(error),
    retriable: true,
    details: error,
  }
}

function validateDraft(story: ReturnType<typeof buildUserStoryDraft>) {
  const errors: StoryFieldErrors = {}

  if (story.title.trim().length === 0) {
    errors.title = 'The story title cannot be empty.'
  }

  if (story.description.trim().length === 0) {
    errors.description = 'The story description cannot be empty.'
  }

  if (story.acceptanceCriteria.length === 0) {
    errors.acceptanceCriteriaText = 'Add at least one acceptance criterion.'
  }

  return errors
}

export function HumanReviewPage() {
  const { workflowId } = useParams()
  const navigate = useNavigate()
  const workflow = useWorkflowState()
  const service = useMemo(() => new WorkflowService(), [])

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [acceptanceCriteriaText, setAcceptanceCriteriaText] = useState('')
  const [additionalContext, setAdditionalContext] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [loading, setLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<StoryFieldErrors>({})

  const originalStory = workflow.state.originalStory
  const draftStory = workflow.state.editedStory ?? workflow.state.originalStory
  const approvedStory = workflow.state.approvedStory
  const modified = hasUserStoryChanged(originalStory, draftStory)

  useEffect(() => {
    if (!workflowId) {
      return
    }

    if (workflow.state.workflowId === workflowId && isStoryValid(workflow.state.originalStory)) {
      return
    }

    let active = true
    setLoading(true)

    service
      .retrieveWorkflowState(workflowId)
      .then((response) => {
        if (!active) {
          return
        }

        workflow.hydrateWorkflow({
          workflowId: response.workflowId,
          stage: response.stage,
          originalStory: response.originalStory,
          editedStory: response.approvedStory ?? response.originalStory,
          approvedStory: response.approvedStory ?? null,
          investAnalysis: response.investAnalysis ?? null,
          complianceAnalysis: response.complianceAnalysis ?? null,
          bddAnalysis: response.bddAnalysis ?? null,
          updatedAt: response.updatedAt,
        })

        const sourceStory = response.approvedStory ?? response.originalStory
        const draft = userStoryToDraftFields(sourceStory)
        setTitle(draft.title)
        setDescription(draft.description)
        setAcceptanceCriteriaText(draft.acceptanceCriteriaText)
        setAdditionalContext(draft.additionalContext)
        setFieldErrors({})
        setErrorMessage(null)
      })
      .catch((error) => {
        if (active) {
          setErrorMessage(getApiErrorMessage(error))
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false)
        }
      })

    return () => {
      active = false
    }
  }, [service, workflow, workflowId])

  useEffect(() => {
    if (!draftStory) {
      return
    }

    const draft = userStoryToDraftFields(draftStory)
    setTitle(draft.title)
    setDescription(draft.description)
    setAcceptanceCriteriaText(draft.acceptanceCriteriaText)
    setAdditionalContext(draft.additionalContext)
  }, [draftStory])

  if (loading || !originalStory) {
    return <LoadingState />
  }

  if (!workflowId) {
    return <EmptyState title="Workflow missing" description="The workflow id was not provided in the route." />
  }

  const currentDraft = buildUserStoryDraft({
    title,
    description,
    acceptanceCriteriaText,
    additionalContext,
  })

  const handleFieldChange = (setter: (value: string) => void, value: string) => {
    setter(value)
    workflow.setDraftStory({
      title,
      description,
      acceptanceCriteria: currentDraft.acceptanceCriteria,
      additionalContext,
    })
  }

  const handleRewrite = () => {
    const resetDraft = userStoryToDraftFields(originalStory)
    setTitle(resetDraft.title)
    setDescription(resetDraft.description)
    setAcceptanceCriteriaText(resetDraft.acceptanceCriteriaText)
    setAdditionalContext(resetDraft.additionalContext)
    workflow.setDraftStory(originalStory)
    setFieldErrors({})
    setErrorMessage(null)
    setIsEditing(true)
  }

  const handleApprove = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setErrorMessage(null)

    const nextErrors = validateDraft(currentDraft)
    setFieldErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) {
      return
    }

    if (!workflowId) {
      setErrorMessage('Workflow id is missing.')
      return
    }

    setIsSubmitting(true)
    try {
      workflow.approveStory(currentDraft, new Date().toISOString())
      workflow.markBddProcessing(new Date().toISOString())

      const response = await service.submitApprovedStory(workflowId, {
        approvedStory: currentDraft,
        reviewerId: 'frontend-human-review',
        reviewNotes: modified ? 'Approved after human edits.' : 'Approved without edits.',
        metadata: {
          modified,
        },
      })

      workflow.approveStory(response.approvedStory, new Date().toISOString())
      workflow.completeWorkflow(response.bddAnalysis, new Date().toISOString())
      navigate(`/workflows/${workflowId}/final`, { replace: true })
    } catch (error) {
      workflow.failWorkflow(toWorkflowError(error), new Date().toISOString())
      setErrorMessage(getApiErrorMessage(error))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="workflow-page workflow-page--human-review">
      <PageHeader
        eyebrow="Human Review"
        title="Approve or refine the story"
        description="Compare the original user story against the current draft, make edits, then approve it for BDD generation."
        actions={
          <div className="button-group">
            <button type="button" className="button" onClick={() => setIsEditing(true)}>
              Edit
            </button>
            <button type="button" className="button" onClick={handleRewrite}>
              Rewrite
            </button>
          </div>
        }
      />

      <div className="workflow-review-meta">
        <span className={modified ? 'status-badge status-badge--warning' : 'status-badge status-badge--neutral'}>
          {modified ? 'Modified content' : 'Unmodified content'}
        </span>
        {workflow.state.stage === 'approved' ? (
          <span className="status-badge status-badge--pass">BDD processing</span>
        ) : null}
      </div>

      {errorMessage ? <div className="inline-error" role="alert">{errorMessage}</div> : null}

      <form className="workflow-grid workflow-grid--human-review" onSubmit={handleApprove} noValidate>
        <article className="panel">
          <h3 className="panel__title">Original User Story</h3>
          <p className="panel__text panel__text--strong">{originalStory.title}</p>
          <p className="panel__text">{originalStory.description}</p>
          <ul className="bullet-list">
            {originalStory.acceptanceCriteria.map((criterion) => (
              <li key={criterion}>{criterion}</li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h3 className="panel__title">Current User Story</h3>
          <label className="field">
            <span className="field__label">Title</span>
            <input
              className="field__control"
              type="text"
              value={title}
              onChange={(event) => {
                const next = event.target.value
                setTitle(next)
                workflow.setDraftStory({
                  title: next,
                  description,
                  acceptanceCriteria: splitAcceptanceCriteria(acceptanceCriteriaText),
                  additionalContext: additionalContext.trim().length > 0 ? additionalContext : null,
                })
              }}
              readOnly={!isEditing}
              aria-invalid={Boolean(fieldErrors.title)}
            />
            {fieldErrors.title ? <span className="field__error">{fieldErrors.title}</span> : null}
          </label>

          <label className="field">
            <span className="field__label">Description</span>
            <textarea
              className="field__control field__control--textarea"
              value={description}
              onChange={(event) => {
                const next = event.target.value
                setDescription(next)
                workflow.setDraftStory({
                  title,
                  description: next,
                  acceptanceCriteria: splitAcceptanceCriteria(acceptanceCriteriaText),
                  additionalContext: additionalContext.trim().length > 0 ? additionalContext : null,
                })
              }}
              rows={6}
              readOnly={!isEditing}
              aria-invalid={Boolean(fieldErrors.description)}
            />
            {fieldErrors.description ? <span className="field__error">{fieldErrors.description}</span> : null}
          </label>

          <label className="field">
            <span className="field__label">Acceptance criteria</span>
            <textarea
              className="field__control field__control--textarea field__control--monospace"
              value={acceptanceCriteriaText}
              onChange={(event) => {
                const next = event.target.value
                setAcceptanceCriteriaText(next)
                workflow.setDraftStory({
                  title,
                  description,
                  acceptanceCriteria: splitAcceptanceCriteria(next),
                  additionalContext: additionalContext.trim().length > 0 ? additionalContext : null,
                })
              }}
              rows={8}
              readOnly={!isEditing}
              aria-invalid={Boolean(fieldErrors.acceptanceCriteriaText)}
            />
            <span className="field__hint">One criterion per line.</span>
            {fieldErrors.acceptanceCriteriaText ? (
              <span className="field__error">{fieldErrors.acceptanceCriteriaText}</span>
            ) : null}
          </label>

          <label className="field">
            <span className="field__label">Additional context</span>
            <textarea
              className="field__control field__control--textarea"
              value={additionalContext}
              onChange={(event) => {
                const next = event.target.value
                setAdditionalContext(next)
                workflow.setDraftStory({
                  title,
                  description,
                  acceptanceCriteria: splitAcceptanceCriteria(acceptanceCriteriaText),
                  additionalContext: next.trim().length > 0 ? next : null,
                })
              }}
              rows={4}
              readOnly={!isEditing}
            />
          </label>
        </article>

        <article className="panel panel--summary">
          <h3 className="panel__title">Invest findings</h3>
          <pre className="code-block">{JSON.stringify(workflow.state.investAnalysis, null, 2)}</pre>
          <h3 className="panel__title">Compliance findings</h3>
          <pre className="code-block">{JSON.stringify(workflow.state.complianceAnalysis, null, 2)}</pre>
        </article>

        <div className="workflow-form__actions workflow-form__actions--sticky">
          <button type="submit" className="button button--primary" disabled={isSubmitting}>
            {isSubmitting ? 'Approving...' : 'Approve'}
          </button>
        </div>
      </form>

      {isSubmitting ? <LoadingState /> : null}
    </section>
  )
}