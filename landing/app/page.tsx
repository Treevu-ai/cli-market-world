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
    <main className="relative min-h-screen bg-[var(--cm-background)] xl:pl-12">
      <div className="grid-bg fixed inset-0 opacity-40 pointer-events-none" aria-hidden="true" />
      <Navbar />
      <SideNav />
      <ErrorBoundary>
        <div className="relative z-10">
          <Hero />
          <HowItWorks />
          <CapabilitiesSection />
          <CinematicVision />
          <UseCasesSection />
          <Pricing />
          <ScaleCoverageSection />
          <FAQ />
          <Footer />
        </div>
      </ErrorBoundary>
    </main>
  );
}
