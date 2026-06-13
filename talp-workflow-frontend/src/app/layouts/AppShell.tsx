import { NavLink, Outlet } from 'react-router-dom';

import { appConfig } from '@/config/env';

export function AppShell() {
  return (
    <div className="app-shell">
      <header className="app-shell__header">
        <div>
          <p className="app-shell__eyebrow">Multi-agent platform</p>
          <h1 className="app-shell__title">{appConfig.appName}</h1>
        </div>

        <nav className="app-shell__nav" aria-label="Primary">
          <NavLink to="/stories/new" className={({ isActive }) => (isActive ? 'nav-link nav-link--active' : 'nav-link')}>
            New story
          </NavLink>
        </nav>
      </header>

      <main className="app-shell__content">
        <Outlet />
      </main>
    </div>
  );
}
