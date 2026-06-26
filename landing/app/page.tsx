import Navbar from "@/components/Navbar";
import SideNav from "@/components/SideNav";
import Hero from "@/components/Hero";
import TrustBar from "@/components/TrustBar";
import SolutionSection from "@/components/SolutionSection";
import UseCasesSection from "@/components/UseCasesSection";
import ProcureCopilotSection from "@/components/ProcureCopilotSection";
import IntelligenceSection from "@/components/IntelligenceSection";
import WhoItsForSection from "@/components/WhoItsForSection";
import MetricsSection from "@/components/MetricsSection";
import Pricing from "@/components/Pricing";
import FAQ from "@/components/FAQ";
import FinalCTASection from "@/components/FinalCTASection";
import Footer from "@/components/Footer";
import { ErrorBoundary } from "@/components/ErrorBoundary";

export default function Home() {
  return (
    <main id="main-content" className="relative min-h-screen bg-[var(--cm-background)] xl:pl-12">
      <div className="fixed inset-0 pointer-events-none z-0" aria-hidden="true">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[min(100vw,500px)] h-[min(100vw,500px)] rounded-full bg-[var(--cm-brand-accent)]/5 blur-[120px]" />
      </div>
      <Navbar />
      <SideNav />
      <ErrorBoundary>
        <div className="relative z-10">
          <Hero />
          <TrustBar />
          <SolutionSection />
          <UseCasesSection />
          <ProcureCopilotSection />
          <IntelligenceSection />
          <MetricsSection />
          <WhoItsForSection />
          <Pricing />
          <FAQ />
          <FinalCTASection />
          <Footer />
        </div>
      </ErrorBoundary>
    </main>
  );
}
