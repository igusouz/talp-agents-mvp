import type { ErrorInfo, ReactNode } from 'react';
import React from 'react';

type GlobalErrorBoundaryProps = {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, info: ErrorInfo) => void;
};

type GlobalErrorBoundaryState = {
  error: Error | null;
};

export class GlobalErrorBoundary extends React.Component<GlobalErrorBoundaryProps, GlobalErrorBoundaryState> {
  constructor(props: GlobalErrorBoundaryProps) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error: Error): GlobalErrorBoundaryState {
    return { error };
  }

  override componentDidCatch(error: Error, info: ErrorInfo) {
    this.props.onError?.(error, info);
  }

  private handleReset = () => {
    this.setState({ error: null });
  };

  override render() {
    if (this.state.error !== null) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="error-state error-state--global" role="alert">
          <p className="error-state__eyebrow">Application error</p>
          <h2 className="error-state__title">Something went wrong</h2>
          <p className="error-state__message">The frontend hit an unexpected failure. You can retry safely.</p>
          <button className="button button--primary" type="button" onClick={this.handleReset}>
            Retry
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
