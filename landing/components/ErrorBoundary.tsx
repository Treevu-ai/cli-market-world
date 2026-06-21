"use client";
import { Component, type ReactNode } from "react";
interface Props { children: ReactNode }
interface State { hasError: boolean }
export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };
  static getDerivedStateFromError(): State { return { hasError: true }; }
  render() {
    if (this.state.hasError) return <div className="min-h-screen flex items-center justify-center bg-black text-white font-mono text-sm">Something went wrong. <a href="/" className="text-[#7CFF5B] ml-2 underline">Reload</a></div>;
    return this.props.children;
  }
}
