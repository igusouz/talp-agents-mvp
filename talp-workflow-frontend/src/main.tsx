import React from 'react';
import ReactDOM from 'react-dom/client';

import { App } from '@/app/App';
import '@/styles/global.css';

const rootElement = document.getElementById('root');

if (rootElement === null) {
  throw new Error('Root element #root was not found');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
import React from 'react'
import ReactDOM from 'react-dom/client'

import { App } from '@/app/App'
import { AppErrorBoundary } from '@/shared/ui/ErrorBoundary'
import '@/styles/global.css'

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <AppErrorBoundary>
      <App />
    </AppErrorBoundary>
  </React.StrictMode>,
)
