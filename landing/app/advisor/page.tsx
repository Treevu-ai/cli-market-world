import type { Metadata } from "next";
import SpokePageShell from "@/components/spoke/SpokePageShell";
import SpokeHero from "@/components/spoke/SpokeHero";
import SpokeHubLink from "@/components/spoke/SpokeHubLink";
import AdvisorStatsStrip from "@/components/advisor/AdvisorStatsStrip";
import AdvisorHubSection from "@/app/advisor/_components/AdvisorHubSection";
import ExamplesSection from "@/app/advisor/_components/ExamplesSection";
import ContactSection from "@/app/advisor/_components/ContactSection";
import Footer from "@/components/Footer";
import { SPOKE_CONFIG } from "@/lib/spokeConfig";

export const metadata: Metadata = {
  title: "Asesores — CLI Market",
  description:
    "Herramienta de evidencia de góndola para asesores, consultores de marketing e inteligencia de mercados en LATAM. Datos verificados, reportes y alertas.",
  alternates: { canonical: "/advisor" },
};

export default function AdvisorPage() {
  const { brandMode } = SPOKE_CONFIG.advisor;

  return (
    <SpokePageShell brandMode={brandMode}>
      <SpokeHero icp="advisor" />
      <SpokeHubLink />
      <AdvisorStatsStrip />
      <AdvisorHubSection />
      <ExamplesSection />
      <ContactSection />
      <Footer />
    </SpokePageShell>
  );
}
