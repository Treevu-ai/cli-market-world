import Navbar from "@/components/Navbar";
import SideNav from "@/components/SideNav";
import Hero from "@/components/Hero";
import HowItWorks from "@/components/HowItWorks";
import QuickstartAPI from "@/components/QuickstartAPI";
import UseCasesSection from "@/components/UseCasesSection";
import RetailersSection from "@/components/RetailersSection";
import ScaleCoverageSection from "@/components/ScaleCoverageSection";
import CoverageToUseCasesBridge from "@/components/CoverageToUseCasesBridge";
import Pricing from "@/components/Pricing";
import FAQ from "@/components/FAQ";
import AboutSection from "@/components/AboutSection";
import Footer from "@/components/Footer";
import { ErrorBoundary } from "@/components/ErrorBoundary";

export default function Home() {
  return (
    <main className="relative min-h-screen bg-[var(--wise-canvas-soft)]">
      <div className="grid-bg fixed inset-0 opacity-30 pointer-events-none" aria-hidden="true" />
      <Navbar />
      <SideNav />
      <ErrorBoundary>
        <div className="relative z-10">
          <Hero />
          <HowItWorks />
          <QuickstartAPI />
          <ScaleCoverageSection />
          <CoverageToUseCasesBridge />
          <UseCasesSection />
          <Pricing />
          <RetailersSection />
          <FAQ />
          <AboutSection />
          <Footer />
        </div>
      </ErrorBoundary>
    </main>
  );
}
