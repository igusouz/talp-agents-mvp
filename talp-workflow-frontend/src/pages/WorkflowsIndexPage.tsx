import { Page } from '@/shared/ui/Page'

export function WorkflowsIndexPage() {
  return (
    <Page
      title="Workflows"
      subtitle="This area will host workflow creation and the review workspace."
    >
      <section className="state-panel">
        <h2 className="state-panel__title">Workflow console scaffold</h2>
        <p className="state-panel__description">
          Business pages are intentionally not implemented yet. The routing and shell structure are ready for the
          submission, review, and BDD result flows.
        </p>
      </section>
    </Page>
  )
}
