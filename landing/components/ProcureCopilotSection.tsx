"use client";

import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { PROCURE_PLANS } from "@/lib/procurePlans";
import { CTA } from "@/lib/ctaCopy";

const STEPS = [
  { n: "01", es: "Solicitud", en: "Request", descEs: "Tu equipo envía una lista de productos. Sin scraping. Sin llamadas.", descEn: "Your team submits a product list. No scraping. No calls." },
  { n: "02", es: "Comparación", en: "Compare", descEs: `CLI Market busca en ${MARKET_STATS.retailersVerified} retailers verificados y normaliza precios por kg/L.`, descEn: `CLI Market searches ${MARKET_STATS.retailersVerified} verified retailers and normalizes prices per kg/L.` },
  { n: "03", es: "Aprobación", en: "Approve", descEs: "Workflow de aprobación interno. Roles, límites, trazabilidad.", descEn: "Internal approval workflow. Roles, limits, audit trail." },
  { n: "04", es: "Checkout", en: "Checkout", descEs: "Pago integrado: Yape, Plin, PayPal. Una orden. Un comprobante.", descEn: "Built-in payment: Yape, Plin, PayPal. One order. One receipt." },
  { n: "05", es: "Ahorro", en: "Savings", descEs: "Reportes de ahorro vs. precio promedio de mercado. ROI medible.", descEn: "Savings reports vs. market average price. Measurable ROI." },
];

const COMPARE_PLAN = PROCURE_PLANS[0];
const OPS_PLAN = PROCURE_PLANS[1];

const PLAN_ROWS = [
  {
    featureEs: "Precio",
    featureEn: "Price",
    compare: (isES: boolean) => isES ? `$${COMPARE_PLAN.price}/mes` : `$${COMPARE_PLAN.price}/mo`,
    ops: (isES: boolean) => isES ? `$${OPS_PLAN.price}/mes` : `$${OPS_PLAN.price}/mo`,
  },
  {
    featureEs: "Comparación multi-retailer",
    featureEn: "Multi-retailer compare",
    compare: () => "✓",
    ops: () => "✓",
  },
  {
    featureEs: "Checkout integrado",
    featureEn: "Integrated checkout",
    compare: () => "—",
    ops: () => "✓",
  },
  {
    featureEs: "Aprobaciones gerente",
    featureEn: "Manager approvals",
    compare: () => "—",
    ops: () => "✓",
  },
  {
    featureEs: "Audit trail",
    featureEn: "Audit trail",
    compare: () => "—",
    ops: () => "✓",
  },
  {
    featureEs: "Procurements / mes",
    featureEn: "Procurements / mo",
    compare: () => "20",
    ops: () => "200",
  },
] as const;

export default function ProcureCopilotSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="procure" className="landing-section animate-fade-in scroll-mt-24" style={{ backgroundColor: "#f8fafc" }}>
      <div className="landing-container-wide">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-4">PROCURE COPILOT</p>
          <h2 className="section-title text-[var(--cm-on-surface)]">
            {isES ? "Compra mejor. Más rápido. Con menos desperdicio." : "Buy better. Faster. With less waste."}
          </h2>
          <p className="section-intro">
            {isES
              ? `Convierte listas de compras en órdenes optimizadas usando precios reales de ${MARKET_STATS.retailersVerified} retailers en ${MARKET_STATS.countries} países — con aprobaciones, trazabilidad y reportes de ahorro.`
              : `Turn shopping lists into optimized orders using real shelf prices from ${MARKET_STATS.retailersVerified} retailers across ${MARKET_STATS.countries} countries — with approvals, audit trail, and savings reports.`}
          </p>
        </div>

        {/* Savings example */}
        <div className="max-w-[640px] mx-auto mb-12 rounded-xl border border-[var(--cm-mint)]/20 bg-[var(--cm-mint)]/5 px-6 py-5 flex flex-col sm:flex-row sm:items-center gap-4">
          <div className="text-3xl shrink-0">📊</div>
          <div>
            <p className="text-sm font-semibold text-[var(--cm-on-surface)] mb-1">
              {isES ? "Ejemplo real de ahorro" : "Real savings example"}
            </p>
            <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
              {isES
                ? "Un restaurante en Lima con canasta semanal de S/ 2,400 encontró la combinación óptima entre Metro y Tottus — ahorro de S/ 312/semana (13%) vs. compra en un solo retailer."
                : "A Lima restaurant with a weekly basket of S/ 2,400 found the optimal split between Metro and Tottus — saving S/ 312/week (13%) vs. single-retailer purchasing."}
            </p>
          </div>
        </div>

        {/* Workflow steps */}
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

        {/* Plan comparison table */}
        <div className="max-w-[640px] mx-auto mb-12">
          <h3 className="text-center text-sm font-semibold text-[var(--cm-on-surface-variant)] uppercase tracking-widest mb-6">
            {isES ? "¿Qué plan necesito?" : "Which plan do I need?"}
          </h3>
          <div className="rounded-xl border border-[var(--cm-outline-variant)]/30 overflow-hidden">
            {/* Header */}
            <div className="grid grid-cols-3 bg-[var(--cm-surface-low)]">
              <div className="p-4" />
              <div className="p-4 text-center border-l border-[var(--cm-outline-variant)]/20">
                <p className="text-xs font-mono text-[var(--cm-on-surface-variant)] uppercase tracking-wider mb-1">Compare</p>
                <p className="text-lg font-bold text-[var(--cm-on-surface)]">${COMPARE_PLAN.price}<span className="text-xs font-normal text-[var(--cm-on-surface-variant)]">{isES ? "/mes" : "/mo"}</span></p>
                <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1">{isES ? COMPARE_PLAN.description_es : COMPARE_PLAN.description_en}</p>
              </div>
              <div className="p-4 text-center border-l border-[var(--cm-outline-variant)]/20 bg-[var(--cm-mint)]/5">
                <p className="text-xs font-mono text-[var(--cm-mint)] uppercase tracking-wider mb-1">Ops ★</p>
                <p className="text-lg font-bold text-[var(--cm-on-surface)]">${OPS_PLAN.price}<span className="text-xs font-normal text-[var(--cm-on-surface-variant)]">{isES ? "/mes" : "/mo"}</span></p>
                <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1">{isES ? OPS_PLAN.description_es : OPS_PLAN.description_en}</p>
              </div>
            </div>
            {/* Rows */}
            {PLAN_ROWS.map((row, i) => (
              <div
                key={i}
                className="grid grid-cols-3 border-t border-[var(--cm-outline-variant)]/20"
              >
                <div className="p-3 px-4 text-sm text-[var(--cm-on-surface-variant)]">
                  {isES ? row.featureEs : row.featureEn}
                </div>
                <div className="p-3 text-center border-l border-[var(--cm-outline-variant)]/20 text-sm text-[var(--cm-on-surface-variant)]">
                  {row.compare(isES)}
                </div>
                <div className="p-3 text-center border-l border-[var(--cm-outline-variant)]/20 text-sm font-medium text-[var(--cm-mint)] bg-[var(--cm-mint)]/5">
                  {row.ops(isES)}
                </div>
              </div>
            ))}
          </div>
          <p className="text-xs text-[var(--cm-on-surface-variant)] text-center mt-3">
            {isES
              ? "★ Ops recomendado para equipos con proceso de aprobación. Infra Build incluida en ambos."
              : "★ Ops recommended for teams with an approval process. Build infra included in both."}
          </p>
        </div>

        {/* CTA */}
        <div className="text-center">
          <a
            href={CTA.viewProcurePlans.href}
            className="inline-flex items-center rounded-[10px] bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-sm font-semibold px-6 py-3 hover:brightness-110 transition-all"
          >
            {isES ? CTA.viewProcurePlans.es : CTA.viewProcurePlans.en}
          </a>
        </div>
      </div>
    </section>
  );
}
