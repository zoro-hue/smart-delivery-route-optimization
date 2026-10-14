import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 my-6 mx-auto max-w-xl rounded-2xl bg-white dark:bg-[#18181B] border border-red-500/30 shadow-xl text-center space-y-4">
          <div className="inline-flex p-3 rounded-full bg-red-100 dark:bg-red-950 text-red-600 font-bold">
            ⚠️ Workspace Render Notice
          </div>
          <h2 className="text-base font-heading font-bold text-[#080808] dark:text-white">
            {this.props.fallbackTitle || 'A rendering issue occurred in this section'}
          </h2>
          <p className="text-xs font-mono text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 p-3 rounded-lg text-left overflow-x-auto">
            {this.state.error?.message || 'Unknown render exception'}
          </p>
          <button
            onClick={() => {
              this.setState({ hasError: false, error: null });
              window.location.reload();
            }}
            className="px-4 py-2 rounded-full bg-[#080808] text-[#B7FF2A] text-xs font-bold font-heading hover:bg-[#171717] transition-all cursor-pointer"
          >
            Reload Workspace
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
