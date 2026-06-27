import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import TrustBar from "@/components/TrustBar";
import SolutionSection from "@/components/SolutionSection";
import MetricsSection from "@/components/MetricsSection";
import Footer from "@/components/Footer";
import LegacyHashRedirect from "@/components/LegacyHashRedirect";
import { ErrorBoundary } from "@/components/ErrorBoundary";

export default function Home() {
  return (
    <main id="main-content" className="relative min-h-screen bg-[var(--cm-background)]">
      <LegacyHashRedirect />
      <div className="fixed inset-0 pointer-events-none z-0" aria-hidden="true">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[min(100vw,500px)] h-[min(100vw,500px)] rounded-full bg-[var(--cm-brand-accent)]/5 blur-[120px]" />
      </div>
      <Navbar />
      <ErrorBoundary>
        <div className="relative z-10">
          <Hero />
          <TrustBar />
          <SolutionSection />
          <MetricsSection />
          <Footer />
        </div>
      </ErrorBoundary>
    </main>
  );
}
