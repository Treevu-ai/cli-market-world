import type { Metadata } from "next";
import SpokePageShell from "@/components/spoke/SpokePageShell";
import SpokeHero from "@/components/spoke/SpokeHero";
import SpokeHubLink from "@/components/spoke/SpokeHubLink";
import Pricing from "@/components/Pricing";
import FAQ from "@/components/FAQ";
import FinalCTASection from "@/components/FinalCTASection";
import Footer from "@/components/Footer";
import { SPOKE_CONFIG } from "@/lib/spokeConfig";

export const metadata: Metadata = {
  title: "Build — API & MCP for developers",
  description:
    "CLI Market Build: API, MCP, and CLI for AI agents. Free tier, Starter $9/mo, Pro $49/mo. Normalized LATAM retail prices.",
  alternates: { canonical: "/build" },
};

export default function BuildPage() {
  const { brandMode } = SPOKE_CONFIG.build;

  return (
    <SpokePageShell brandMode={brandMode} legacyHashRedirect>
      <SpokeHero icp="build" />
      <SpokeHubLink />
      <Pricing />
      <FAQ />
      <FinalCTASection />
      <Footer />
    </SpokePageShell>
  );
}
