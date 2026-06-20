"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import ProSubscribeButton from "@/components/ProSubscribeButton";
import BillingCheckoutTrigger from "@/components/BillingCheckoutTrigger";
import FreeSignupModal from "@/components/FreeSignupModal";
import ProcurePricingPanel from "@/components/ProcurePricingPanel";
import { MARKET_STATS } from "@/lib/marketStats";
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
  BUILD_TIER_FREE,
  BUILD_TIER_STARTER,
  BUILD_TIER_PRO,
  formatReqLimit,
} from "@/lib/buildPricingTiers";

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
    name: BUILD_TIER_FREE.name,
    price: "$0",
    period_es: "sin tarjeta",
    period_en: "no card",
    f_es: BUILD_TIER_FREE.features_es,
    f_en: BUILD_TIER_FREE.features_en,
    cta_es: "Empezar gratis",
    cta_en: "Start free",
    href: MARKET_STATS.pypiUrl,
  },
  {
    name: BUILD_TIER_STARTER.name,
    price: `$${BUILD_TIER_STARTER.priceUsd}`,
    latamPrice: BUILD_TIER_STARTER.latamPricePen,
    period_es: "/ mes · 14 días de prueba",
    period_en: "/ mo · 14-day trial",
    f_es: BUILD_TIER_STARTER.features_es,
    f_en: BUILD_TIER_STARTER.features_en,
    cta_es: "Prueba gratis 14 días",
    cta_en: "Free 14-day trial",
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
    href: "/#contact-general",
  },
];

const BUILD_VISIBLE_TIERS = tiers.filter((t) =>
  ["Starter", "Pro", "Enterprise"].includes(t.name),
);
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

      <h3 className={`text-lg font-bold ${tier.dark ? "text-[var(--cm-mint)]" : "text-gray-900"}`}>
        {tier.name}
      </h3>

      <div className="mt-3 mb-1 flex flex-wrap items-baseline gap-x-2 gap-y-0">
        {tier.compareAt && (
          <span className="text-lg text-[var(--cm-on-surface-variant)]/50 line-through tabular-nums">
            {tier.compareAt}
          </span>
        )}
        <span className="text-3xl font-black tabular-nums text-gray-900">{displayPrice}</span>
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

export default function Pricing() {
  const { lang } = useLang();
  const isES = lang === "es";
  const billing: Billing = "monthly";
  const [audience, setAudience] = useState<PricingAudience>("procure");
  const [freeModalOpen, setFreeModalOpen] = useState(false);
  const paymentsLabel = usePaymentsChannels(isES);
  const billingFootnote = usePricingBillingFootnote(isES);

  const activeTab = PRICING_TABS.find((t) => t.id === audience)!;

  useEffect(() => {
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
      } else if (hashId === "procure") {
        scrollToPricingSection("procure");
      } else if (state) {
        scrollToPricingSection(returnAudience === "procure" ? "procure" : undefined);
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
    <section id="pricing" className="landing-section landing-section-alt landing-section-glow animate-fade-in scroll-mt-24">
      <div className="landing-container-wide text-center">
        <p className="section-eyebrow section-eyebrow-action mb-4">
          {isES ? "Planes" : "Plans"}
        </p>

        <PaymentReturnBanner />

        <div
          role="tablist"
          aria-label={isES ? "Líneas de producto" : "Product lines"}
          className="flex flex-row flex-nowrap items-stretch justify-center gap-1 rounded-full border border-[var(--cm-outline-variant)]/50 p-1 mb-6 w-full max-w-[320px] sm:max-w-[420px] mx-auto"
        >
          {PRICING_TABS.map((tab) => (
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
                  : "text-[var(--cm-on-surface-variant)] hover:text-gray-900"
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
          <div className="landing-content-rail grid grid-cols-1 lg:grid-cols-3 gap-5 mb-6 mt-4">
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
                ¿Plan intermedio?{" "}
                <span className="text-[var(--cm-mint)]">{STARTER_TIER.price}/mes Starter</span> —{" "}
                {formatReqLimit(BUILD_TIER_STARTER.reqLimit, true)}, export CSV, sin checkout. Pro estándar{" "}
                <span className="text-[var(--cm-mint)]">{PRO_TIER.price}/mes</span>{" "}
                <BillingCheckoutTrigger
                  kind={{ type: "build-pro" }}
                  className="inline-flex align-middle ml-1 mr-0.5 rounded-full border border-[var(--cm-mint)]/40 px-2.5 py-0.5 text-[11px] font-semibold text-[var(--cm-mint)] hover:bg-[var(--cm-mint)]/10 transition-colors"
                  label_es="Elegir Pro →"
                  label_en="Choose Pro →"
                />{" "}
                o <span className="text-[var(--cm-mint)]">{PRO_TIER.annualPrice}/año</span>{" "}
                <BillingCheckoutTrigger
                  kind={{ type: "build-pro", annual: true }}
                  className="inline-flex align-middle ml-1 rounded-full border border-[var(--cm-mint)]/40 px-2.5 py-0.5 text-[11px] font-semibold text-[var(--cm-mint)] hover:bg-[var(--cm-mint)]/10 transition-colors"
                  label_es="Pro anual →"
                  label_en="Pro annual →"
                />
                . Detalle en{" "}
                <a href="/docs#billing" className="text-[var(--cm-mint)] underline hover:no-underline">
                  /docs#billing
                </a>
                .
              </>
            ) : (
              <>
                Need a mid-tier?{" "}
                <span className="text-[var(--cm-mint)]">{STARTER_TIER.price}/mo Starter</span> —{" "}
                {formatReqLimit(BUILD_TIER_STARTER.reqLimit, false)}, CSV export, no checkout. Standard Pro{" "}
                <span className="text-[var(--cm-mint)]">{PRO_TIER.price}/mo</span>{" "}
                <BillingCheckoutTrigger
                  kind={{ type: "build-pro" }}
                  className="inline-flex align-middle ml-1 mr-0.5 rounded-full border border-[var(--cm-mint)]/40 px-2.5 py-0.5 text-[11px] font-semibold text-[var(--cm-mint)] hover:bg-[var(--cm-mint)]/10 transition-colors"
                  label_es="Elegir Pro →"
                  label_en="Choose Pro →"
                />{" "}
                or <span className="text-[var(--cm-mint)]">{PRO_TIER.annualPrice}/yr</span>{" "}
                <BillingCheckoutTrigger
                  kind={{ type: "build-pro", annual: true }}
                  className="inline-flex align-middle ml-1 rounded-full border border-[var(--cm-mint)]/40 px-2.5 py-0.5 text-[11px] font-semibold text-[var(--cm-mint)] hover:bg-[var(--cm-mint)]/10 transition-colors"
                  label_es="Pro anual →"
                  label_en="Pro annual →"
                />
                . Details in{" "}
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

          <FreeSignupModal open={freeModalOpen} onClose={() => setFreeModalOpen(false)} />

          <div className="border-t border-[var(--cm-outline-variant)]/30 pt-12 text-center">
            <p className="text-base text-[var(--cm-on-surface-variant)] mb-4">
              {isES
                ? "¿Necesita límites, SLAs o licencia de datos personalizados?"
                : "Need custom limits, SLAs, or a data license?"}
            </p>
            <a
              href="/#contact-general"
              className="inline-flex items-center rounded-3xl border border-gray-300 text-gray-700 text-sm font-semibold px-6 py-2.5 hover:border-indigo-400 hover:text-indigo-600 transition-all"
            >
              {isES ? "Contáctenos →" : "Contact us →"}
            </a>
          </div>
        </div>

        <div
          id="pricing-panel-procure"
          className={audience !== "procure" ? "hidden" : undefined}
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
