import Navbar from "@/components/Navbar";
import SideNav from "@/components/SideNav";
import Hero from "@/components/Hero";
import TrustBar from "@/components/TrustBar";
import ProblemSection from "@/components/ProblemSection";
import SolutionSection from "@/components/SolutionSection";
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
          <div id="intelligence" className="scroll-mt-20" aria-hidden="true" />
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
