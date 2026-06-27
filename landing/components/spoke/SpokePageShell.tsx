"use client";

import Navbar from "@/components/Navbar";
import LegacyHashRedirect from "@/components/LegacyHashRedirect";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import type { SpokeBrandMode } from "@/lib/spokeConfig";

type SpokePageShellProps = {
  brandMode?: SpokeBrandMode;
  legacyHashRedirect?: boolean;
  children: React.ReactNode;
};

/** Shared page shell for ICP spokes — matches hub ambient glow + nav. */
export default function SpokePageShell({
  brandMode = "terminal",
  legacyHashRedirect = false,
  children,
}: SpokePageShellProps) {
  const isOperations = brandMode === "operations";

  return (
    <main
      id="main-content"
      className={`relative min-h-screen bg-[var(--cm-background)]${isOperations ? " brand-mode-operations" : ""}`}
    >
      {legacyHashRedirect ? <LegacyHashRedirect /> : null}
      <div className="fixed inset-0 pointer-events-none z-0" aria-hidden="true">
        <div
          className={`absolute top-1/4 left-1/2 -translate-x-1/2 w-[min(100vw,500px)] h-[min(100vw,500px)] rounded-full blur-[120px] ${
            isOperations ? "bg-[var(--cm-brand-accent)]/[0.02]" : "bg-[var(--cm-brand-accent)]/5"
          }`}
        />
      </div>
      <Navbar />
      <ErrorBoundary>
        <div className="relative z-10">{children}</div>
      </ErrorBoundary>
    </main>
  );
}
