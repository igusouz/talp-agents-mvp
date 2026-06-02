import { Page } from '@/shared/ui/Page'

export function WorkflowReviewPage() {
  return (
    <Page
      title="Review workspace"
      subtitle="The human review interface will render original story, analyses, and editing tools here."
    >
      <section className="state-panel">
        <h2 className="state-panel__title">Coming soon</h2>
        <p className="state-panel__description">
          This route is reserved for the Human-in-the-Loop editing and approval experience.
        </p>
      </section>
    </Page>
  )
}
