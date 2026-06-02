import { Page } from '@/shared/ui/Page'

export function WorkflowFinalPage() {
  return (
    <Page
      title="BDD results"
      subtitle="Final analysis will appear here after the approved story is processed by the orchestrator."
    >
      <section className="state-panel">
        <h2 className="state-panel__title">Final analysis placeholder</h2>
        <p className="state-panel__description">
          This page is reserved for the post-approval BDD analysis and generated scenarios.
        </p>
      </section>
    </Page>
  )
}
