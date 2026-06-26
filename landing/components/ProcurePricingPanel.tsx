"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { PROCURE_APP_URL, PROCURE_PLANS, type ProcurePlanSlug } from "@/lib/procurePlans";
import ProcureSubscribeButton from "@/components/ProcureSubscribeButton";
import {
  clearProcureCheckoutQuery,
  readProcureCheckoutDeepLink,
} from "@/lib/procureCheckoutUrl";

const BENEFITS_ES = [
  "Comparación automática — sin WhatsApp ni Excel.",
  "Data-gate: no recomienda si los precios están desactualizados.",
  "Compare compara; Ops añade aprobaciones y checkout.",
];

const BENEFITS_EN = [
  "Automatic comparison — no WhatsApp or Excel.",
  "Data-gate blocks recommendations when prices are stale.",
  "Compare compares; Ops adds approvals and checkout.",
];

export default function ProcurePricingPanel() {
  const { lang } = useLang();
  const isES = lang === "es";
  const benefits = isES ? BENEFITS_ES : BENEFITS_EN;
  const [autoOpenPlan, setAutoOpenPlan] = useState<ProcurePlanSlug | null>(null);

  useEffect(() => {
    const link = readProcureCheckoutDeepLink();
    if (link?.open) {
      setAutoOpenPlan(link.plan);
      clearProcureCheckoutQuery();
    }
  }, []);

  return (
    <div className="scroll-mt-24 text-left">
      <div className="landing-content-narrow mb-10 space-y-4 text-center">
        <div className="rounded-xl border border-[var(--cm-outline-variant)]/35 bg-[var(--cm-surface-low)]/40 px-4 py-3 text-left text-xs text-[var(--cm-on-surface-variant)] leading-relaxed">
          <p className="font-semibold text-[var(--cm-on-surface)] mb-1">
            {isES ? "¿Build Pro o Procure Ops?" : "Build Pro or Procure Ops?"}
          </p>
          <p>
            {isES
              ? "Build Pro ($49) es para quien integra la API en código. Procure Ops ($79) es para equipos de compras (aprobaciones, checkout retail) — incluye la API; no pagues los dos salvo que quieras ambos dashboards."
              : "Build Pro ($49) is for developers integrating the API. Procure Ops ($79) is for procurement teams (approvals, retail checkout) — API included; only pay both if you need both dashboards."}
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
            <h3 className="text-lg font-bold text-[var(--cm-on-surface)]">{plan.name}</h3>
            <p className="text-sm text-[var(--cm-on-surface-variant)] mt-2 min-h-[2.5rem]">
              {isES ? plan.description_es : plan.description_en}
            </p>
            <div className="mt-4 mb-4">
              <span className="text-3xl font-black text-[var(--cm-on-surface)]">${plan.price}</span>
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
            <ProcureSubscribeButton plan={plan.slug} autoOpen={autoOpenPlan === plan.slug} />
          </motion.div>
        ))}
      </div>

      <div className="landing-content-rail grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
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
            ? "Tras pagar: crea cuenta en cli-market.dev/account → copia tu API key → pégala en el dashboard Procure."
            : "After payment: create account at cli-market.dev/account → copy your API key → paste it in the Procure dashboard."}
        </p>
      </div>
    </div>
  );
}
