import type { Metadata } from "next";
import Navbar from "@/components/Navbar";
import BuildSpokeHeader from "@/components/BuildSpokeHeader";
import Pricing from "@/components/Pricing";
import FAQ from "@/components/FAQ";
import FinalCTASection from "@/components/FinalCTASection";
import Footer from "@/components/Footer";
import LegacyHashRedirect from "@/components/LegacyHashRedirect";
import { ErrorBoundary } from "@/components/ErrorBoundary";

export const metadata: Metadata = {
  title: "Build — API & MCP for developers",
  description:
    "CLI Market Build: API, MCP, and CLI for AI agents. Free tier, Starter $9/mo, Pro $49/mo. Normalized LATAM retail prices.",
  alternates: { canonical: "/build" },
};

export default function BuildPage() {
  return (
    <main id="main-content" className="relative min-h-screen bg-[var(--cm-background)]">
      <LegacyHashRedirect />
      <Navbar />
      <ErrorBoundary>
        <div className="relative z-10">
          <BuildSpokeHeader />
          <Pricing />
          <FAQ />
          <FinalCTASection />
          <Footer />
        </div>
      </ErrorBoundary>
    </main>
  );
}
