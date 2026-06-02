import { isRouteErrorResponse, useRouteError } from 'react-router-dom'

import { ErrorState } from '@/shared/ui/ErrorState'

export function RouteErrorBoundary() {
  const error = useRouteError()

  if (isRouteErrorResponse(error)) {
    return (
      <ErrorState
        title={`${error.status} ${error.statusText}`}
        description={typeof error.data === 'string' ? error.data : 'The route could not be loaded.'}
      />
    )
  }

  if (error instanceof Error) {
    return <ErrorState title="Route error" description={error.message} />
  }

  return <ErrorState title="Route error" description="The requested route could not be loaded." />
}
