import type { Metadata } from "next";
import SpokePageShell from "@/components/spoke/SpokePageShell";
import SpokeHero from "@/components/spoke/SpokeHero";
import SpokeHubLink from "@/components/spoke/SpokeHubLink";
import IntelligenceSection from "@/components/IntelligenceSection";
import Footer from "@/components/Footer";
import { SPOKE_CONFIG } from "@/lib/spokeConfig";

export const metadata: Metadata = {
  title: "Intelligence — Retail signals before CPI",
  description:
    "CLI Market Intelligence: spreads, category inflation, and basic basket from verified shelf data. Pilot from $300/mo.",
  alternates: { canonical: "/intelligence" },
};

export default function IntelligencePage() {
  const { brandMode } = SPOKE_CONFIG.intelligence;

  return (
    <SpokePageShell brandMode={brandMode}>
      <SpokeHero icp="intelligence" />
      <SpokeHubLink />
      <IntelligenceSection omitHeader />
      <Footer />
    </SpokePageShell>
  );
}
