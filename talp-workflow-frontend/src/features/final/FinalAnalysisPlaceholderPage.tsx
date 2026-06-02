import { useEffect, useMemo, useState } from 'react'

import { WorkflowService } from '@/api/workflowService'
import { EmptyState } from '@/components/ui/EmptyState'
import { LoadingState } from '@/components/ui/LoadingState'
import { PageHeader } from '@/components/ui/PageHeader'
import { useWorkflowState } from '@/state/workflow'
import { buildBddExportPayload, downloadJsonFile, getApiErrorMessage, isStoryValid, toPrettyJson } from '@/features/workflow/workflowUtils'

export function FinalAnalysisPlaceholderPage() {
  const workflow = useWorkflowState()
  const service = useMemo(() => new WorkflowService(), [])
  const [isLoading, setIsLoading] = useState(false)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [copyStatus, setCopyStatus] = useState<'idle' | 'copied'>('idle')

  useEffect(() => {
    if (!workflow.state.workflowId) {
      return
    }

    if (workflow.state.bddAnalysis || !isStoryValid(workflow.state.originalStory)) {
      return
    }

    let active = true
    setIsLoading(true)

    service
      .retrieveWorkflowState(workflow.state.workflowId)
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

        if (!response.bddAnalysis) {
          return service.retrieveBddResults(response.workflowId).then((bddAnalysis) => {
            workflow.completeWorkflow(bddAnalysis, new Date().toISOString())
          })
        }

        setLoadError(null)
      })
      .catch((error) => {
        if (active) {
          setLoadError(getApiErrorMessage(error))
        }
      })
      .finally(() => {
        if (active) {
          setIsLoading(false)
        }
      })

    return () => {
      active = false
    }
  }, [service, workflow])

  const bddAnalysis = workflow.state.bddAnalysis
  const exportPayload = useMemo(
    () =>
      workflow.state.workflowId && bddAnalysis
        ? buildBddExportPayload({
            workflowId: workflow.state.workflowId,
            originalStory: workflow.state.originalStory,
            approvedStory: workflow.state.approvedStory,
            investAnalysis: workflow.state.investAnalysis,
            complianceAnalysis: workflow.state.complianceAnalysis,
            bddAnalysis,
          })
        : null,
    [bddAnalysis, workflow.state.approvedStory, workflow.state.complianceAnalysis, workflow.state.investAnalysis, workflow.state.originalStory, workflow.state.workflowId],
  )

  const handleCopy = async () => {
    if (!exportPayload) {
      return
    }

    await navigator.clipboard.writeText(toPrettyJson(exportPayload))
    setCopyStatus('copied')
    window.setTimeout(() => setCopyStatus('idle'), 1500)
  }

  const handleExport = () => {
    if (!exportPayload || !workflow.state.workflowId) {
      return
    }

    downloadJsonFile(`workflow-${workflow.state.workflowId}-bdd-results.json`, exportPayload)
  }

  if (isLoading) {
    return <LoadingState />
  }

  if (!bddAnalysis || !workflow.state.workflowId) {
    return <EmptyState title="BDD analysis unavailable" description={loadError ?? 'No BDD output is available for the current workflow.'} />
  }

  return (
    <section className="workflow-page workflow-page--bdd-results">
      <PageHeader
        eyebrow="BDD Results"
        title="Final analysis"
        description="Review the generated BDD scenarios, risks, and refinement questions after approval."
        actions={
          <div className="button-group">
            <button className="button" type="button" onClick={handleCopy}>
              {copyStatus === 'copied' ? 'Copied' : 'Copy to clipboard'}
            </button>
            <button className="button button--primary" type="button" onClick={handleExport}>
              Export JSON
            </button>
          </div>
        }
      />

      {loadError ? <div className="inline-error" role="alert">{loadError}</div> : null}

      <div className="workflow-grid workflow-grid--results">
        <article className="panel panel--full">
          <h3 className="panel__title">Summary</h3>
          <p className="panel__text">{bddAnalysis.summary}</p>
        </article>

        <article className="panel panel--full">
          <h3 className="panel__title">BDD Scenarios</h3>
          <div className="stack-list">
            {bddAnalysis.bddScenarios.map((scenario) => (
              <section className="stack-card" key={scenario.title}>
                <div className="criterion-card__header">
                  <h4 className="stack-card__title">{scenario.title}</h4>
                  <span className="status-badge status-badge--neutral">{scenario.scenarioType}</span>
                </div>
                <div className="scenario-columns">
                  <div>
                    <p className="panel__text panel__text--label">Given</p>
                    <ul className="bullet-list bullet-list--compact">
                      {scenario.given.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <p className="panel__text panel__text--label">When</p>
                    <ul className="bullet-list bullet-list--compact">
                      {scenario.when.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <p className="panel__text panel__text--label">Then</p>
                    <ul className="bullet-list bullet-list--compact">
                      {scenario.then.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </section>
            ))}
          </div>
        </article>

        <article className="panel">
          <h3 className="panel__title">Negative Cases</h3>
          <ul className="bullet-list">
            {bddAnalysis.negativeCases.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h3 className="panel__title">Edge Cases</h3>
          <ul className="bullet-list">
            {bddAnalysis.edgeCases.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h3 className="panel__title">Risks</h3>
          <ul className="bullet-list">
            {bddAnalysis.risks.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h3 className="panel__title">Automation Suggestions</h3>
          <ul className="bullet-list">
            {bddAnalysis.automationSuggestions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>

        <article className="panel panel--full">
          <h3 className="panel__title">Questions for Refinement</h3>
          <ul className="bullet-list">
            {bddAnalysis.questionsForRefinement.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </div>
    </section>
  )
}
