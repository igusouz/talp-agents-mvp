import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { WorkflowService } from '@/api/workflowService'
import { EmptyState } from '@/components/ui/EmptyState'
import { LoadingState } from '@/components/ui/LoadingState'
import { PageHeader } from '@/components/ui/PageHeader'
import { useWorkflowState } from '@/state/workflow'
import { getApiErrorMessage, isStoryValid } from '@/features/workflow/workflowUtils'

function criterionBadgeClass(status: 'pass' | 'fail') {
  return status === 'pass' ? 'status-badge status-badge--pass' : 'status-badge status-badge--fail'
}

function formatJson(value: unknown) {
  return JSON.stringify(value, null, 2)
}

export function ReviewPlaceholderPage() {
  const { workflowId } = useParams()
  const navigate = useNavigate()
  const workflow = useWorkflowState()
  const service = useMemo(() => new WorkflowService(), [])
  const [isHydrating, setIsHydrating] = useState(false)
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    if (!workflowId) {
      return
    }

    if (workflow.state.workflowId === workflowId && isStoryValid(workflow.state.originalStory)) {
      return
    }

    let active = true
    setIsHydrating(true)

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
        setLoadError(null)
      })
      .catch((error) => {
        if (active) {
          setLoadError(getApiErrorMessage(error))
        }
      })
      .finally(() => {
        if (active) {
          setIsHydrating(false)
        }
      })

    return () => {
      active = false
    }
  }, [service, workflow, workflowId])

  const story = workflow.state.originalStory
  const investAnalysis = workflow.state.investAnalysis
  const complianceAnalysis = workflow.state.complianceAnalysis

  if (isHydrating) {
    return <LoadingState />
  }

  if (!story || !investAnalysis || !complianceAnalysis) {
    return (
      <EmptyState
        title="Analysis not available"
        description={loadError ?? 'The workflow does not yet contain Invest and Compliance results.'}
        action={
          <Link className="button button--primary" to="/stories/new">
            Start a new story
          </Link>
        }
      />
    )
  }

  return (
    <section className="workflow-page workflow-page--review">
      <PageHeader
        eyebrow="Analysis Review"
        title="Invest and Compliance findings"
        description="Review the original user story, the Invest Agent output, and the Compliance Agent findings before human editing."
        actions={
          <button className="button button--primary" type="button" onClick={() => navigate('human')}>
            Open Human Review
          </button>
        }
      />

      {loadError ? <div className="inline-error">{loadError}</div> : null}

      <div className="workflow-grid workflow-grid--analysis">
        <article className="panel">
          <h3 className="panel__title">Original User Story</h3>
          <p className="panel__text panel__text--strong">{story.title}</p>
          <p className="panel__text">{story.description}</p>
          <div className="panel__section">
            <h4 className="panel__subtitle">Acceptance criteria</h4>
            <ul className="bullet-list">
              {story.acceptanceCriteria.map((criterion) => (
                <li key={criterion}>{criterion}</li>
              ))}
            </ul>
          </div>
          {story.additionalContext ? (
            <div className="panel__section">
              <h4 className="panel__subtitle">Additional context</h4>
              <p className="panel__text">{story.additionalContext}</p>
            </div>
          ) : null}
        </article>

        <article className="panel">
          <h3 className="panel__title">Invest Agent findings</h3>
          <div className="analysis-criteria">
            {(['independent', 'negotiable', 'valuable', 'estimable', 'small', 'testable'] as const).map((criterion) => {
              const assessment = investAnalysis[criterion]
              return (
                <section className="criterion-card" key={criterion}>
                  <div className="criterion-card__header">
                    <h4 className="criterion-card__title">{criterion}</h4>
                    <span className={criterionBadgeClass(assessment.status)}>{assessment.status}</span>
                  </div>
                  <p className="panel__text">{assessment.reason}</p>
                  {assessment.evidence.length > 0 ? (
                    <ul className="bullet-list bullet-list--compact">
                      {assessment.evidence.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  ) : null}
                </section>
              )
            })}
          </div>
        </article>

        <article className="panel">
          <h3 className="panel__title">Compliance Agent findings</h3>
          <p className="panel__text">{complianceAnalysis.summary}</p>

          <div className="panel__section">
            <h4 className="panel__subtitle">Gaps</h4>
            {complianceAnalysis.complianceGaps.length > 0 ? (
              <div className="stack-list">
                {complianceAnalysis.complianceGaps.map((gap) => (
                  <section className="stack-card" key={`${gap.ruleId}-${gap.ruleName}`}>
                    <div className="criterion-card__header">
                      <h5 className="stack-card__title">{gap.ruleName}</h5>
                      <span className={`status-badge status-badge--${gap.severity}`}>{gap.severity}</span>
                    </div>
                    <p className="panel__text">{gap.gapDescription}</p>
                    {gap.remediationSuggestion ? <p className="panel__text">{gap.remediationSuggestion}</p> : null}
                  </section>
                ))}
              </div>
            ) : (
              <p className="panel__text">No compliance gaps were identified.</p>
            )}
          </div>

          <div className="panel__section">
            <h4 className="panel__subtitle">Requirements</h4>
            <ul className="bullet-list">
              {complianceAnalysis.requirements.map((requirement) => (
                <li key={requirement.requirementId}>
                  <strong>{requirement.status}:</strong> {requirement.description}
                </li>
              ))}
            </ul>
          </div>

          <details className="details-block">
            <summary>Raw compliance payload</summary>
            <pre className="code-block">{formatJson(complianceAnalysis)}</pre>
          </details>
        </article>
      </div>
    </section>
  )
}
