import Navbar from "@/components/Navbar";
import SideNav from "@/components/SideNav";
import Hero from "@/components/Hero";
import TrustBar from "@/components/TrustBar";
import ProblemSection from "@/components/ProblemSection";
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
    <main id="main-content" className="relative min-h-screen bg-[#f8fafc] xl:pl-12">
      <Navbar />
      <SideNav />
      <ErrorBoundary>
        <div className="relative z-10">
          <Hero />
          <TrustBar />
          <ProblemSection />
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
