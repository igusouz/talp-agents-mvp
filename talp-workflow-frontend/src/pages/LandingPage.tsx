import { Page } from '@/shared/ui/Page'

export function LandingPage() {
  return (
    <Page
      title="Foundation ready"
      subtitle="The multi-agent review experience will be layered on top of this shell."
    >
      <div className="card-grid">
        <article className="card">
          <h2 className="card__title">Routing</h2>
          <p className="card__text">Browser routes are configured for workflow submission, review, and final results.</p>
        </article>
        <article className="card">
          <h2 className="card__title">API layer</h2>
          <p className="card__text">A typed client foundation is ready for the Workflow Orchestrator API.</p>
        </article>
        <article className="card">
          <h2 className="card__title">Architecture</h2>
          <p className="card__text">Presentation, layout, and API concerns are isolated into separate layers.</p>
        </article>
      </div>
    </Page>
  )
}
