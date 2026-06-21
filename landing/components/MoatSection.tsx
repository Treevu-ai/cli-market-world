"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function MoatSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  const stats = [
    {
      label_en: "Retail graph",
      label_es: "Grafo retail",
      value: `${MARKET_STATS.retailersDefined} retailers · ${MARKET_STATS.retailersVerified} verified`,
      value_es: `${MARKET_STATS.retailersDefined} retailers · ${MARKET_STATS.retailersVerified} verificados`,
    },
    {
      label_en: "Normalization engine",
      label_es: "Motor de normalización",
      value: isES
        ? "Precios normalizados por kg/L en catálogos fragmentados."
        : "Prices normalized per kg/L across fragmented catalogs.",
      value_es: "Precios normalizados por kg/L en catálogos fragmentados.",
    },
    {
      label_en: "Agent toolkit",
      label_es: "Toolkit para agentes",
      value: `${MARKET_STATS.mcpTools} MCP tools · API · CLI · SDK`,
      value_es: `${MARKET_STATS.mcpTools} herramientas MCP · API · CLI · SDK`,
    },
    {
      label_en: "Historical intelligence",
      label_es: "Inteligencia histórica",
      value: `${MARKET_STATS.indicatorsCount} market indicators`,
      value_es: `${MARKET_STATS.indicatorsCount} indicadores de mercado`,
    },
  ];

  return (
    <section id="moat" className="landing-section animate-fade-in scroll-mt-24">
      <div className="landing-container-wide text-center">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-4">{isES ? "DEFENSIBILIDAD" : "DEFENSIBILITY"}</p>
          <h2 className="section-title text-[var(--cm-on-surface)]">
            {isES ? "Construido para ser difícil de replicar" : "Built to be difficult to replicate"}
          </h2>
          <p className="section-intro">
            {isES
              ? "La defensibilidad de CLI Market proviene de la normalización de datos, cobertura, validación y ejecución."
              : "CLI Market's defensibility comes from data normalization, coverage, validation, and execution."}
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mt-8">
          {stats.map((s, i) => (
            <div key={i} className="card-cyber rounded-2xl p-6 text-left">
              <p className="text-xs font-semibold uppercase tracking-widest text-[var(--cm-on-surface-variant)] mb-3">
                {isES ? s.label_es : s.label_en}
              </p>
              <p className="text-sm font-mono text-[var(--cm-on-surface)] leading-relaxed">
                {isES && s.value_es ? s.value_es : s.value}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
