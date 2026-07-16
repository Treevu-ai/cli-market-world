import type { Metadata } from "next";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import HeroSection from "@/app/advisor/_components/HeroSection";
import AdvisorHubSection from "@/app/advisor/_components/AdvisorHubSection";
import ExamplesSection from "@/app/advisor/_components/ExamplesSection";
import ContactSection from "@/app/advisor/_components/ContactSection";

export const metadata: Metadata = {
  title: "Asesores — CLI Market",
  description:
    "Herramienta de evidencia de góndola para asesores, consultores de marketing e inteligencia de mercados en LATAM. Datos verificados, reportes y alertas.",
  alternates: { canonical: "/advisor" },
};

export default function AdvisorPage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-10">
        <HeroSection />
        <AdvisorHubSection />
        <ExamplesSection />
        <ContactSection />
      </div>
      <Footer />
    </main>
  );
}
