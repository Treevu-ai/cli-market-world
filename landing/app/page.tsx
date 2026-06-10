import Navbar from "@/components/Navbar";
import SideNav from "@/components/SideNav";
import Hero from "@/components/Hero";
import HeroPlayground from "@/components/HeroPlayground";
import ScrollStorySection from "@/components/ScrollStorySection";
import HowItWorks from "@/components/HowItWorks";
import QuickstartAPI from "@/components/QuickstartAPI";
import UseCasesSection from "@/components/UseCasesSection";
import IntelligenceSection from "@/components/IntelligenceSection";


import ScaleCoverageSection from "@/components/ScaleCoverageSection";
import CoverageToUseCasesBridge from "@/components/CoverageToUseCasesBridge";
import Pricing from "@/components/Pricing";
import FAQ from "@/components/FAQ";
import ContactSection from "@/components/ContactSection";
import AboutSection from "@/components/AboutSection";
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
          <ScrollStorySection />
          <section
            id="hero-playground-mobile"
            className="md:hidden landing-container-wide pb-12 -mt-2 scroll-mt-20 text-center"
            aria-label="CLI Market playground"
          >
            <HeroPlayground />
          </section>
          <UseCasesSection />
          <ScaleCoverageSection />
          <CoverageToUseCasesBridge />
          <HowItWorks />
          <QuickstartAPI />
          <IntelligenceSection />
          <Pricing />
          <FAQ />
          <ContactSection />
          <AboutSection />
          <Footer />
        </div>
      </ErrorBoundary>
    </main>
  );
}
