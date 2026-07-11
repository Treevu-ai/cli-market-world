"use client";

import { AuthProvider, useApiKey } from "@/lib/useApiKey";
import ApiKeyGate from "@/components/dashboard/ApiKeyGate";
import DashboardNav from "@/components/dashboard/DashboardNav";

/** Real console shell (was a no-op passthrough). Only gates/navs here —
 *  Navbar/Footer stay inside each page (Pricing/Household already render
 *  their own; duplicating them at this layout level would double-render). */
function DashboardShell({ children }: { children: React.ReactNode }) {
  const { status } = useApiKey();

  if (status === "unknown") return null;

  if (status === "anonymous") {
    return (
      <main className="min-h-screen bg-[var(--cm-background)] flex items-center justify-center px-4 py-20">
        <ApiKeyGate />
      </main>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--cm-background)]">
      {/* pt-20 clears the fixed Navbar each page renders (same offset those
          pages use for their own <main>), so it doesn't overlap and swallow
          clicks on DashboardNav underneath it. */}
      <div className="pt-20 relative z-40">
        <DashboardNav />
      </div>
      {children}
    </div>
  );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <DashboardShell>{children}</DashboardShell>
    </AuthProvider>
  );
}
