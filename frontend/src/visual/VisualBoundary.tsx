import { Component, type ReactNode } from 'react';

/** A visual that fails to render disappears; the solution steps around it stay (ADR-006). */
export class VisualBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  render() {
    return this.state.failed ? null : this.props.children;
  }
}
