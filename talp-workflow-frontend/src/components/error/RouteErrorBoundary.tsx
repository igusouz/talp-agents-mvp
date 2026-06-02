import { isRouteErrorResponse, useRouteError } from 'react-router-dom';

export function RouteErrorBoundary() {
  const error = useRouteError();

  const title = isRouteErrorResponse(error) ? `${error.status} ${error.statusText}` : 'Route error';
  const message = isRouteErrorResponse(error)
    ? typeof error.data === 'string'
      ? error.data
      : error.data && typeof error.data === 'object' && 'message' in error.data
        ? String((error.data as { message?: unknown }).message ?? 'The requested route could not be rendered.')
        : 'The requested route could not be rendered.'
    : error instanceof Error
      ? error.message
      : 'The requested route could not be rendered.';

  return (
    <div className="error-state error-state--route" role="alert">
      <p className="error-state__eyebrow">Navigation problem</p>
      <h2 className="error-state__title">{title}</h2>
      <p className="error-state__message">{message}</p>
    </div>
  );
}
