import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Lines from "@/components/Lines";
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

export default function Home() {
  return (
    <main className="relative min-h-screen bg-[#0A0A0A]">
      {/* Global grid background */}
      <div className="grid-bg fixed inset-0 opacity-[0.03] pointer-events-none" style={{
        backgroundImage: "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
        backgroundSize: "64px 64px",
      }} aria-hidden="true" />

      <NoiseOverlay />
      <Navbar />

      <div className="relative z-10">
        <Hero />
        <Lines />
        <TerminalSection />
        <AgentDispatch />
        <HowItWorks />
        <StatsSection />
        <UseCases />
        <Features />
        <Pricing />
        <FAQ />
        <FinalCTA />
        <Footer />
      </div>
    </main>
  );
}
