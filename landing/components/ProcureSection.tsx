"use client";

import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { PROCURE_APP_URL, PROCURE_PLANS } from "@/lib/procurePlans";
import ProcureSubscribeButton from "@/components/ProcureSubscribeButton";

const BENEFITS_ES = [
  "Comparación automática en retailers verificados — sin WhatsApp ni Excel.",
  "Data-gate: no recomienda compra si el moat está stale.",
  "Starter compara; Pro añade aprobaciones gerente y checkout.",
  "Infraestructura CLI Market incluida — una sola factura.",
];

const BENEFITS_EN = [
  "Automatic comparison across verified retailers — no WhatsApp or Excel.",
  "Data-gate blocks recommendations when the moat is stale.",
  "Starter compares; Pro adds manager approvals and checkout.",
  "CLI Market infrastructure included — one invoice.",
];

export default function ProcureSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const benefits = isES ? BENEFITS_ES : BENEFITS_EN;

  return (
    <section
      id="procure"
      className="brand-mode-operations landing-section animate-fade-in scroll-mt-20"
    >
      <div className="landing-container-wide">
        <div className="text-center mb-14">
          <p className="section-eyebrow text-[var(--cm-mint)] mb-4">Procure</p>
          <h2 className="section-title">
            {isES ? "Compras de empresa. Sin programar." : "Enterprise buying. No code."}
          </h2>
          <p className="section-intro max-w-2xl mx-auto">
            {isES
              ? `Para restaurantes, hoteles y equipos de compras. Mismos datos que Build (${MARKET_STATS.retailersVerified} retailers), con gobernanza y trazabilidad.`
              : `For restaurants, hotels, and procurement teams. Same data as Build (${MARKET_STATS.retailersVerified} retailers), with governance and audit trail.`}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 max-w-6xl mx-auto mb-10">
          {PROCURE_PLANS.map((plan, i) => (
            <motion.div
              key={plan.slug}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              className={`h-full rounded-2xl p-6 flex flex-col card-cyber ${
                plan.highlighted ? "energy-border-active" : ""
              }`}
            >
              {plan.highlighted && (
                <span className="self-center mb-3 bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-xs font-semibold px-4 py-1 rounded-full">
                  {isES ? "Más popular" : "Most popular"}
                </span>
              )}
              <h3 className="text-lg font-bold text-white">{plan.name}</h3>
              <p className="text-sm text-[var(--cm-on-surface-variant)] mt-2 min-h-[2.5rem]">
                {isES ? plan.description_es : plan.description_en}
              </p>
              <div className="mt-4 mb-4">
                <span className="text-3xl font-black text-white">${plan.price}</span>
                <span className="text-sm text-[var(--cm-on-surface-variant)] ml-1">
                  {isES ? "/ mes" : "/ mo"}
                </span>
              </div>
              <ul className="space-y-2 mb-6 flex-1 text-sm text-[var(--cm-on-surface-variant)]">
                {(isES ? plan.features_es : plan.features_en).map((f) => (
                  <li key={f} className="flex gap-2">
                    <span className="text-[var(--cm-mint)] shrink-0">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
              <ProcureSubscribeButton plan={plan.slug} />
            </motion.div>
          ))}
        </div>

        <div className="max-w-3xl mx-auto grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          {benefits.map((b) => (
            <p key={b} className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
              {b}
            </p>
          ))}
        </div>

        <div className="text-center space-y-3">
          <a href={PROCURE_APP_URL} className="btn-mint inline-block">
            {isES ? "Abrir app Procure →" : "Open Procure app →"}
          </a>
          <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]/60 max-w-lg mx-auto">
            {isES
              ? "Tras pagar: market register (si es nuevo) → pega tu API key en el dashboard Procure. Developers: usa Build Pro en #pricing."
              : "After payment: market register (if new) → paste API key in Procure dashboard. Developers: use Build Pro at #pricing."}
          </p>
        </div>
      </div>
    </section>
  );
}