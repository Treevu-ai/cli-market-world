"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function FAQ() {
  const { lang } = useLang();
  const isES = lang === "es";

  const faqs = isES
    ? [
        {
          q: "¿Los precios son reales?",
          a: "Sí. Provienen de retailers verificados y pasan por pipelines de validación.",
        },
        {
          q: "¿Con qué frecuencia se actualizan?",
          a: `Cada ${MARKET_STATS.pricesRefreshHours} horas en retailers activos.`,
        },
        {
          q: "¿Cómo empiezo?",
          a: "pip install cli-market-world, API key en el dashboard y MCP en tu IDE. Sin contrato ni demo obligatoria.",
        },
      ]
    : [
        {
          q: "Are the prices real?",
          a: "Yes. They come from verified retailers and pass validation pipelines.",
        },
        {
          q: "How often is data refreshed?",
          a: `Every ${MARKET_STATS.pricesRefreshHours} hours across active retailers.`,
        },
        {
          q: "How do I get started?",
          a: "pip install cli-market-world, API key in the dashboard, and MCP in your IDE. No contract or mandatory demo.",
        },
      ];

  return (
    <section id="faq" className="landing-section animate-fade-in" style={{ backgroundColor: "#ffffff" }}>
      <div className="landing-container-wide">
        <div className="landing-section-header text-center">
          <p className="section-eyebrow mb-4">FAQ</p>
          <h2 className="section-title">
            {isES ? "Preguntas frecuentes." : "Frequently asked questions."}
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
                  className="shrink-0 text-[var(--cm-mint)] text-lg leading-none transition-transform duration-200 group-open:rotate-45"
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
