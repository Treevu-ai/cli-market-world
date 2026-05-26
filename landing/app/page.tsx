import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import QuickstartAPI from "@/components/QuickstartAPI";
import CoverageSection from "@/components/CoverageSection";
import DataSection from "@/components/DataSection";
import TerminalSection from "@/components/TerminalSection";
import AgentDispatch from "@/components/AgentDispatch";
import HowItWorks from "@/components/HowItWorks";
import StatsSection from "@/components/StatsSection";
import UseCases from "@/components/UseCases";
import Features from "@/components/Features";
import FAQ from "@/components/FAQ";
import Pricing from "@/components/Pricing";
import FinalCTA from "@/components/FinalCTA";
import Footer from "@/components/Footer";
import { NoiseOverlay } from "@/components/AnimatedSphere";
import { ErrorBoundary } from "@/components/ErrorBoundary";

export default function Home() {
  return (
    <main className="relative min-h-screen bg-[#131313]">
      {/* Global grid background */}
      <div className="grid-bg fixed inset-0 opacity-[0.03] pointer-events-none" style={{
        backgroundImage: "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
        backgroundSize: "64px 64px",
      }} aria-hidden="true" />

      <NoiseOverlay />
      <Navbar />

      <ErrorBoundary>
      <div className="relative z-10">
        <Hero />
        <StatsSection />
        <HowItWorks />
        <TerminalSection />
        <QuickstartAPI />
        <Features />
        <CoverageSection />
        <DataSection />
        <Pricing />
        <FAQ />
        <AgentDispatch />
        <FinalCTA />
        <Footer />
      </div>
      </ErrorBoundary>
    </main>
  );
}
