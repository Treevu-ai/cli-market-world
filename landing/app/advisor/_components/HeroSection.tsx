"use client";

import { Terminal, ArrowRight, ShieldCheck, BarChart3 } from "lucide-react";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function HeroSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  const stats = [
    {
      value: MARKET_STATS.pricesVerifiedLabel,
      label_es: "Precios verificados",
      label_en: "Verified prices",
      detail_es: `Actualizados cada ${MARKET_STATS.pricesRefreshHours}h`,
      detail_en: `Refreshed every ${MARKET_STATS.pricesRefreshHours}h`,
    },
    {
      value: String(MARKET_STATS.retailersVerified),
      label_es: "Retailers activos",
      label_en: "Active retailers",
      detail_es: `${MARKET_STATS.retailersDefined} catálogo total`,
      detail_en: `${MARKET_STATS.retailersDefined} total catalog`,
    },
    {
      value: String(MARKET_STATS.countries),
      label_es: "Países",
      label_en: "Countries",
      detail_es: "Cobertura LATAM",
      detail_en: "LATAM coverage",
    },
    {
      value: String(MARKET_STATS.mcpTools),
      label_es: "Herramientas MCP",
      label_en: "MCP tools",
      detail_es: "API + CLI + agentes",
      detail_en: "API + CLI + agents",
    },
  ];

  return (
    <section className="relative overflow-hidden pt-14 pb-16 bg-[var(--cm-surface)] border border-[var(--cm-outline-variant)] rounded-3xl mb-12 shadow-xs">
      <div className="absolute inset-0 bg-[linear-gradient(to_right,var(--cm-hairline-soft)_1px,transparent_1px),linear-gradient(to_bottom,var(--cm-hairline-soft)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-30 pointer-events-none" />

      <div className="max-w-5xl mx-auto px-6 sm:px-8 relative z-10">
        <div className="flex flex-wrap items-center gap-2 mb-6">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[var(--cm-action-soft)] border border-[var(--cm-mint)]/20 text-[var(--cm-action-deep)]">
            <Terminal className="w-3.5 h-3.5" /> CLI Market for Advisors
          </span>
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] text-[var(--cm-on-surface-variant)]">
            {isES ? "Para consultores y asesores de negocio" : "For business consultants and advisors"}
          </span>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[var(--cm-action-soft)] border border-[var(--cm-mint)]/20 text-[var(--cm-action-deep)]">
            <ShieldCheck className="w-3.5 h-3.5" /> {isES ? "Evidencia citable" : "Citable evidence"}
          </span>
        </div>

        <div className="max-w-3xl mb-10">
          <h1 className="text-4xl sm:text-5xl font-extrabold text-[var(--cm-on-surface)] leading-none tracking-tight mb-6">
            {isES ? "Respalda tu consultoría de retail con " : "Back your retail consulting with "}
            <span className="text-[var(--cm-mint)] italic">
              {isES ? "hechos de góndola verificables." : "verifiable shelf data."}
            </span>
          </h1>
          <p className="text-base sm:text-lg text-[var(--cm-on-surface-variant)] leading-relaxed mb-8">
            {isES
              ? "Como asesor de negocio o consultor estratégico de marcas de retail, tus recomendaciones valen por su precisión. Conéctate a la góndola digital de LATAM en tiempo real, automatiza el análisis competitivo y entrega a tus clientes datos de anaquel verificables en vez de auditorías manuales."
              : "As a business advisor or brand strategy consultant in retail, your recommendations are worth what they can prove. Connect to LATAM's digital shelf in real time, automate competitive analysis, and hand clients verifiable shelf data instead of manual audits."}
          </p>

          <div className="flex flex-wrap gap-4">
            <a
              href="#advisor-hub"
              className="px-5 py-3 rounded-xl bg-[var(--cm-mint)] hover:bg-[var(--cm-action-deep)] text-[var(--cm-on-mint)] font-semibold text-sm transition-all duration-200 shadow-sm flex items-center gap-2"
            >
              {isES ? "Probar el radar de mercado" : "Try the market radar"} <ArrowRight className="w-4 h-4" />
            </a>
            <a
              href="#ejemplos-casos"
              className="px-5 py-3 rounded-xl bg-[var(--cm-surface-high)] hover:bg-[var(--cm-outline-variant)]/40 text-[var(--cm-on-surface-variant)] font-semibold text-sm transition-all duration-200 border border-[var(--cm-outline-variant)]"
            >
              {isES ? "Ver casos de aplicación" : "See applied use cases"}
            </a>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 border-t border-[var(--cm-hairline-soft)] pt-8 mt-12 text-left">
          {stats.map((s) => (
            <div key={s.label_es} className="p-4 bg-[var(--cm-surface-high)]/60 rounded-xl border border-[var(--cm-hairline-soft)]">
              <div className="flex items-center gap-1.5 text-[var(--cm-on-surface)] mb-1">
                <BarChart3 className="w-4 h-4 text-[var(--cm-mint)]" />
                <span className="text-2xl font-black">{s.value}</span>
              </div>
              <span className="text-xs font-semibold text-[var(--cm-text-secondary)] uppercase tracking-wider block">
                {isES ? s.label_es : s.label_en}
              </span>
              <span className="text-[11px] text-[var(--cm-text-secondary)] mt-0.5 block leading-tight">
                {isES ? s.detail_es : s.detail_en}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
