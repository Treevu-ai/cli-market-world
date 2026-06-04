"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import ProSubscribeButton from "@/components/ProSubscribeButton";
import FreeSignupModal from "@/components/FreeSignupModal";
import { MARKET_STATS } from "@/lib/marketStats";

type Tier = {
  name: string;
  price: string;
  latamPrice?: string;
  annualPrice?: string;
  annualLatamPrice?: string;
  trial_es?: string;
  trial_en?: string;
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
    price: "$9",
    latamPrice: "S/34",
    annualPrice: "$90",
    annualLatamPrice: "S/340",
    period_es: "/ mes",
    period_en: "/ month",
    trial_es: "14 dias gratis",
    trial_en: "14 days free",
    f_es: [
      "1,000 consultas / dia",
      "3 claves API (lectura)",
      "Exportacion JSON",
      "Soporte email 48h",
    ],
    f_en: [
      "1,000 requests / day",
      "3 API keys (read-only)",
      "JSON export",
      "Email support 48h",
    ],
    cta_es: "Probar gratis",
    cta_en: "Try free",
  },
  {
    name: "Pro",
    price: "$49",
    latamPrice: "S/185",
    annualPrice: "$490",
    annualLatamPrice: "S/1,850",
    trial_es: "14 dias gratis",
    trial_en: "14 days free",
    period_es: "/ mes",
    period_en: "/ month",
    f_es: [
      "10,000 consultas / día",
      "10 claves API (lectura y escritura)",
      "Exportación de precios (JSON/CSV)",
      "Checkout con PayPal + Yape/Plin",
    ],
    f_en: [
      "10,000 requests / day",
      "10 API keys (read + write)",
      "Price data export (JSON/CSV)",
      "Checkout with PayPal + Yape/Plin",
    ],
    cta_es: "Obtener Pro",
    cta_en: "Get Pro",
    featured: true,
    proNote_es:
      "Para builders y agentes en producción. Facturación en soles con RUC 20613045563.",
    proNote_en:
      "For builders and agents in production. Invoicing in PEN with tax ID 20613045563.",
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
    href: "#contact-general",
  },
];

function TierCard({
  tier,
  isES,
  children,
}: {
  tier: Tier;
  isES: boolean;
  children?: React.ReactNode;
}) {
  return (
    <div
      className={`h-full rounded-2xl p-6 text-left flex flex-col relative ${
        tier.dark
          ? "energy-border-active card-cyber"
          : tier.featured
            ? "energy-border-active card-cyber"
            : "card-cyber"
      }`}
    >
      {tier.featured && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-xs font-semibold px-4 py-1 rounded-full whitespace-nowrap">
          {isES ? "Más popular" : "Most popular"}
        </span>
      )}
      <h3 className={`text-lg font-bold ${tier.dark ? "text-[var(--cm-mint)]" : "text-white"}`}>
        {tier.name}
      </h3>
      <div className="mt-3 mb-5">
        <span className="text-3xl font-black break-all tabular-nums text-white">
          {tier.price}
        </span>
        {(tier.period_es || tier.period_en) && (
          <span className="text-sm ml-1 text-[var(--cm-on-surface-variant)]">
            {isES ? tier.period_es : tier.period_en}
          </span>
        )}
      </div>
      <ul className="space-y-2.5 mb-6 flex-1">
        {(isES ? tier.f_es : tier.f_en).map((f, i) => (
          <li key={i} className="flex items-start gap-2.5 text-sm text-[var(--cm-on-surface-variant)]">
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
    </div>
  );
}

export default function Pricing() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [freeModalOpen, setFreeModalOpen] = useState(false);
  const [starterModalOpen, setStarterModalOpen] = useState(false);

  return (
    <section id="pricing" className="landing-section-alt animate-fade-in">
      <div className="landing-container-wide text-center">
        <p className="section-eyebrow mb-4 text-[var(--cm-mint)]">
          {isES ? "Planes" : "Plans"}
        </p>
        <h2 className="section-title mb-2">
          {isES ? "Construido para escalar." : "Built to scale."}
        </h2>
        <p className="text-sm text-[var(--cm-on-surface-variant)] max-w-xl mx-auto mb-12">
          {isES
            ? "Elige tu punto de entrada. Migra cuando crezcas sin cambiar de integración."
            : "Pick your entry point. Migrate as you grow without changing integrations."}
        </p>

        {/* Pricing cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 max-w-6xl mx-auto mb-12">
          {tiers.map((tier, i) => (
            <motion.div key={tier.name} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.4, delay: i * 0.08 }}>
              <TierCard tier={tier} isES={isES}>
                {tier.name === "Pro" ? (
                  <div id="pro-checkout" className="scroll-mt-24">
                    <ProSubscribeButton />
                  </div>
                ) : tier.name === "Starter" ? (
                  <button
                    onClick={() => setStarterModalOpen(true)}
                    className="btn-mint w-full"
                  >
                    {isES ? tier.cta_es : tier.cta_en}
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
              {tier.name === "Pro" && tier.proNote_es && (
                <p className="text-xs text-[var(--cm-on-surface-variant)]/60 mt-2 text-center font-mono">
                  {isES ? tier.proNote_es : tier.proNote_en}
                </p>
              )}
            </motion.div>
          ))}
        </div>

        <FreeSignupModal open={freeModalOpen} onClose={() => setFreeModalOpen(false)} />
        <FreeSignupModal open={starterModalOpen} onClose={() => setStarterModalOpen(false)} plan="starter" />

        {/* Enterprise CTA */}
        <div className="border-t border-[var(--cm-outline-variant)]/30 pt-10 text-center">
          <p className="text-sm text-[var(--cm-on-surface-variant)] mb-3">
            {isES
              ? "¿Necesitas límites, SLAs o licencia de datos personalizados?"
              : "Need custom limits, SLAs, or a data license?"}
          </p>
          <a href="#contact-general" className="inline-flex items-center rounded-3xl border border-[var(--cm-outline-variant)] text-white text-sm font-semibold px-6 py-2.5 hover:border-[var(--cm-mint)] hover:text-[var(--cm-mint)] transition-all">
            {isES ? "Contáctanos →" : "Contact us →"}
          </a>
        </div>
      </div>
    </section>
  );
}
