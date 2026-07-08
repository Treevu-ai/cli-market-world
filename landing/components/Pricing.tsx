"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import ProSubscribeButton from "@/components/ProSubscribeButton";
import BillingCheckoutTrigger from "@/components/BillingCheckoutTrigger";
import ProcurePricingPanel from "@/components/ProcurePricingPanel";
import { PROCURE_SITE_URL } from "@/lib/procurePlans";
import { redirectLegacyProcureCheckout } from "@/lib/procureCheckoutUrl";
import type { BillingCheckoutKind } from "@/components/BillingCheckoutModal";
import {
  PRICING_TABS,
  resolvePricingAudience,
  hashForAudience,
  isLegacyListedPricingHash,
  type PricingAudience,
} from "@/lib/pricingAudiences";
import {
  PAYMENTS_PLACEHOLDER,
  formatPaymentsFeature,
} from "@/lib/billingCopy";
import { usePaymentsChannels, usePricingBillingFootnote } from "@/lib/useBillingCopy";
import PaymentReturnBanner, { readPaymentReturnState } from "@/components/PaymentReturnBanner";
import {
  BUILD_TIER_STARTER,
  BUILD_TIER_PRO,
  TRIAL_DAYS,
  formatReqLimit,
} from "@/lib/buildPricingTiers";
import type { SpokeIcp } from "@/lib/spokeConfig";

type Billing = "monthly" | "annual";

type Tier = {
  name: string;
  price: string;
  latamPrice?: string;
  annualPrice?: string;
  annualLatamPrice?: string;
  compareAt?: string;
  period_es?: string;
  period_en?: string;
  f_es: string[];
  f_en: string[];
  cta_es: string;
  cta_en: string;
  dark?: boolean;
  featured?: boolean;
  limited?: boolean;
  href?: string;
  checkoutKind?: BillingCheckoutKind;
};

const FEATURE_COUNT = 5;

const tiers: Tier[] = [
  {
    name: BUILD_TIER_STARTER.name,
    price: `$${BUILD_TIER_STARTER.priceUsd}`,
    latamPrice: BUILD_TIER_STARTER.latamPricePen,
    period_es: `/ mes · ${TRIAL_DAYS} días de prueba`,
    period_en: `/ mo · ${TRIAL_DAYS}-day trial`,
    f_es: BUILD_TIER_STARTER.features_es,
    f_en: BUILD_TIER_STARTER.features_en,
    cta_es: `Prueba gratis ${TRIAL_DAYS} días`,
    cta_en: `Free ${TRIAL_DAYS}-day trial`,
    checkoutKind: { type: "build-starter" },
  },
  {
    name: BUILD_TIER_PRO.name,
    price: `$${BUILD_TIER_PRO.priceUsd}`,
    latamPrice: BUILD_TIER_PRO.latamPricePen,
    annualPrice: `$${BUILD_TIER_PRO.annualPriceUsd}`,
    annualLatamPrice: BUILD_TIER_PRO.annualLatamPricePen,
    period_es: "/ mes",
    period_en: "/ month",
    f_es: [
      formatReqLimit(BUILD_TIER_PRO.reqLimit, true),
      "3 asientos · 10 API keys",
      `Checkout retail · ${PAYMENTS_PLACEHOLDER}`,
      "Alertas · historial 12 meses",
      "Export CSV · basket optimization",
    ],
    f_en: [
      formatReqLimit(BUILD_TIER_PRO.reqLimit, false),
      "3 seats · 10 API keys",
      `Retail checkout · ${PAYMENTS_PLACEHOLDER}`,
      "Alerts · 12-month history",
      "CSV export · basket optimization",
    ],
    cta_es: "Elegir Pro",
    cta_en: "Choose Pro",
    featured: true,
    checkoutKind: { type: "build-pro" },
  },
  {
    name: "Enterprise",
    price: "Custom",
    period_es: "",
    period_en: "",
    f_es: [
      "Límites y SLAs personalizados",
      "Webhooks + endpoints dedicados",
      "Licencia de datos ampliada",
      "Soporte 24/7 + consultoría",
      "White-label y despliegue dedicado",
    ],
    f_en: [
      "Custom limits and SLAs",
      "Webhooks + dedicated endpoints",
      "Extended data license",
      "24/7 support + consulting",
      "White-label + dedicated deployment",
    ],
    cta_es: "Contactar ventas",
    cta_en: "Contact sales",
    dark: true,
    href: "/contact?topic=enterprise#contact-form",
  },
];

const BUILD_VISIBLE_TIERS = tiers.filter((t) =>
  ["Starter", "Pro", "Enterprise"].includes(t.name),
);
// cli-market.dev publicly shows only the developer ("build") line. The Procure
// audience panel still renders when reached via ?audience=procure (checkout /
// payment-return continuity) but is not offered as a browsable tab here.
const VISIBLE_PRICING_TABS = PRICING_TABS.filter((t) => t.id === "build");
const STARTER_TIER = tiers.find((t) => t.name === "Starter")!;
const PRO_TIER = tiers.find((t) => t.name === "Pro")!;

function TierCard({
  tier,
  isES,
  billing,
  foundingSeats,
  paymentsLabel,
  children,
}: {
  tier: Tier;
  isES: boolean;
  billing: Billing;
  foundingSeats?: number | null;
  paymentsLabel: string;
  children?: React.ReactNode;
}) {
  const isAnnual = billing === "annual" && tier.annualPrice;
  const displayPrice = isAnnual ? tier.annualPrice! : tier.price;
  const displayLatam = isAnnual && tier.annualLatamPrice ? tier.annualLatamPrice : tier.latamPrice;
  const period = isAnnual
    ? isES
      ? "/ año"
      : "/ year"
    : isES
      ? tier.period_es
      : tier.period_en;
  const features = (isES ? tier.f_es : tier.f_en)
    .slice(0, FEATURE_COUNT)
    .map((line) => formatPaymentsFeature(line, paymentsLabel));

  return (
    <div
      className={`h-full min-h-[24rem] rounded-2xl p-5 sm:p-6 text-left flex flex-col ${
        tier.dark || tier.featured ? "energy-border-active card-cyber" : "card-cyber"
      }`}
    >
      <div className="min-h-[1.75rem] mb-3 flex items-center justify-center">
        {tier.featured && (
          <span className="bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-xs font-semibold px-4 py-1 rounded-full whitespace-nowrap">
            {isES ? "Recomendado" : "Recommended"}
          </span>
        )}
        {tier.limited && (
          <span className="bg-[var(--cm-action)]/15 text-[var(--cm-action)] border border-[var(--cm-action)]/30 text-xs font-semibold px-4 py-1 rounded-full whitespace-nowrap">
            {foundingSeats != null
              ? isES
                ? `${foundingSeats} plazas`
                : `${foundingSeats} seats left`
              : isES
                ? "Oferta limitada"
                : "Limited offer"}
          </span>
        )}
      </div>

      <h3 className={`text-lg font-bold ${tier.dark ? "text-[var(--cm-mint)]" : "text-[var(--cm-on-surface)]"}`}>
        {tier.name}
      </h3>

      <div className="mt-3 mb-1 flex flex-wrap items-baseline gap-x-2 gap-y-0">
        {tier.compareAt && (
          <span className="text-lg text-[var(--cm-on-surface-variant)]/50 line-through tabular-nums">
            {tier.compareAt}
          </span>
        )}
        <span className="text-3xl font-black tabular-nums text-[var(--cm-on-surface)]">{displayPrice}</span>
        {period && (
          <span className="text-sm text-[var(--cm-on-surface-variant)]">{period}</span>
        )}
      </div>

      {displayLatam && displayLatam !== "S/0" && (
        <p className="text-xs text-[var(--cm-on-surface-variant)]/60 mb-1 font-mono tabular-nums">
          {displayLatam}
          {period ? ` ${period}` : ""}
        </p>
      )}

      <p className="text-xs text-[var(--cm-mint)] mb-4 min-h-[1.25rem] font-mono">
        {isAnnual && tier.annualPrice
          ? isES
            ? "Ahorra 2 meses vs mensual"
            : "Save 2 months vs monthly"
          : " "}
      </p>

      <ul className="space-y-3 mb-6 flex-1">
        {features.map((f, i) => (
          <li
            key={i}
            className="flex items-start gap-2.5 text-sm text-[var(--cm-on-surface-variant)] leading-relaxed"
          >
            <svg
              className="w-4 h-4 mt-0.5 shrink-0"
              viewBox="0 0 24 24"
              fill="none"
              stroke="var(--cm-mint)"
              strokeWidth="2.5"
            >
              <path d="M20 6L9 17l-5-5" />
            </svg>
            {f}
          </li>
        ))}
      </ul>

      <div className="mt-auto">{children}</div>
    </div>
  );
}

function scrollToPricingSection(focusId?: string) {
  requestAnimationFrame(() => {
    document.getElementById("pricing")?.scrollIntoView({ behavior: "smooth", block: "start" });
    if (focusId) {
      document.getElementById(focusId)?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
}

export default function Pricing({ spoke }: { spoke?: SpokeIcp }) {
  const { lang } = useLang();
  const isES = lang === "es";
  const isSpoke = spoke != null;
  const billing: Billing = "monthly";
  const [audience, setAudience] = useState<PricingAudience>(() =>
    typeof window !== "undefined" ? resolvePricingAudience() : "build",
  );
  const paymentsLabel = usePaymentsChannels(isES);
  const billingFootnote = usePricingBillingFootnote(isES);

  const activeTab = PRICING_TABS.find((t) => t.id === audience)!;

  useEffect(() => {
    if (redirectLegacyProcureCheckout()) return;

    const syncFromLocation = () => {
      const hash = window.location.hash;
      if (isLegacyListedPricingHash(hash)) {
        window.location.replace("/retailers");
        return;
      }
      const { state, audience: returnAudience } = readPaymentReturnState();
      const next = returnAudience === "procure" && state ? "procure" : resolvePricingAudience();
      setAudience(next);
      const hashId = hash.replace("#", "");
      if (hashId === "pro-checkout" || hashId === "pricing-build" || hashId === "pricing") {
        scrollToPricingSection(hashId === "pro-checkout" ? "pro-checkout" : undefined);
      } else if (state) {
        scrollToPricingSection(undefined);
      }
    };
    syncFromLocation();
    window.addEventListener("hashchange", syncFromLocation);
    return () => window.removeEventListener("hashchange", syncFromLocation);
  }, []);

  const setAudienceTab = (tab: PricingAudience) => {
    setAudience(tab);
    const hash = hashForAudience(tab);
    if (window.location.hash !== hash) {
      window.history.replaceState(null, "", hash);
    }
  };

  return (
    <section
      id="pricing"
      className={`landing-section landing-section-alt animate-fade-in scroll-mt-24${
        isSpoke ? "" : " landing-section-glow"
      }`}
    >
      <div className="landing-container-wide text-center">
        <p className={`section-eyebrow mb-4${isSpoke ? "" : " section-eyebrow-action"}`}>
          {isES ? "Planes" : "Plans"}
        </p>

        <PaymentReturnBanner />

        <div className="flex flex-wrap justify-center gap-3 mb-8 text-sm">
          <span className="text-[var(--cm-on-surface-variant)]/70 w-full sm:w-auto">
            {isES ? "¿No es su perfil?" : "Not your profile?"}
          </span>
          <a
            href={`${PROCURE_SITE_URL}/procure`}
            className="text-[var(--cm-mint)] font-semibold hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            {isES ? "Procure — compras desde $29/mes →" : "Procure — procurement from $29/mo →"}
          </a>
          <a href="/intelligence" className="text-[var(--cm-signal)] font-semibold hover:underline">
            {isES ? "Intelligence — piloto desde $300/mes →" : "Intelligence — pilot from $300/mo →"}
          </a>
        </div>

        {VISIBLE_PRICING_TABS.length > 1 && (
        <div
          role="tablist"
          aria-label={isES ? "Líneas de producto" : "Product lines"}
          className="flex flex-row flex-nowrap items-stretch justify-center gap-1 rounded-full border border-[var(--cm-outline-variant)]/50 p-1 mb-6 w-full max-w-[320px] sm:max-w-[420px] mx-auto"
        >
          {VISIBLE_PRICING_TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              role="tab"
              id={`pricing-tab-${tab.id}`}
              aria-controls={`pricing-panel-${tab.id}`}
              aria-selected={audience === tab.id}
              onClick={() => setAudienceTab(tab.id)}
              className={`flex-1 min-w-0 px-3 sm:px-5 py-2.5 rounded-full text-sm font-semibold transition-all flex flex-col items-center justify-center ${
                audience === tab.id
                  ? "bg-[var(--cm-mint)] text-[var(--cm-on-mint)]"
                  : "text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-on-surface)]"
              }`}
            >
              <span className="whitespace-nowrap">{tab.label}</span>
              <span
                className={`hidden sm:inline text-[10px] font-mono font-normal mt-0.5 ${
                  audience === tab.id ? "text-[var(--cm-on-mint)]/75" : "text-[var(--cm-on-surface-variant)]/60"
                }`}
              >
                {isES ? tab.hint_es : tab.hint_en}
              </span>
            </button>
          ))}
        </div>
        )}

        <p className="text-xs text-[var(--cm-on-surface-variant)]/60 mb-6 max-w-lg mx-auto">
          {isES
            ? "Precios en USD. El equivalente en soles (PEN) es referencial para checkout local."
            : "Prices in USD. PEN equivalent is indicative for local checkout only."}
        </p>

        <div className="landing-section-header">
          <h2 className="section-title">{isES ? activeTab.title_es : activeTab.title_en}</h2>
          <p className="section-intro">{isES ? activeTab.intro_es : activeTab.intro_en}</p>
        </div>

        <div
          id="pricing-panel-build"
          className={audience !== "build" ? "hidden" : undefined}
          aria-hidden={audience !== "build"}
          role="tabpanel"
          aria-labelledby="pricing-tab-build"
        >
          <div className="landing-content-rail grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-6 mt-4">
            {BUILD_VISIBLE_TIERS.map((tier, i) => (
              <motion.div
                key={tier.name}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.06 }}
                id={undefined}
                className="scroll-mt-24"
              >
                <TierCard
                  tier={tier}
                  isES={isES}
                  billing={billing}
                  paymentsLabel={paymentsLabel}
                >
                  {tier.checkoutKind ? (
                    <ProSubscribeButton kind={tier.checkoutKind} />
                  ) : tier.href ? (
                    <a href={tier.href} className="btn-mint w-full">
                      {isES ? tier.cta_es : tier.cta_en}
                    </a>
                  ) : null}
                </TierCard>
              </motion.div>
            ))}
          </div>

          <p className="text-xs text-[var(--cm-on-surface-variant)]/60 landing-content-narrow leading-relaxed mb-4">
            {isES ? (
              <>
                Starter, Pro y Enterprise — límites y facturación en{" "}
                <a href="/docs#billing" className="text-[var(--cm-mint)] underline hover:no-underline">
                  /docs#billing
                </a>
                .
              </>
            ) : (
              <>
                Starter, Pro, and Enterprise — limits and billing in{" "}
                <a href="/docs#billing" className="text-[var(--cm-mint)] underline hover:no-underline">
                  /docs#billing
                </a>
                .
              </>
            )}
          </p>

          <p className="text-xs text-[var(--cm-on-surface-variant)]/60 landing-content-narrow leading-relaxed mb-14">
            {billingFootnote}{" "}
          </p>

          <div className="border-t border-[var(--cm-outline-variant)]/30 pt-12 text-center">
            <p className="text-base text-[var(--cm-on-surface-variant)] mb-4">
              {isES
                ? "¿Necesita límites, SLAs o licencia de datos personalizados?"
                : "Need custom limits, SLAs, or a data license?"}
            </p>
            <a
              href="/contact?topic=enterprise#contact-form"
              className="inline-flex items-center rounded-[10px] border border-[var(--cm-outline-variant)] text-[var(--cm-on-surface-variant)] text-sm font-semibold px-6 py-2.5 hover:border-[var(--cm-action)] hover:text-[var(--cm-action)] transition-all"
            >
              {isES ? "Contáctenos →" : "Contact us →"}
            </a>
          </div>
        </div>

        <div
          id="pricing-panel-procure"
          className={audience !== "procure" ? "hidden" : "brand-mode-operations rounded-2xl border border-[var(--cm-outline-variant)] p-6 sm:p-8 -mx-2 sm:mx-0"}
          aria-hidden={audience !== "procure"}
          role="tabpanel"
          aria-labelledby="pricing-tab-procure"
        >
          <ProcurePricingPanel />
        </div>
      </div>
    </section>
  );
}
