"use client";

import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { procurePriceRangeLabel } from "@/lib/procurePlans";
import { CTA } from "@/lib/ctaCopy";

const STEPS = [
  { n: "01", es: "Solicitud", en: "Request", descEs: "Tu equipo envía una lista de productos. Sin scraping. Sin llamadas.", descEn: "Your team submits a product list. No scraping. No calls." },
  {
    n: "02",
    es: "Comparación",
    en: "Compare",
    descEs: `CLI Market busca en ${MARKET_STATS.retailersVerified} retailers verificados y normaliza precios por kg/L.`,
    descEn: `CLI Market searches ${MARKET_STATS.retailersVerified} verified retailers and normalizes prices per kg/L.`,
  },
  { n: "03", es: "Aprobación", en: "Approve", descEs: "Workflow de aprobación interno. Roles, límites, trazabilidad.", descEn: "Internal approval workflow. Roles, limits, audit trail." },
  { n: "04", es: "Checkout", en: "Checkout", descEs: "Pago integrado: Yape, Plin, PayPal. Una orden. Un comprobante.", descEn: "Built-in payment: Yape, Plin, PayPal. One order. One receipt." },
  { n: "05", es: "Ahorro", en: "Savings", descEs: "Reportes de ahorro vs. precio promedio de mercado. ROI medible.", descEn: "Savings reports vs. market average price. Measurable ROI." },
];

export default function ProcureCopilotPage() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <main className="min-h-screen bg-[var(--cm-background)] pt-24 pb-20">
      <div className="landing-container-wide max-w-[880px] mx-auto">
        {/* Hero */}
        <section className="text-center mb-20">
          <p className="section-eyebrow mb-4">
            {isES ? "Procure Copilot" : "Procure Copilot"}
          </p>
          <h1 className="font-display text-[clamp(2rem,5vw,3.5rem)] font-bold text-[var(--cm-on-surface)] mb-4 tracking-tight">
            {isES ? "Compra mejor. Más rápido. Con menos desperdicio." : "Buy better. Faster. With less waste."}
          </h1>
          <p className="text-lg text-[var(--cm-on-surface-variant)] max-w-[640px] mx-auto leading-relaxed">
            {isES
              ? `Procure Copilot convierte listas de compras en órdenes optimizadas usando precios reales de ${MARKET_STATS.retailersVerified} retailers en ${MARKET_STATS.countries} países. Con aprobaciones, trazabilidad y reportes de ahorro.`
              : `Procure Copilot turns shopping lists into optimized orders using real shelf prices from ${MARKET_STATS.retailersVerified} retailers across ${MARKET_STATS.countries} countries. With approvals, audit trail, and savings reports.`}
          </p>
          <a
            href={CTA.viewProcurePlans.href}
            className="inline-flex items-center rounded-3xl bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-sm font-semibold px-6 py-3 mt-8 hover:brightness-110 transition-all"
          >
            {isES ? CTA.viewProcurePlans.es : CTA.viewProcurePlans.en}
          </a>
        </section>

        {/* Workflow */}
        <section className="mb-20">
          <h2 className="section-title text-center mb-12">
            {isES ? "Cómo funciona" : "How it works"}
          </h2>
          <div className="grid gap-1">
            {STEPS.map((step) => (
              <div
                key={step.n}
                className="flex items-start gap-6 p-6 rounded-lg border border-[var(--cm-outline-variant)]/20 hover:border-[var(--cm-mint)]/30 transition-colors"
              >
                <span className="font-mono text-2xl font-bold text-[var(--cm-mint)]/40 shrink-0 w-12">
                  {step.n}
                </span>
                <div>
                  <h3 className="font-semibold text-[var(--cm-on-surface)] text-lg mb-1">
                    {isES ? step.es : step.en}
                  </h3>
                  <p className="text-[var(--cm-on-surface-variant)] leading-relaxed">
                    {isES ? step.descEs : step.descEn}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Value props */}
        <section className="mb-20 grid sm:grid-cols-3 gap-6">
          {[
            { es: "Datos reales", en: "Real data", descEs: "Precios de góndola, no estimaciones.", descEn: "Shelf prices, not estimates." },
            { es: "Trazabilidad", en: "Audit trail", descEs: "Cada aprobación queda registrada.", descEn: "Every approval is logged." },
            { es: "ROI medible", en: "Measurable ROI", descEs: "Ahorro vs. precio promedio del mercado.", descEn: "Savings vs. market average price." },
          ].map((v, i) => (
            <div key={i} className="p-6 rounded-lg border border-[var(--cm-outline-variant)]/20 text-center">
              <h3 className="font-semibold text-[var(--cm-on-surface)] mb-2">{isES ? v.es : v.en}</h3>
              <p className="text-sm text-[var(--cm-on-surface-variant)]">{isES ? v.descEs : v.descEn}</p>
            </div>
          ))}
        </section>

        {/* CTA */}
        <section className="text-center py-16 rounded-2xl bg-gradient-to-b from-[var(--cm-surface-low)] to-[var(--cm-background)] border border-[var(--cm-outline-variant)]/20">
          <h2 className="font-display text-2xl font-bold text-[var(--cm-on-surface)] mb-4">
            {isES ? "¿Listo para optimizar tus compras?" : "Ready to optimize procurement?"}
          </h2>
          <p className="text-[var(--cm-on-surface-variant)] mb-8">
            {isES
              ? `${procurePriceRangeLabel(true)} · infra Build incluida.`
              : `${procurePriceRangeLabel(false)} · Build infra included.`}
          </p>
          <a
            href={CTA.viewProcurePlans.href}
            className="inline-flex items-center rounded-3xl bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-sm font-semibold px-6 py-3 hover:brightness-110 transition-all"
          >
            {isES ? CTA.viewProcurePlans.es : CTA.viewProcurePlans.en}
          </a>
        </section>
      </div>
    </main>
  );
}
