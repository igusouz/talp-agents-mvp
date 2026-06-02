import { NavLink, Outlet, useParams } from 'react-router-dom';

import { PageHeader } from '@/components/ui/PageHeader';

export function WorkflowShell() {
  const { workflowId } = useParams();

  return (
    <section className="workflow-shell">
      <PageHeader
        eyebrow="Workflow"
        title={workflowId ?? 'Unknown workflow'}
        description="Review state, analysis snapshots, and final BDD output are organized within this route group."
      />

      <div className="workflow-shell__tabs" role="tablist" aria-label="Workflow stages">
        <NavLink to="review" className={({ isActive }) => (isActive ? 'tab-link tab-link--active' : 'tab-link')}>
          Review
        </NavLink>
          <NavLink
            to="review/human"
            className={({ isActive }) => (isActive ? 'tab-link tab-link--active' : 'tab-link')}
          >
            Human Review
          </NavLink>
        <NavLink to="final" className={({ isActive }) => (isActive ? 'tab-link tab-link--active' : 'tab-link')}>
          Final analysis
        </NavLink>
      </div>

      <div className="workflow-shell__panel">
        <Outlet />
      </div>
    </section>
  );
}
import { NavLink, Outlet, useParams } from 'react-router-dom'

const stepLinkClassName = ({ isActive }: { isActive: boolean }) =>
  isActive ? 'step-link step-link--active' : 'step-link'

export function WorkflowShell() {
  const { workflowId } = useParams()

  return (
    <section className="workflow-shell">
      <header className="workflow-shell__header">
        <div>
          <p className="workflow-shell__eyebrow">Workflow</p>
          <h2 className="workflow-shell__title">{workflowId ?? 'Untitled workflow'}</h2>
        </div>

        <nav className="workflow-shell__steps" aria-label="Workflow steps">
          <NavLink className={stepLinkClassName} to="review">
            Review
          </NavLink>
          <NavLink className={stepLinkClassName} to="final">
            Final Result
          </NavLink>
        </nav>
      </header>

      <div className="workflow-shell__content">
        <Outlet />
      </div>
    </section>
  )
}
