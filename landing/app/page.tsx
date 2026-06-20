import Navbar from "@/components/Navbar";
import SideNav from "@/components/SideNav";
import Hero from "@/components/Hero";
import HowItWorks from "@/components/HowItWorks";
import CinematicVision from "@/components/CinematicVision";
import CapabilitiesSection from "@/components/CapabilitiesSection";
import UseCasesSection from "@/components/UseCasesSection";
import ScaleCoverageSection from "@/components/ScaleCoverageSection";
import Pricing from "@/components/Pricing";
import FAQ from "@/components/FAQ";
import Footer from "@/components/Footer";
import { ErrorBoundary } from "@/components/ErrorBoundary";

export default function Home() {
  return (
    <main className="relative min-h-screen bg-white xl:pl-12">
      <Navbar />
      <SideNav />
      <ErrorBoundary>
        <div className="relative z-10">
          <Hero />
          <HowItWorks />
          <CapabilitiesSection />
          <CinematicVision />
          <UseCasesSection />
          <div id="intelligence" className="scroll-mt-20" aria-hidden="true" />
          <Pricing />
          <ScaleCoverageSection />
          <FAQ />
          <Footer />
        </div>
      </ErrorBoundary>
    </main>
  );
}
