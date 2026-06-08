"use client";
import RetailersPricingPanel from "@/components/RetailersPricingPanel";

/** @deprecated Use Pricing section with Retailers tab. Kept for backward-compatible imports. */
export default function RetailersSection() {
  return (
    <section className="landing-section landing-section-alt animate-fade-in">
      <div className="landing-container">
        <RetailersPricingPanel />
      </div>
    </section>
  );
}