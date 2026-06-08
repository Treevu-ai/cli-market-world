"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import ProSubscribeButton from "@/components/ProSubscribeButton";
import FreeSignupModal from "@/components/FreeSignupModal";
import RetailersPricingPanel from "@/components/RetailersPricingPanel";
import { MARKET_STATS } from "@/lib/marketStats";

type Billing = "monthly" | "annual";
type Audience = "developers" | "retailers";

type Tier = {
  name: string;
  price: string;
  latamPrice?: string;
  annualPrice?: string;
  annualLatamPrice?: string;
  period_es?: string;
  period_en?: string;
  f_es: string[];
  f_en: string[];
  cta_es: string;
  cta_en: string;
  dark?: boolean;
  featured?: boolean;
  starterPick?: boolean;
  href?: string;
  proNote_es?: string;
  proNote_en?: string;
};

const tiers: Tier[] = [
  {
    name: "Free",
    price: "$0",
    latamPrice: "S/0",
    period_es: "sin costo",
    period_en: "no cost",
    f_es: [
      "1,000 consultas / día",
      "1 clave API (lectura)",
      `${MARKET_STATS.mcpTools} herramientas MCP`,
      "Búsqueda multi-retailer",
    ],
    f_en: [
      "1,000 requests / day",
      "1 API key (read-only)",
      `${MARKET_STATS.mcpTools} MCP tools`,
      "Multi-retailer search",
    ],
    cta_es: "Empezar",
    cta_en: "Get started",
    href: MARKET_STATS.pypiUrl,
  },
  {
    name: "Pro",
    price: "$39",
    latamPrice: "S/149",
    annualPrice: "$390",
    annualLatamPrice: "S/1,490",
    period_es: "/ mes",
    period_en: "/ month",
    f_es: [
      "10,000 consultas / día",
      "10 claves API (lectura y escritura)",
      `Checkout ${MARKET_STATS.paymentsLabel} + full MCP`,
      "10 alertas · historial 12 meses",
    ],
    f_en: [
      "10,000 requests / day",
      "10 API keys (read + write)",
      `Checkout ${MARKET_STATS.paymentsLabel} + full MCP`,
      "10 alerts · 12-month history",
    ],
    cta_es: "Configurar suscripción",
    cta_en: "Set up subscription",
    featured: true,
    proNote_es: `Pagos: ${MARKET_STATS.paymentsLabel} — mismos canales para suscripción Pro y checkout retail. Facturación USD · Sinapsis Innovadora S.A.C. · RUC 20613045563.`,
    proNote_en: `Payments: ${MARKET_STATS.paymentsLabel} — same channels for Pro billing and retail checkout. USD invoicing · Sinapsis Innovadora S.A.C. · tax ID 20613045563.`,
  },
  {
    name: "Enterprise",
    price: "A medida",
    period_es: "",
    period_en: "",
    f_es: [
      "Límites y SLAs personalizados",
      "Webhooks + endpoints dedicados",
      "Licencia de datos ampliada",
      "Soporte 24/7 + consultoría",
    ],
    f_en: [
      "Custom limits and SLAs",
      "Webhooks + dedicated endpoints",
      "Extended data license",
      "24/7 support + consulting",
    ],
    cta_es: "Contactar",
    cta_en: "Contact us",
    dark: true,
    href: "/#contact-general",
  },
];

function resolveAudienceFromLocation(): Audience {
  if (typeof window === "undefined") return "developers";
  const hash = window.location.hash.replace("#", "");
  const params = new URLSearchParams(window.location.search);
  if (hash === "retailers" || params.get("audience") === "retailers") return "retailers";
  return "developers";
}

function TierCard({
  tier,
  isES,
  billing,
  children,
  footerNote,
  className,
}: {
  tier: Tier;
  isES: boolean;
  billing: Billing;
  children?: React.ReactNode;
  footerNote?: string;
  className?: string;
}) {
  const isAnnual = billing === "annual";
  const displayPrice = isAnnual && tier.annualPrice ? tier.annualPrice : tier.price;
  const displayLatam = isAnnual && tier.annualLatamPrice ? tier.annualLatamPrice : tier.latamPrice;
  const period =
    isAnnual && tier.annualPrice
      ? isES
        ? "/ año"
        : "/ year"
      : isES
        ? tier.period_es
        : tier.period_en;

  return (
    <div
      className={`h-full min-h-0 md:min-h-[22rem] rounded-2xl p-5 sm:p-6 text-left flex flex-col ${
        tier.dark || tier.featured ? "energy-border-active card-cyber" : "card-cyber"
      } ${className ?? ""}`}
    >
      {tier.starterPick && (
        <span className="self-center mb-4 border border-[var(--cm-mint)]/50 text-[var(--cm-mint)] text-xs font-semibold px-4 py-1 rounded-full whitespace-nowrap">
          {isES ? "Primer upgrade" : "First upgrade"}
        </span>
      )}
      {tier.featured && (
        <span className="self-center mb-4 bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-xs font-semibold px-4 py-1 rounded-full whitespace-nowrap">
          {isES ? "Más popular" : "Most popular"}
        </span>
      )}
      <h3 className={`text-lg font-bold ${tier.dark ? "text-[var(--cm-mint)]" : "text-white"}`}>{tier.name}</h3>
      <div className="mt-3 mb-1">
        <span className="text-3xl font-black break-all tabular-nums text-white">{displayPrice}</span>
        {period && (
          <span className="text-sm ml-1 text-[var(--cm-on-surface-variant)]">{period}</span>
        )}
      </div>
      {displayLatam && displayLatam !== "S/0" && (
        <p className="text-xs text-[var(--cm-on-surface-variant)]/60 mb-1 font-mono">
          {displayLatam}
          {period ? ` ${period}` : ""}
        </p>
      )}
      {isAnnual && tier.annualPrice ? (
        <p className="text-xs text-[var(--cm-mint)] mb-4 font-mono min-h-[1.25rem]">
          {isES ? "2 meses gratis" : "2 months free"}
        </p>
      ) : (
        <div className="mb-4 min-h-[1.25rem]" aria-hidden="true" />
      )}
      <ul className="space-y-3 mb-6 flex-1">
        {(isES ? tier.f_es : tier.f_en).map((f, i) => (
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
      <div className="mt-auto space-y-3">
        {children ? (
          children
        ) : (
          <a href={tier.href ?? "#"} className="btn-mint w-full">
            {isES ? tier.cta_es : tier.cta_en}
          </a>
        )}
        {footerNote && (
          <p className="text-xs text-[var(--cm-on-surface-variant)]/60 text-center font-mono leading-relaxed pt-1 border-t border-[var(--cm-outline-variant)]/20">
            {footerNote}
          </p>
        )}
      </div>
    </div>
  );
}

export default function Pricing() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [billing, setBilling] = useState<Billing>("monthly");
  const [audience, setAudience] = useState<Audience>("developers");
  const [freeModalOpen, setFreeModalOpen] = useState(false);

  useEffect(() => {
    const syncFromLocation = () => {
      const next = resolveAudienceFromLocation();
      setAudience(next);
      const hash = window.location.hash.replace("#", "");
      if (hash === "pro-checkout" || hash === "pricing-build") {
        requestAnimationFrame(() => {
          document.getElementById("pro-checkout")?.scrollIntoView({ behavior: "smooth", block: "start" });
        });
      } else if (hash === "retailers") {
        requestAnimationFrame(() => {
          document.getElementById("retailers")?.scrollIntoView({ behavior: "smooth", block: "start" });
        });
      }
    };
    syncFromLocation();
    window.addEventListener("hashchange", syncFromLocation);
    return () => window.removeEventListener("hashchange", syncFromLocation);
  }, []);

  const setAudienceTab = (tab: Audience) => {
    setAudience(tab);
    const hash = tab === "retailers" ? "#retailers" : "#pricing";
    if (window.location.hash !== hash) {
      window.history.replaceState(null, "", hash);
    }
  };

  return (
    <section id="pricing" className="landing-section landing-section-alt animate-fade-in scroll-mt-24">
      <div className="landing-container-wide text-center">
        <p className="section-eyebrow mb-4 text-[var(--cm-mint)]">
          {isES ? "Planes" : "Plans"}
        </p>

        <div className="inline-flex items-center gap-1 rounded-full border border-[var(--cm-outline-variant)]/50 p-1 mb-8">
          <button
            type="button"
            onClick={() => setAudienceTab("developers")}
            className={`px-5 py-2 rounded-full text-sm font-semibold transition-all ${
              audience === "developers"
                ? "bg-[var(--cm-mint)] text-[var(--cm-on-mint)]"
                : "text-[var(--cm-on-surface-variant)] hover:text-white"
            }`}
          >
            {isES ? "Developers" : "Developers"}
          </button>
          <button
            type="button"
            onClick={() => setAudienceTab("retailers")}
            className={`px-5 py-2 rounded-full text-sm font-semibold transition-all ${
              audience === "retailers"
                ? "bg-[var(--cm-mint)] text-[var(--cm-on-mint)]"
                : "text-[var(--cm-on-surface-variant)] hover:text-white"
            }`}
          >
            {isES ? "Retailers" : "Retailers"}
          </button>
        </div>

        <div className={audience !== "developers" ? "hidden" : undefined} aria-hidden={audience !== "developers"}>
            <h2 className="section-title">
              {isES ? "Construido para escalar." : "Built to scale."}
            </h2>
            <p className="section-intro">
              {isES
                ? "Elige tu punto de entrada. Migra cuando crezcas sin cambiar de integración."
                : "Pick your entry point. Migrate as you grow without changing integrations."}
            </p>

            <div className="inline-flex items-center gap-1 rounded-full border border-[var(--cm-outline-variant)]/50 p-1 mb-12">
              <button
                type="button"
                onClick={() => setBilling("monthly")}
                className={`px-4 py-1.5 rounded-full text-sm font-semibold transition-all ${
                  billing === "monthly"
                    ? "bg-[var(--cm-surface-high)] text-white"
                    : "text-[var(--cm-on-surface-variant)] hover:text-white"
                }`}
              >
                {isES ? "Mensual" : "Monthly"}
              </button>
              <button
                type="button"
                onClick={() => setBilling("annual")}
                className={`px-4 py-1.5 rounded-full text-sm font-semibold transition-all flex items-center gap-2 ${
                  billing === "annual"
                    ? "bg-[var(--cm-surface-high)] text-white"
                    : "text-[var(--cm-on-surface-variant)] hover:text-white"
                }`}
              >
                {isES ? "Anual" : "Annual"}
                <span className="text-[10px] font-bold text-[var(--cm-mint)] bg-[var(--cm-mint)]/10 px-1.5 py-0.5 rounded-full">
                  −17%
                </span>
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 max-w-7xl mx-auto mb-14">
              {tiers.map((tier, i) => (
                <motion.div
                  key={tier.name}
                  initial={{ opacity: 0, y: 16 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: i * 0.08 }}
                  className={tier.name === "Pro" ? "sm:col-span-2 lg:col-span-1" : undefined}
                >
                  <TierCard
                    tier={tier}
                    isES={isES}
                    billing={billing}
                    className={tier.name === "Pro" ? "lg:min-h-[28rem]" : undefined}
                    footerNote={
                      tier.name === "Pro" && tier.proNote_es
                        ? isES
                          ? tier.proNote_es
                          : tier.proNote_en
                        : undefined
                    }
                  >
                    {tier.name === "Pro" ? (
                      <div id="pro-checkout" className="scroll-mt-24 space-y-3">
                        <ProSubscribeButton />
                      </div>
                    ) : tier.name === "Free" ? (
                      <button type="button" onClick={() => setFreeModalOpen(true)} className="btn-mint w-full">
                        {isES ? tier.cta_es : tier.cta_en}
                      </button>
                    ) : null}
                  </TierCard>
                </motion.div>
              ))}
            </div>

            <FreeSignupModal open={freeModalOpen} onClose={() => setFreeModalOpen(false)} />

            <div className="border-t border-[var(--cm-outline-variant)]/30 pt-12 text-center">
              <p className="text-base text-[var(--cm-on-surface-variant)] mb-4">
                {isES
                  ? "¿Necesita límites, SLAs o licencia de datos personalizados?"
                  : "Need custom limits, SLAs, or a data license?"}
              </p>
              <a
                href="/#contact-general"
                className="inline-flex items-center rounded-3xl border border-[var(--cm-outline-variant)] text-white text-sm font-semibold px-6 py-2.5 hover:border-[var(--cm-mint)] hover:text-[var(--cm-mint)] transition-all"
              >
                {isES ? "Contáctenos →" : "Contact us →"}
              </a>
            </div>
        </div>

        <div className={audience !== "retailers" ? "hidden" : undefined} aria-hidden={audience !== "retailers"}>
          <RetailersPricingPanel />
        </div>
      </div>
    </section>
  );
}