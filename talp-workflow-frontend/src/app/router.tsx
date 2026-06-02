import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom';

import { AppShell } from '@/app/layouts/AppShell';
import { WorkflowShell } from '@/app/layouts/WorkflowShell';
import { RouteErrorBoundary } from '@/components/error/RouteErrorBoundary';
import { HomeRedirect } from '@/pages/HomeRedirect';
import { NotFoundPage } from '@/pages/NotFoundPage';
import { FinalAnalysisPlaceholderPage } from '@/features/final/FinalAnalysisPlaceholderPage';
import { HumanReviewPage } from '@/features/review/HumanReviewPage';
import { ReviewPlaceholderPage } from '@/features/review/ReviewPlaceholderPage';
import { StorySubmissionPlaceholderPage } from '@/features/story-submission/StorySubmissionPlaceholderPage';

const router = createBrowserRouter([
  {
    element: <AppShell />,
    errorElement: <RouteErrorBoundary />,
    children: [
      {
        index: true,
        element: <HomeRedirect />,
      },
      {
        path: 'stories/new',
        element: <StorySubmissionPlaceholderPage />,
      },
      {
        path: 'workflows/:workflowId',
        element: <WorkflowShell />,
        children: [
          {
            index: true,
            element: <Navigate to="review" replace />,
          },
          {
            path: 'review',
            element: <ReviewPlaceholderPage />,
          },
          {
            path: 'review/human',
            element: <HumanReviewPage />,
          },
          {
            path: 'final',
            element: <FinalAnalysisPlaceholderPage />,
          },
        ],
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
