"use client";

import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function IntelligenceFAQ() {
  const { lang } = useLang();
  const isES = lang === "es";

  const faqs = isES
    ? [
        {
          q: "¿En qué se diferencia de CLI Market Pro?",
          a: "Pro es self-serve para desarrolladores (API, MCP, CLI). Intelligence es un piloto gestionado con spreads, inflación por categoría y exports para equipos de pricing y fintech.",
        },
        {
          q: "¿De dónde vienen los datos?",
          a: `Precios verificados de ${MARKET_STATS.retailersVerified} retailers indexados, normalizados por kg/L con pipelines de validación.`,
        },
        {
          q: "¿Qué incluye un piloto?",
          a: "Según tier (S/M/L): 1 país a multi-país, export semanal o API, y SLA documentado en el one-pager de metodología.",
        },
        {
          q: "¿Con qué frecuencia se actualizan?",
          a: `Cada ${MARKET_STATS.pricesRefreshHours} horas en retailers activos — señales de inflación en ventanas 7 / 30 / 90 días.`,
        },
      ]
    : [
        {
          q: "How is this different from CLI Market Pro?",
          a: "Pro is self-serve for developers (API, MCP, CLI). Intelligence is a managed pilot with spreads, category inflation, and exports for pricing and fintech teams.",
        },
        {
          q: "Where does the data come from?",
          a: `Verified prices from ${MARKET_STATS.retailersVerified} indexed retailers, normalized per kg/L with validation pipelines.`,
        },
        {
          q: "What does a pilot include?",
          a: "By tier (S/M/L): 1 country to multi-country, weekly export or API access, with SLA documented in the methodology one-pager.",
        },
        {
          q: "How often is data refreshed?",
          a: `Every ${MARKET_STATS.pricesRefreshHours} hours across active retailers — inflation signals in 7 / 30 / 90-day windows.`,
        },
      ];

  return (
    <section id="faq" className="landing-section animate-fade-in scroll-mt-24">
      <div className="landing-container-wide">
        <div className="landing-section-header text-center">
          <p className="section-eyebrow mb-4">FAQ</p>
          <h2 className="section-title">
            {isES ? "Preguntas de analistas." : "Analyst questions."}
          </h2>
        </div>

        <div className="landing-content-narrow text-left space-y-0">
          {faqs.map((faq, i) => (
            <details
              key={i}
              className="group border-b border-[var(--cm-outline-variant)]/30 py-1"
              {...(i === 0 ? { open: true } : {})}
            >
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 py-5 text-base font-medium text-[var(--cm-on-surface)] marker:content-none [&::-webkit-details-marker]:hidden">
                <span className="text-left">{faq.q}</span>
                <span
                  className="shrink-0 text-[var(--cm-signal)] text-lg leading-none transition-transform duration-200 group-open:rotate-45"
                  aria-hidden
                >
                  +
                </span>
              </summary>
              <p className="pb-5 text-base text-[var(--cm-on-surface-variant)] leading-relaxed">{faq.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
