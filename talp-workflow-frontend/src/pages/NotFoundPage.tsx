import { EmptyState } from '@/components/ui/EmptyState';
import { PageHeader } from '@/components/ui/PageHeader';

export function NotFoundPage() {
  return (
    <div className="not-found-page">
      <PageHeader eyebrow="404" title="Page not found" description="The requested route does not exist." />
      <EmptyState title="Nothing here" description="Use the navigation to return to the workflow shell." />
    </div>
  );
}
import { Link } from 'react-router-dom'

import { Page } from '@/shared/ui/Page'

export function NotFoundPage() {
  return (
    <Page title="Page not found" subtitle="The requested route does not exist.">
      <section className="state-panel">
        <p className="state-panel__description">Return to the workflow console to continue.</p>
        <Link className="button button--primary" to="/workflows">
          Go to workflows
        </Link>
      </section>
    </Page>
  )
}
