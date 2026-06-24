"use client";

import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { PRICING_PROCURE_HASH } from "@/lib/siteNav";
import { procurePriceRangeLabel } from "@/lib/procurePlans";

const STEPS = [
  { n: "01", es: "Solicitud", en: "Request", descEs: "Tu equipo envía una lista de productos. Sin scraping. Sin llamadas.", descEn: "Your team submits a product list. No scraping. No calls." },
  { n: "02", es: "Comparación", en: "Compare", descEs: `CLI Market busca en ${MARKET_STATS.retailersVerified} retailers verificados y normaliza precios por kg/L.`, descEn: `CLI Market searches ${MARKET_STATS.retailersVerified} verified retailers and normalizes prices per kg/L.` },
  { n: "03", es: "Aprobación", en: "Approve", descEs: "Workflow de aprobación interno. Roles, límites, trazabilidad.", descEn: "Internal approval workflow. Roles, limits, audit trail." },
  { n: "04", es: "Checkout", en: "Checkout", descEs: "Pago integrado: Yape, Plin, PayPal. Una orden. Un comprobante.", descEn: "Built-in payment: Yape, Plin, PayPal. One order. One receipt." },
  { n: "05", es: "Ahorro", en: "Savings", descEs: "Reportes de ahorro vs. precio promedio de mercado. ROI medible.", descEn: "Savings reports vs. market average price. Measurable ROI." },
];

const VALUE_PROPS = [
  { es: "Datos reales", en: "Real data", descEs: "Precios de góndola, no estimaciones.", descEn: "Shelf prices, not estimates." },
  { es: "Trazabilidad", en: "Audit trail", descEs: "Cada aprobación queda registrada.", descEn: "Every approval is logged." },
  { es: "ROI medible", en: "Measurable ROI", descEs: "Ahorro vs. precio promedio del mercado.", descEn: "Savings vs. market average price." },
];

export default function ProcureCopilotSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="procure" className="landing-section animate-fade-in scroll-mt-24" style={{ backgroundColor: "#09090B" }}>
      <div className="landing-container-wide">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-4">{isES ? "PROCURE COPILOT" : "PROCURE COPILOT"}</p>
          <h2 className="section-title text-[var(--cm-on-surface)]">
            {isES ? "Compra mejor. Más rápido. Con menos desperdicio." : "Buy better. Faster. With less waste."}
          </h2>
          <p className="section-intro">
            {isES
              ? `Convierte listas de compras en órdenes optimizadas usando precios reales de ${MARKET_STATS.retailersVerified} retailers en ${MARKET_STATS.countries} países — con aprobaciones, trazabilidad y reportes de ahorro.`
              : `Turn shopping lists into optimized orders using real shelf prices from ${MARKET_STATS.retailersVerified} retailers across ${MARKET_STATS.countries} countries — with approvals, audit trail, and savings reports.`}
          </p>
        </div>

        <div className="max-w-[640px] mx-auto grid gap-1 mb-12">
          {STEPS.map((step) => (
            <div
              key={step.n}
              className="flex items-start gap-6 p-6 rounded-lg border border-[var(--cm-outline-variant)]/20 hover:border-[var(--cm-mint)]/30 transition-colors"
            >
              <span className="font-mono text-2xl font-bold text-[var(--cm-mint)]/40 shrink-0 w-12">
                {step.n}
              </span>
              <div>
                <h3 className="font-semibold text-[var(--cm-on-surface)] text-base mb-1">
                  {isES ? step.es : step.en}
                </h3>
                <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
                  {isES ? step.descEs : step.descEn}
                </p>
              </div>
            </div>
          ))}
        </div>

        <div className="max-w-[640px] mx-auto grid sm:grid-cols-3 gap-4 mb-12">
          {VALUE_PROPS.map((v, i) => (
            <div key={i} className="p-5 rounded-lg border border-[var(--cm-outline-variant)]/20 text-center">
              <h3 className="font-semibold text-[var(--cm-on-surface)] text-sm mb-1">{isES ? v.es : v.en}</h3>
              <p className="text-xs text-[var(--cm-on-surface-variant)]">{isES ? v.descEs : v.descEn}</p>
            </div>
          ))}
        </div>

        <div className="text-center">
          <p className="text-sm text-[var(--cm-on-surface-variant)] mb-4">
            {isES
              ? `${procurePriceRangeLabel(true)} · infra Build incluida.`
              : `${procurePriceRangeLabel(false)} · Build infra included.`}
          </p>
          <a
            href={PRICING_PROCURE_HASH}
            className="inline-flex items-center rounded-[10px] bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-sm font-semibold px-6 py-3 hover:brightness-110 transition-all"
          >
            {isES ? "Ver planes Procure →" : "See Procure plans →"}
          </a>
        </div>
      </div>
    </section>
  );
}
