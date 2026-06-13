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
