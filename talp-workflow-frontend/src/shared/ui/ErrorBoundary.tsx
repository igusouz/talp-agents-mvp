import { Component, type ErrorInfo, type ReactNode } from 'react'

import { ErrorState } from '@/shared/ui/ErrorState'

interface ErrorBoundaryProps {
  children: ReactNode
}

interface ErrorBoundaryState {
  error: Error | null
}

export class AppErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error }
  }

  override componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Production apps should forward this to a logging pipeline.
    console.error('Unhandled UI error', error, errorInfo)
  }

  private handleReset = () => {
    this.setState({ error: null })
  }

  override render() {
    if (this.state.error) {
      return (
        <ErrorState
          title="Something went wrong"
          description={this.state.error.message}
          actionLabel="Try again"
          onAction={this.handleReset}
        />
      )
    }

    return this.props.children
  }
}
