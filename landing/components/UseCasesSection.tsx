"use client";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

const cases = [
  {
    icon: "🤖",
    title_es: "Agentes de compra",
    title_en: "Shopping agents",
    before_es: "Scraping por retailer · parsers frágiles",
    before_en: "Per-retailer scraping · fragile parsers",
    after_es: `Una API + ${MARKET_STATS.mcpTools} MCP tools · canasta multi-cadena`,
    after_en: `One API + ${MARKET_STATS.mcpTools} MCP tools · multi-chain basket`,
    href: "#pricing",
  },
  {
    icon: "📊",
    title_es: "Datos de mercado",
    title_en: "Market data",
    before_es: "IPC y encuestas con semanas de retraso",
    before_en: "CPI and surveys weeks behind",
    after_es: `${MARKET_STATS.pricesVerifiedLabel} precios/kg/L · refresh cada ${MARKET_STATS.pricesRefreshHours}h`,
    after_en: `${MARKET_STATS.pricesVerifiedLabel} per kg/L prices · refresh every ${MARKET_STATS.pricesRefreshHours}h`,
    href: "#coverage",
  },
  {
    icon: "\ud83e\uddfa",
    title_es: "Canasta multi-retailer",
    title_en: "Multi-retailer basket",
    before_es: "Comparar manualmente en 3+ apps",
    before_en: "Manual comparison across 3+ apps",
    after_es: "Un comando · mejor total por cadena",
    after_en: "One command · best total per chain",
    href: "#api",
  },
  {
    icon: "📈",
    title_es: "Inflación desde góndola",
    title_en: "Shelf-price inflation",
    before_es: "Estimaciones macro, no góndola",
    before_en: "Macro estimates, not shelf",
    after_es: `Tendencias reales · ${MARKET_STATS.indicatorsCount} indicadores intel`,
    after_en: `Real trends · ${MARKET_STATS.indicatorsCount} intel indicators`,
    href: "#intelligence",
  },
  {
    icon: "🛒",
    title_es: "Compras de empresa",
    title_en: "Enterprise procurement",
    before_es: "WhatsApp + Excel para aprobar compras",
    before_en: "WhatsApp + Excel to approve buys",
    after_es: "Procure Copilot · comparar y aprobar sin código",
    after_en: "Procure Copilot · compare and approve without code",
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
          {isES ? "¿Para quién es CLI Market?" : "Who is CLI Market for?"}
        </h2>
        <p className="section-intro max-w-xl">
          {isES
            ? "Builders, equipos comerciales y operadores de compras — mismos precios verificados, distintas superficies."
            : "Builders, commercial teams, and procurement operators — same verified prices, different surfaces."}
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
              className="card-cyber card-cyber-interactive p-6 flex flex-col gap-3 hover:border-[var(--cm-mint)]/30 transition-colors"
            >
              <span className="text-2xl" aria-hidden="true">{c.icon}</span>
              <h3 className="text-sm font-bold text-white">
                {isES ? c.title_es : c.title_en}
              </h3>
              <div className="space-y-2 text-sm leading-relaxed flex-1">
                <p className="text-[var(--cm-on-surface-variant)]/60">
                  <span className="font-mono text-[10px] uppercase tracking-wider mr-2">
                    {isES ? "Antes" : "Before"}
                  </span>
                  {isES ? c.before_es : c.before_en}
                </p>
                <p className="text-[var(--cm-on-surface-variant)]">
                  <span className="font-mono text-[10px] uppercase tracking-wider text-[var(--cm-mint)] mr-2">
                    {isES ? "Con CLI Market" : "With CLI Market"}
                  </span>
                  {isES ? c.after_es : c.after_en}
                </p>
              </div>
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
