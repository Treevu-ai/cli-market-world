"use client";

import { useLang } from "@/lib/LanguageContext";
import { RETAILER_TIERS, type RetailerTierSpec } from "@/lib/retailersPricingTiers";

function TierCard({
  tier,
  isES,
  onApply,
}: {
  tier: RetailerTierSpec;
  isES: boolean;
  onApply: () => void;
}) {
  const features = isES ? tier.features_es : tier.features_en;
  const period = isES ? tier.period_es : tier.period_en;

  return (
    <div
      className={`relative h-full rounded-2xl p-6 text-left flex flex-col ${tier.featured ? "energy-border-active card-cyber" : "card-cyber"}`}
      style={tier.featured ? { background: "var(--cm-mint)", borderColor: "var(--cm-mint)" } : undefined}
    >
      {tier.featured && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[var(--cm-ink)] text-[var(--cm-background)] text-xs font-semibold px-4 py-1 rounded-full whitespace-nowrap shadow-sm">
          {isES ? "Recomendado" : "Recommended"}
        </span>
      )}

      <h3 className={`text-lg font-bold ${tier.featured ? "text-[var(--cm-on-mint)]" : "text-[var(--cm-on-surface)]"}`}>
        {tier.name}
      </h3>

      <div className="mt-3 mb-1 flex flex-wrap items-baseline gap-x-2">
        <span className={`text-3xl font-black tabular-nums ${tier.featured ? "text-[var(--cm-on-mint)]" : "text-[var(--cm-on-surface)]"}`}>
          {tier.priceUsd === null ? (isES ? "A medida" : "Custom") : tier.priceUsd === 0 ? (isES ? "$0" : "$0") : `$${tier.priceUsd}`}
        </span>
        {period && (
          <span className={`text-sm ${tier.featured ? "text-[var(--cm-on-mint)]/85" : "text-[var(--cm-on-surface-variant)]"}`}>
            {period}
          </span>
        )}
      </div>

      <ul className="space-y-3 mb-6 mt-4 flex-1">
        {features.map((f) => (
          <li
            key={f}
            className={`flex items-start gap-2.5 text-sm leading-relaxed ${tier.featured ? "text-[var(--cm-on-mint)]/90" : "text-[var(--cm-on-surface-variant)]"}`}
          >
            <svg
              className="w-4 h-4 mt-0.5 shrink-0"
              viewBox="0 0 24 24"
              fill="none"
              stroke={tier.featured ? "var(--cm-on-mint)" : "var(--cm-mint)"}
              strokeWidth="2.5"
            >
              <path d="M20 6L9 17l-5-5" />
            </svg>
            {f}
          </li>
        ))}
      </ul>

      <div className="mt-auto">
        {tier.id === "custom" ? (
          <a href="/contact?topic=enterprise#contact-form" className="btn-outline w-full">
            {isES ? tier.cta_es : tier.cta_en}
          </a>
        ) : (
          <button type="button" onClick={onApply} className={tier.featured ? "btn-mint w-full" : "btn-outline w-full"}>
            {isES ? tier.cta_es : tier.cta_en}
          </button>
        )}
      </div>
    </div>
  );
}

export default function RetailersPricingSection({ onApply }: { onApply: () => void }) {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="retailers-pricing" className="landing-section landing-section-alt scroll-mt-24">
      <div className="landing-container-wide">
        <div className="landing-section-header text-center">
          <p className="section-eyebrow mb-4">{isES ? "PLANES" : "PLANS"}</p>
          <h2 className="section-title">{isES ? "Crece tu visibilidad" : "Grow your visibility"}</h2>
          <p className="section-intro">
            {isES
              ? "El listado básico es gratis para siempre. Sube de plan cuando quieras prioridad e inteligencia competitiva."
              : "Basic listing is free forever. Upgrade when you want priority and competitive intelligence."}
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mt-10 max-w-4xl mx-auto">
          {RETAILER_TIERS.map((tier) => (
            <TierCard key={tier.id} tier={tier} isES={isES} onApply={onApply} />
          ))}
        </div>
      </div>
    </section>
  );
}
