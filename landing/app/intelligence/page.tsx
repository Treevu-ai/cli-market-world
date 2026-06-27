import type { Metadata } from "next";
import Navbar from "@/components/Navbar";
import IntelligenceSection from "@/components/IntelligenceSection";
import Footer from "@/components/Footer";
import { ErrorBoundary } from "@/components/ErrorBoundary";

export const metadata: Metadata = {
  title: "Intelligence — Retail signals before CPI",
  description:
    "CLI Market Intelligence: spreads, category inflation, and basic basket from verified shelf data. Pilot from $300/mo.",
  alternates: { canonical: "/intelligence" },
};

export default function IntelligencePage() {
  return (
    <main id="main-content" className="relative min-h-screen bg-[var(--cm-background)]">
      <Navbar />
      <ErrorBoundary>
        <div className="relative z-10 pt-16">
          <IntelligenceSection />
          <Footer />
        </div>
      </ErrorBoundary>
    </main>
  );
}
