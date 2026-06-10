"use client";

import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { PROCURE_APP_URL, PROCURE_PLANS } from "@/lib/procurePlans";
import ProcureSubscribeButton from "@/components/ProcureSubscribeButton";

const BENEFITS_ES = [
  "Comparación automática en retailers verificados — sin WhatsApp ni Excel.",
  "Data-gate: no recomienda compra si los precios están desactualizados.",
  "Compare compara; Ops añade aprobaciones gerente y checkout.",
  "Infraestructura CLI Market incluida — una sola factura.",
];

const BENEFITS_EN = [
  "Automatic comparison across verified retailers — no WhatsApp or Excel.",
  "Data-gate blocks recommendations when prices are stale.",
  "Compare compares; Ops adds manager approvals and checkout.",
  "CLI Market infrastructure included — one invoice.",
];

export default function ProcurePricingPanel() {
  const { lang } = useLang();
  const isES = lang === "es";
  const benefits = isES ? BENEFITS_ES : BENEFITS_EN;

  return (
    <div
      id="procure"
      className="brand-mode-operations scroll-mt-24 text-left"
    >
      <div className="landing-content-narrow mb-10 space-y-4 text-center">
        <p className="text-sm text-[var(--cm-on-surface-variant)]">
          {isES
            ? `${MARKET_STATS.retailersVerified} retailers verificados · misma API que Build · dashboard Procure incluido.`
            : `${MARKET_STATS.retailersVerified} verified retailers · same API as Build · Procure dashboard included.`}
        </p>
        <div className="rounded-xl border border-[var(--cm-outline-variant)]/35 bg-[var(--cm-surface-low)]/40 px-4 py-3 text-left text-xs text-[var(--cm-on-surface-variant)] leading-relaxed">
          <p className="font-semibold text-white mb-1">
            {isES ? "¿Build Pro o Procure Ops?" : "Build Pro or Procure Ops?"}
          </p>
          <p>
            {isES
              ? "Build Pro ($39) es para quien integra la API/MCP en código. Procure Ops ($79) es para equipos de compras (aprobaciones, checkout retail) — incluye la API; no pagues los dos salvo que quieras ambos dashboards."
              : "Build Pro ($39) is for developers integrating the API/MCP. Procure Ops ($79) is for procurement teams (approvals, retail checkout) — API included; only pay both if you need both dashboards."}
          </p>
        </div>
      </div>

      <div className="landing-content-rail grid grid-cols-1 lg:grid-cols-3 gap-5 mb-10">
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

      <div className="landing-content-rail grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
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
            ? "Tras pagar: market register (si es nuevo) → pega tu API key en el dashboard Procure."
            : "After payment: market register (if new) → paste API key in the Procure dashboard."}
        </p>
      </div>
    </div>
  );
}