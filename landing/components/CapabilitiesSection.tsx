"use client";

import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

const CAPABILITIES = [
  {
    slug: "price-engine",
    icon: "⚡",
    title_es: "Price Engine",
    title_en: "Price Engine",
    description_es: `Precios normalizados por kg/L en ${MARKET_STATS.retailersVerified} retailers de ${MARKET_STATS.countries} países. Cada ciclo de ${MARKET_STATS.pricesRefreshHours}h pasa por validación de calidad: sin valores atípicos, sin datos stale.`,
    description_en: `Prices normalized per kg/L across ${MARKET_STATS.retailersVerified} retailers in ${MARKET_STATS.countries} countries. Every ${MARKET_STATS.pricesRefreshHours}h cycle passes quality validation: no outliers, no stale data.`,
    href: "#how-it-works",
  },
  {
    slug: "agent-tools",
    icon: "🤖",
    title_es: "Agent Tools",
    title_en: "Agent Tools",
    description_es: `${MARKET_STATS.mcpTools} tools MCP (perfil default) — optimize, basket, compare, intel, alertas de precio. Una llamada a market_optimize_purchase cubre canasta, TCO y sustitutos. Sin scraping ni integraciones manuales.`,
    description_en: `${MARKET_STATS.mcpTools} MCP tools (default profile) — optimize, basket, compare, intel, price alerts. One market_optimize_purchase call covers basket, TCO, and substitutes. No scraping or manual integrations.`,
    href: "/tools",
  },
  {
    slug: "procurement",
    icon: "🛒",
    title_es: "Procurement",
    title_en: "Procurement",
    description_es: "Canasta multi-retailer con flujo de aprobaciones, control presupuestario y checkout. Tu equipo compara en segundos y cierra con Yape o PayPal — sin WhatsApp, sin hojas de cálculo.",
    description_en: "Multi-retailer basket with approval workflows, budget control, and checkout. Your team compares in seconds and closes with Yape or PayPal — no WhatsApp, no spreadsheets.",
    href: "/#procure",
  },
  {
    slug: "intelligence",
    icon: "📈",
    title_es: "Intelligence",
    title_en: "Intelligence",
    description_es: `${MARKET_STATS.indicatorsCount} indicadores de mercado — tendencias de precios, spreads de calidad, inflación desde góndola. Para analistas y fondos que necesitan datos de retail LATAM antes que el IPC.`,
    description_en: `${MARKET_STATS.indicatorsCount} market indicators — price trends, quality spreads, shelf-price inflation. For analysts and funds that need LATAM retail data before CPI.`,
    href: "/docs#intel",
  },
];

export default function CapabilitiesSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="capabilities" className="landing-section animate-fade-in bg-[var(--cm-surface)]">
      <div className="landing-container-wide text-center">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-4">{isES ? "Capacidades" : "Capabilities"}</p>
          <h2 className="section-title">{isES ? "Todo lo que necesita tu agente." : "Everything your agent needs."}</h2>
          <p className="section-intro">
            {isES
              ? "Una API. Cuatro superficies. Mismos precios verificados."
              : "One API. Four surfaces. Same verified prices."}
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 landing-content-rail text-left mb-10">
          {CAPABILITIES.map((cap, i) => (
            <motion.a
              key={cap.slug}
              href={cap.href}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              className="card-cyber card-cyber-interactive p-6 flex flex-col gap-3 text-left no-underline"
            >
              <span className="text-2xl" aria-hidden="true">{cap.icon}</span>
              <h3 className="text-sm font-bold text-[var(--cm-on-surface)]">
                {isES ? cap.title_es : cap.title_en}
              </h3>
              <p className="text-sm leading-relaxed text-[var(--cm-on-surface-variant)] flex-1">
                {isES ? cap.description_es : cap.description_en}
              </p>
              <span className="text-xs font-mono text-[var(--cm-mint)]">
                {isES ? "Explorar →" : "Explore →"}
              </span>
            </motion.a>
          ))}
        </div>
      </div>
    </section>
  );
}
