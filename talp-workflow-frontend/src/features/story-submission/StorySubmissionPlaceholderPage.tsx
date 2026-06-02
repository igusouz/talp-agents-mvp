import { useMemo, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'

import { PageHeader } from '@/components/ui/PageHeader'
import { LoadingState } from '@/components/ui/LoadingState'
import { useWorkflowState } from '@/state/workflow'
import { WorkflowService } from '@/api/workflowService'
import { buildUserStoryDraft, getApiErrorMessage, splitAcceptanceCriteria } from '@/features/workflow/workflowUtils'

type FormErrors = Partial<Record<'title' | 'description' | 'acceptanceCriteriaText', string>>

function mapToWorkflowError(error: unknown) {
  return {
    kind: 'unexpected' as const,
    message: getApiErrorMessage(error),
    retriable: true,
    details: error,
  }
}

export function StorySubmissionPlaceholderPage() {
  const navigate = useNavigate()
  const workflow = useWorkflowState()
  const service = useMemo(() => new WorkflowService(), [])

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [acceptanceCriteriaText, setAcceptanceCriteriaText] = useState('')
  const [additionalContext, setAdditionalContext] = useState('')
  const [errors, setErrors] = useState<FormErrors>({})
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const acceptanceCriteriaCount = splitAcceptanceCriteria(acceptanceCriteriaText).length

  const validate = () => {
    const nextErrors: FormErrors = {}

    if (title.trim().length === 0) {
      nextErrors.title = 'A story title is required.'
    }

    if (description.trim().length === 0) {
      nextErrors.description = 'A story description is required.'
    }

    if (acceptanceCriteriaCount === 0) {
      nextErrors.acceptanceCriteriaText = 'Add at least one acceptance criterion, one per line.'
    }

    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitError(null)

    if (!validate()) {
      return
    }

    const userStory = buildUserStoryDraft({
      title,
      description,
      acceptanceCriteriaText,
      additionalContext,
    })

    setIsSubmitting(true)
    try {
      const response = await service.startWorkflow({
        userStory,
        metadata: {
          source: 'frontend',
        },
      })

      workflow.startWorkflow({
        workflowId: response.workflowId,
        originalStory: response.originalStory,
        investAnalysis: response.investAnalysis,
        complianceAnalysis: response.complianceAnalysis,
        updatedAt: new Date().toISOString(),
      })

      navigate(`/workflows/${response.workflowId}/review`, { replace: true })
    } catch (error) {
      setSubmitError(getApiErrorMessage(error))
      workflow.failWorkflow(mapToWorkflowError(error), new Date().toISOString())
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="workflow-page workflow-page--submission">
      <PageHeader
        eyebrow="Submission"
        title="User Story Submission"
        description="Submit a user story to start the Invest and Compliance analysis flow."
      />

      <div className="workflow-layout workflow-layout--single">
        <form className="workflow-form" onSubmit={handleSubmit} noValidate>
          <div className="workflow-form__grid">
            <label className="field">
              <span className="field__label">Story title</span>
              <input
                className="field__control"
                type="text"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="As a customer, I want..."
                aria-invalid={Boolean(errors.title)}
              />
              {errors.title ? <span className="field__error">{errors.title}</span> : null}
            </label>

            <label className="field field--full">
              <span className="field__label">Story description</span>
              <textarea
                className="field__control field__control--textarea"
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                placeholder="Describe the user need, intent, and business value."
                rows={6}
                aria-invalid={Boolean(errors.description)}
              />
              {errors.description ? <span className="field__error">{errors.description}</span> : null}
            </label>

            <label className="field field--full">
              <span className="field__label">Acceptance criteria</span>
              <textarea
                className="field__control field__control--textarea field__control--monospace"
                value={acceptanceCriteriaText}
                onChange={(event) => setAcceptanceCriteriaText(event.target.value)}
                placeholder="- Criterion 1\n- Criterion 2\n- Criterion 3"
                rows={8}
                aria-invalid={Boolean(errors.acceptanceCriteriaText)}
              />
              <span className="field__hint">Write one criterion per line.</span>
              {errors.acceptanceCriteriaText ? (
                <span className="field__error">{errors.acceptanceCriteriaText}</span>
              ) : (
                <span className="field__hint">{acceptanceCriteriaCount} criterion(s) detected.</span>
              )}
            </label>

            <label className="field field--full">
              <span className="field__label">Additional context</span>
              <textarea
                className="field__control field__control--textarea"
                value={additionalContext}
                onChange={(event) => setAdditionalContext(event.target.value)}
                placeholder="Optional notes, constraints, or domain context."
                rows={4}
              />
            </label>
          </div>

          {submitError ? (
            <div className="inline-error" role="alert">
              {submitError}
            </div>
          ) : null}

          <div className="workflow-form__actions">
            <button className="button button--primary" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Submitting...' : 'Start workflow'}
            </button>
          </div>
        </form>

        {isSubmitting ? <LoadingState /> : null}
      </div>
    </section>
  )
}
