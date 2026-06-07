"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import ProSubscribeButton from "@/components/ProSubscribeButton";
import StarterSubscribeButton from "@/components/StarterSubscribeButton";
import FreeSignupModal from "@/components/FreeSignupModal";
import { MARKET_STATS } from "@/lib/marketStats";

type Billing = "monthly" | "annual";

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
    href: "https://pypi.org/project/cli-market/",
  },
  {
    name: "Starter",
    price: "$29",
    latamPrice: "S/109",
    annualPrice: "$290",
    annualLatamPrice: "S/1,090",
    period_es: "/ mes",
    period_en: "/ month",
    f_es: [
      "5,000 consultas / día",
      "3 claves API (lectura)",
      "3 alertas de precio",
      "Exportación CSV · soporte 48h",
    ],
    f_en: [
      "5,000 requests / day",
      "3 API keys (read-only)",
      "3 price alerts",
      "CSV export · email support 48h",
    ],
    cta_es: "Activar Starter",
    cta_en: "Activate Starter",
  },
  {
    name: "Pro",
    price: "$79",
    latamPrice: "S/299",
    annualPrice: "$790",
    annualLatamPrice: "S/2,990",
    period_es: "/ mes",
    period_en: "/ month",
    f_es: [
      "10,000 consultas / día",
      "10 claves API (lectura y escritura)",
      `Checkout ${MARKET_STATS.paymentsLabel}`,
      "10 alertas · historial 12 meses",
    ],
    f_en: [
      "10,000 requests / day",
      "10 API keys (read + write)",
      `Checkout ${MARKET_STATS.paymentsLabel}`,
      "10 alerts · 12-month history",
    ],
    cta_es: "Configurar suscripción",
    cta_en: "Set up subscription",
    featured: true,
    proNote_es:
      `Pagos: ${MARKET_STATS.paymentsLabel}. PayPal con activación automática vía webhook. Facturación PEN · RUC 20613045563.`,
    proNote_en:
      `Payments: ${MARKET_STATS.paymentsLabel}. PayPal auto-activation via webhook. PEN invoicing · tax ID 20613045563.`,
  },
  {
    name: "Builder",
    price: "$149",
    latamPrice: "S/565",
    annualPrice: "$1,490",
    annualLatamPrice: "S/5,650",
    period_es: "/ mes",
    period_en: "/ month",
    f_es: [
      "50,000 consultas / día",
      "25 claves API · white-label",
      "Intelligence API completa (34 indicadores)",
      "Alertas y exportación ilimitadas",
    ],
    f_en: [
      "50,000 requests / day",
      "25 API keys · white-label",
      "Full Intelligence API (34 indicators)",
      "Unlimited alerts & export",
    ],
    cta_es: "Construir con CLI Market",
    cta_en: "Build with CLI Market",
    href: "/#contact-general",
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

function TierCard({
  tier,
  isES,
  billing,
  children,
  footerNote,
}: {
  tier: Tier;
  isES: boolean;
  billing: Billing;
  children?: React.ReactNode;
  footerNote?: string;
}) {
  const isAnnual = billing === "annual";
  const displayPrice = isAnnual && tier.annualPrice ? tier.annualPrice : tier.price;
  const displayLatam = isAnnual && tier.annualLatamPrice ? tier.annualLatamPrice : tier.latamPrice;
  const period = isAnnual && tier.annualPrice
    ? (isES ? "/ año" : "/ year")
    : (isES ? tier.period_es : tier.period_en);

  return (
    <div
      className={`h-full min-h-0 md:min-h-[22rem] rounded-2xl p-5 sm:p-6 text-left flex flex-col ${
        tier.dark
          ? "energy-border-active card-cyber"
          : tier.featured
            ? "energy-border-active card-cyber"
            : "card-cyber"
      }`}
    >
      {tier.featured && (
        <span className="self-center mb-4 bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-xs font-semibold px-4 py-1 rounded-full whitespace-nowrap">
          {isES ? "Más popular" : "Most popular"}
        </span>
      )}
      <h3 className={`text-lg font-bold ${tier.dark ? "text-[var(--cm-mint)]" : "text-white"}`}>
        {tier.name}
      </h3>
      <div className="mt-3 mb-1">
        <span className="text-3xl font-black break-all tabular-nums text-white">
          {displayPrice}
        </span>
        {period && (
          <span className="text-sm ml-1 text-[var(--cm-on-surface-variant)]">
            {period}
          </span>
        )}
      </div>
      {displayLatam && displayLatam !== "S/0" && (
        <p className="text-xs text-[var(--cm-on-surface-variant)]/60 mb-1 font-mono">
          {displayLatam}{period ? ` ${period}` : ""}
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
          <li key={i} className="flex items-start gap-2.5 text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
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
          <a
            href={tier.href ?? "#"}
            className="btn-mint w-full"
          >
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

const proTier = tiers.find((t) => t.name === "Pro")!;
const starterTier = tiers.find((t) => t.name === "Starter")!;

export default function Pricing() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [billing, setBilling] = useState<Billing>("monthly");
  const [freeModalOpen, setFreeModalOpen] = useState(false);

  const scrollToProCheckout = () => {
    document.getElementById("pro-checkout")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };
  const scrollToStarterCheckout = () => {
    document.getElementById("starter-checkout")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <section id="pricing" className="landing-section-alt animate-fade-in">
      <div className="landing-container-wide text-center">
        <p className="section-eyebrow mb-4 text-[var(--cm-mint)]">
          {isES ? "Planes" : "Plans"}
        </p>
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

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5 max-w-7xl mx-auto mb-14">
          {tiers.map((tier, i) => (
            <motion.div
              key={tier.name}
              id={tier.name === "Builder" ? "pricing-build" : undefined}
              className={tier.name === "Builder" ? "scroll-mt-24" : undefined}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
            >
              <TierCard
                tier={tier}
                isES={isES}
                billing={billing}
              >
                {tier.name === "Pro" ? (
                  <button type="button" onClick={scrollToProCheckout} className="btn-mint w-full">
                    {isES ? tier.cta_es : tier.cta_en} ↓
                  </button>
                ) : tier.name === "Starter" ? (
                  <button type="button" onClick={scrollToStarterCheckout} className="btn-mint w-full">
                    {isES ? tier.cta_es : tier.cta_en} ↓
                  </button>
                ) : tier.name === "Free" ? (
                  <button
                    onClick={() => setFreeModalOpen(true)}
                    className="btn-mint w-full"
                  >
                    {isES ? tier.cta_es : tier.cta_en}
                  </button>
                ) : null}
              </TierCard>
            </motion.div>
          ))}
        </div>

        <div
          id="starter-checkout"
          className="scroll-mt-24 max-w-4xl mx-auto mb-10 text-left"
        >
          <div className="card-cyber p-6 sm:p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-10">
              <div className="space-y-4">
                <p className="section-eyebrow text-[var(--cm-mint)]">Starter</p>
                <h3 className="text-xl font-bold text-white">
                  {isES ? "Suscripción Starter — USD 29/mes" : "Starter subscription — USD 29/mo"}
                </h3>
                <ul className="space-y-2 text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
                  {(isES ? starterTier.f_es : starterTier.f_en).map((f) => (
                    <li key={f} className="flex items-start gap-2">
                      <span className="text-[var(--cm-mint)] shrink-0">✓</span>
                      {f}
                    </li>
                  ))}
                </ul>

              </div>
              <div>
                <StarterSubscribeButton />
              </div>
            </div>
          </div>
        </div>

        <div
          id="pro-checkout"
          className="scroll-mt-24 max-w-4xl mx-auto mb-14 text-left"
        >
          <div className="card-cyber energy-border-active p-6 sm:p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-10">
              <div className="space-y-4">
                <p className="section-eyebrow text-[var(--cm-mint)]">Pro</p>
                <h3 className="text-xl font-bold text-white">
                  {isES ? "Suscripción Pro — USD 79/mes" : "Pro subscription — USD 79/mo"}
                </h3>
                <ul className="space-y-2 text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
                  {(isES ? proTier.f_es : proTier.f_en).map((f) => (
                    <li key={f} className="flex items-start gap-2">
                      <span className="text-[var(--cm-mint)] shrink-0">✓</span>
                      {f}
                    </li>
                  ))}
                </ul>
                {proTier.proNote_es && (
                  <p className="text-xs text-[var(--cm-on-surface-variant)]/70 font-mono leading-relaxed pt-3 border-t border-[var(--cm-outline-variant)]/25">
                    {isES ? proTier.proNote_es : proTier.proNote_en}
                  </p>
                )}
              </div>
              <div>
                <ProSubscribeButton />
              </div>
            </div>
          </div>
        </div>

        <FreeSignupModal open={freeModalOpen} onClose={() => setFreeModalOpen(false)} />

        <div className="border-t border-[var(--cm-outline-variant)]/30 pt-12 text-center">
          <p className="text-base text-[var(--cm-on-surface-variant)] mb-4">
            {isES
              ? "¿Necesita límites, SLAs o licencia de datos personalizados?"
              : "Need custom limits, SLAs, or a data license?"}
          </p>
          <a href="/#contact-general" className="inline-flex items-center rounded-3xl border border-[var(--cm-outline-variant)] text-white text-sm font-semibold px-6 py-2.5 hover:border-[var(--cm-mint)] hover:text-[var(--cm-mint)] transition-all">
            {isES ? "Contáctenos →" : "Contact us →"}
          </a>
        </div>
      </div>
    </section>
  );
}