"use client";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

const cases = [
  {
    icon: "🤖",
    title_es: "Agentes de compra",
    title_en: "Shopping agents",
    desc_es: `Search, compare y canastas con ${MARKET_STATS.mcpTools} herramientas MCP. Build Free/Pro — checkout vía PayPal/Mercado Pago/QR.`,
    desc_en: `Search, compare, and baskets with ${MARKET_STATS.mcpTools} MCP tools. Build Free/Pro — checkout via PayPal/Mercado Pago/QR.`,
    href: "#pricing",
  },
  {
    icon: "📊",
    title_es: "Datos de mercado",
    title_en: "Market data",
    desc_es: `${MARKET_STATS.pricesVerifiedLabel} precios normalizados, ${MARKET_STATS.indicatorsCount} indicadores, fuentes públicas (OFF, Wikimedia, World Bank, IMF, Eurostat, BCB).`,
    desc_en: `${MARKET_STATS.pricesVerifiedLabel} normalized prices, ${MARKET_STATS.indicatorsCount} indicators, public sources (OFF, Wikimedia, World Bank, IMF, Eurostat, BCB).`,
    href: "#coverage",
  },
  {
    icon: "\ud83e\uddfa",
    title_es: "Canasta multi-retailer",
    title_en: "Multi-retailer basket",
    desc_es: "Compara tu carrito completo entre cadenas. Precios por kg/L para decisiones de compra informadas.",
    desc_en: "Compare your full cart across chains. Per kg/L pricing for informed purchase decisions.",
    href: "#api",
  },
  {
    icon: "📈",
    title_es: "Inflación desde góndola",
    title_en: "Shelf-price inflation",
    desc_es: `Cambios reales de precios actualizados cada ${MARKET_STATS.pricesRefreshHours} horas, no estimaciones con 30 días de retraso.`,
    desc_en: `Real price changes refreshed every ${MARKET_STATS.pricesRefreshHours} hours, not 30-day-lagged estimates.`,
    href: "#coverage",
  },
  {
    icon: "🛒",
    title_es: "Compras de empresa",
    title_en: "Enterprise procurement",
    desc_es: "Procure Copilot: comparar, aprobar y pagar sin programar. Infra CLI Market incluida desde $29/mes.",
    desc_en: "Procure Copilot: compare, approve, and pay without code. CLI Market infra included from $29/mo.",
    href: "#procure",
  },
];

export default function UseCasesSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="casos" className="brand-mode-terminal landing-section landing-section-glow animate-fade-in">
      <div className="landing-container text-center">
        <p className="section-eyebrow mb-4">
          {isES ? "Casos de uso" : "Use cases"}
        </p>
        <h2 className="section-title">
          {isES ? "Una API. Múltiples aplicaciones." : "One API. Multiple applications."}
        </h2>
        <p className="section-intro max-w-xl">
          {isES
            ? "Desde agentes de compra hasta equipos de datos: los mismos precios verificados para todos."
            : "From shopping agents to data teams: the same verified prices for everyone."}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 max-w-[800px] mx-auto text-left mb-12">
          {cases.map((c, i) => (
            <motion.a
              key={c.title_es}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              href={c.href}
              target={c.href.startsWith("http") ? "_blank" : undefined}
              rel={c.href.startsWith("http") ? "noopener" : undefined}
              className="card-cyber card-cyber-interactive p-6 flex flex-col gap-4 hover:border-[var(--cm-mint)]/30 transition-colors"
            >
              <span className="text-2xl" aria-hidden="true">{c.icon}</span>
              <h3 className="text-sm font-bold text-white">
                {isES ? c.title_es : c.title_en}
              </h3>
              <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed flex-1">
                {isES ? c.desc_es : c.desc_en}
              </p>
              <span className="text-xs font-mono text-[var(--cm-mint)]">
                {isES ? "Explorar →" : "Explore →"}
              </span>
            </motion.a>
          ))}
        </div>

        <a
          href="#pricing"
          className="btn-mint"
        >
          {isES ? "Ver planes →" : "View plans →"}
        </a>
      </div>
    </section>
  );
}
