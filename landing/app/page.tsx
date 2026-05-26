import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import QuickstartAPI from "@/components/QuickstartAPI";
import DataSection from "@/components/DataSection";
import AboutSection from "@/components/AboutSection";
import TerminalSection from "@/components/TerminalSection";
import AgentDispatch from "@/components/AgentDispatch";
import HowItWorks from "@/components/HowItWorks";
import StatsSection from "@/components/StatsSection";
import FAQ from "@/components/FAQ";
import Pricing from "@/components/Pricing";
import FinalCTA from "@/components/FinalCTA";
import Footer from "@/components/Footer";
import { ErrorBoundary } from "@/components/ErrorBoundary";

export default function Home() {
  return (
    <main className="relative min-h-screen bg-[var(--wise-canvas-soft)]">
      <Navbar />
      <ErrorBoundary>
        <div className="relative z-10">
          <Hero />
          <StatsSection />
          <HowItWorks />
          <TerminalSection />
          <QuickstartAPI />
          <DataSection />
          <Pricing />
          <AgentDispatch />
          <FAQ />
          <AboutSection />
          <FinalCTA />
          <Footer />
        </div>
      </ErrorBoundary>
    </main>
  );
}
