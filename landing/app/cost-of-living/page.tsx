import type { Metadata } from "next";
import SpokePageShell from "@/components/spoke/SpokePageShell";
import SpokeHero from "@/components/spoke/SpokeHero";
import SpokeHubLink from "@/components/spoke/SpokeHubLink";
import CostOfLivingSection from "@/components/CostOfLivingSection";
import SpokeFinalCTA from "@/components/spoke/SpokeFinalCTA";
import Footer from "@/components/Footer";
import { SPOKE_CONFIG } from "@/lib/spokeConfig";

export const metadata: Metadata = {
  title: "Cost of Living OS — Affordability score & basket optimization",
  description:
    "Affordability score, optimized basket with real TCO, smart substitutes, and regulatory context from verified shelf prices across LATAM.",
  alternates: { canonical: "/cost-of-living" },
};

export default function CostOfLivingPage() {
  const { brandMode } = SPOKE_CONFIG["cost-of-living"];

  return (
    <SpokePageShell brandMode={brandMode}>
      <SpokeHero icp="cost-of-living" />
      <SpokeHubLink />
      <CostOfLivingSection />
      <SpokeFinalCTA icp="cost-of-living" />
      <Footer />
    </SpokePageShell>
  );
}
