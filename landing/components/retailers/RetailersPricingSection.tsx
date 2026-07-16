"use client";

import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import PaymentReturnBanner from "@/components/PaymentReturnBanner";
import {
  RETAILER_TIERS,
  type RetailerTierSpec,
} from "@/lib/retailersPricingTiers";

type RetailersPricingSectionProps = {
  onFreeCta: () => void;
};

function TierCard({
  tier,
  isES,
  onFreeCta,
}: {
  tier: RetailerTierSpec;
  isES: boolean;
  onFreeCta: () => void;
}) {
  const [growthState, setGrowthState] = useState<"idle" | "loading" | "error">("idle");
  const [growthEmail, setGrowthEmail] = useState("");
  const [growthStore, setGrowthStore] = useState("");
  const [showGrowthForm, setShowGrowthForm] = useState(false);
  const features = isES ? tier.features_es : tier.features_en;
  const cta = isES ? tier.cta_es : tier.cta_en;

  const startGrowthCheckout = async () => {
    if (!growthEmail.trim() || !growthStore.trim()) return;
    setGrowthState("loading");
    try {
      const res = await fetch(`${API_URL}/billing/retailer-growth-checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: growthEmail.trim(),
          store_name: growthStore.trim(),
          lang: isES ? "es" : "en",
        }),
      });
      const data = await res.json();
      if (!res.ok || !data.checkout_url) {
        setGrowthState("error");
        return;
      }
      window.location.href = data.checkout_url;
    } catch {
      setGrowthState("error");
    }
  };

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
          {tier.priceUsd === null ? (isES ? "A medida" : "Custom") : tier.priceUsd === 0 ? "$0" : `$${tier.priceUsd}`}
        </span>
        {(isES ? tier.period_es : tier.period_en) && (
          <span className={`text-sm ${tier.featured ? "text-[var(--cm-on-mint)]/85" : "text-[var(--cm-on-surface-variant)]"}`}>
            {isES ? tier.period_es : tier.period_en}
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

      {tier.id === "free" && (
        <button type="button" onClick={onFreeCta} className="mt-auto btn-outline w-full">
          {cta}
        </button>
      )}

      {tier.id === "custom" && (
        <a href="/contact?topic=retailer-custom#contact-form" className="mt-auto btn-outline w-full">
          {cta}
        </a>
      )}

      {tier.id === "growth" && (
        <div className="mt-auto space-y-2">
          {!showGrowthForm ? (
            <button type="button" onClick={() => setShowGrowthForm(true)} className="btn-mint w-full">
              {cta}
            </button>
          ) : (
            <div className="space-y-2 pt-2 border-t border-[var(--cm-on-mint)]/20">
              <input
                type="text"
                value={growthStore}
                onChange={(e) => setGrowthStore(e.target.value)}
                placeholder={isES ? "Nombre de tu tienda" : "Your store name"}
                className="w-full text-sm bg-[var(--cm-surface)] border border-[var(--cm-on-mint)]/30 rounded-lg p-2 outline-none focus:ring-1 focus:ring-[var(--cm-on-mint)]"
              />
              <input
                type="email"
                value={growthEmail}
                onChange={(e) => setGrowthEmail(e.target.value)}
                placeholder={isES ? "Tu email" : "Your email"}
                className="w-full text-sm bg-[var(--cm-surface)] border border-[var(--cm-on-mint)]/30 rounded-lg p-2 outline-none focus:ring-1 focus:ring-[var(--cm-on-mint)]"
              />
              <button
                type="button"
                onClick={startGrowthCheckout}
                disabled={growthState === "loading" || !growthEmail.trim() || !growthStore.trim()}
                className="btn-mint w-full disabled:opacity-60"
              >
                {growthState === "loading"
                  ? isES
                    ? "Abriendo Mercado Pago…"
                    : "Opening Mercado Pago…"
                  : isES
                    ? "Ir a pagar — Mercado Pago"
                    : "Go to payment — Mercado Pago"}
              </button>
              {growthState === "error" && (
                <p className="text-xs text-rose-100">
                  {isES
                    ? "No pudimos iniciar el pago. Intenta de nuevo o escríbenos a hello@cli-market.dev."
                    : "We couldn't start the payment. Try again or email hello@cli-market.dev."}
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function RetailersPricingSection({ onFreeCta }: RetailersPricingSectionProps) {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="retailers-pricing" className="landing-section landing-section-alt scroll-mt-24">
      <div className="landing-container-wide">
        <div className="landing-section-header text-center">
          <p className="section-eyebrow mb-4">{isES ? "PLANES" : "PLANS"}</p>
          <h2 className="section-title">
            {isES ? "Empieza gratis, crece cuando quieras" : "Start free, grow when you're ready"}
          </h2>
          <p className="section-intro">
            {isES
              ? "El listado básico siempre es gratis. Growth suma visibilidad y datos de competencia por un pago mensual fijo."
              : "Basic listing is always free. Growth adds visibility and competitor data for a fixed monthly fee."}
          </p>
        </div>

        <PaymentReturnBanner />

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mt-10 max-w-4xl mx-auto">
          {RETAILER_TIERS.map((tier) => (
            <TierCard key={tier.id} tier={tier} isES={isES} onFreeCta={onFreeCta} />
          ))}
        </div>
      </div>
    </section>
  );
}
