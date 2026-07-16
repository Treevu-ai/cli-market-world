"use client";

import { useState } from "react";
import SpokePageShell from "@/components/spoke/SpokePageShell";
import SpokeHero from "@/components/spoke/SpokeHero";
import SpokeHubLink from "@/components/spoke/SpokeHubLink";
import SpokeStepsSection from "@/components/spoke/SpokeStepsSection";
import SpokeFinalCTA from "@/components/spoke/SpokeFinalCTA";
import RetailersStatsStrip from "@/components/retailers/RetailersStatsStrip";
import RetailersBenefitsSection from "@/components/retailers/RetailersBenefitsSection";
import RetailersPricingSection from "@/components/retailers/RetailersPricingSection";
import ActiveBrandTicker from "@/components/ActiveBrandTicker";
import RetailerApplyModal from "@/components/RetailerApplyModal";
import Footer from "@/components/Footer";
import { SPOKE_CONFIG } from "@/lib/spokeConfig";
import { RETAILERS_STEPS_SECTION } from "@/lib/retailersSpokeContent";

export default function RetailersPage() {
  const [applyOpen, setApplyOpen] = useState(false);
  const openApply = () => setApplyOpen(true);

  return (
    <SpokePageShell brandMode={SPOKE_CONFIG.retailers.brandMode}>
      <SpokeHero icp="retailers" onPrimaryClick={openApply} />
      <SpokeHubLink />
      <ActiveBrandTicker />
      <RetailersStatsStrip />
      <RetailersBenefitsSection />
      <SpokeStepsSection {...RETAILERS_STEPS_SECTION} altBackground />
      <RetailersPricingSection onFreeCta={openApply} />
      <SpokeFinalCTA icp="retailers" onPrimaryClick={openApply} />
      <RetailerApplyModal open={applyOpen} onClose={() => setApplyOpen(false)} />
      <Footer />
    </SpokePageShell>
  );
}
