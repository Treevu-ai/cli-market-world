"use client";

import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

const STATS = [
  { value: MARKET_STATS.retailersVerified, label_es: "retailers verificados", label_en: "verified retailers" },
  { value: MARKET_STATS.countries, label_es: "países LATAM", label_en: "LATAM countries" },
  { value: MARKET_STATS.pricesVerifiedLabel, label_es: "price points verificados", label_en: "verified price points" },
  { value: `${MARKET_STATS.pricesRefreshHours}h`, label_es: "ciclo de refresh", label_en: "refresh cycle" },
];

export default function CinematicVision() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="infrastructure" className="landing-section animate-fade-in bg-[#f6f9fc]" style={{ borderTop: "1px solid #e3e8ee", borderBottom: "1px solid #e3e8ee" }}>
      <div className="landing-container-wide text-center">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-4">{isES ? "Infraestructura" : "Infrastructure"}</p>
          <h2 className="section-title">
            {isES
              ? "Precios verificados. Sin scraping. Para agentes."
              : "Verified prices. Zero scraping. For agents."}
          </h2>
          <p className="section-intro">
            {isES
              ? `CLI Market normaliza precios por kg/L en ${MARKET_STATS.retailersVerified} retailers. Cada precio pasa por validación de calidad — sin valores atípicos, sin datos desactualizados. Tu agente recibe datos limpios, listos para comparar canastas o disparar flujos de compra.`
              : `CLI Market normalizes prices per kg/L across ${MARKET_STATS.retailersVerified} retailers. Every price point passes quality validation — no outliers, no stale data. Your agent gets clean data, ready to compare baskets or trigger procurement workflows.`}
          </p>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-2 sm:grid-cols-4 gap-4 landing-content-rail"
        >
          {STATS.map((s) => (
            <div key={s.label_en} className="card-cyber px-4 py-5 flex flex-col items-center gap-1">
              <span className="text-2xl font-bold text-[#0d253d] tabular-nums">{s.value}</span>
              <span className="text-xs text-[#64748d] text-center leading-snug">
                {isES ? s.label_es : s.label_en}
              </span>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
