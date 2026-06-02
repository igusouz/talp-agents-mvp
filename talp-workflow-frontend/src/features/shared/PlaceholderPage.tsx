import { EmptyState } from '@/components/ui/EmptyState';
import { PageHeader } from '@/components/ui/PageHeader';

type PlaceholderPageProps = {
  eyebrow: string;
  title: string;
  description: string;
};

export function PlaceholderPage({ eyebrow, title, description }: PlaceholderPageProps) {
  return (
    <div className="placeholder-page">
      <PageHeader eyebrow={eyebrow} title={title} description={description} />
      <EmptyState
        title="Foundation ready"
        description="This route is reserved for the next implementation slice and already has the surrounding shell, routing, and type contracts in place."
      />
    </div>
  );
}
