"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import CommercePulseEmbed from "@/components/CommercePulseEmbed";

const AUDIENCE_LENSES = (isES: boolean) => [
  {
    id: "comercial",
    label: isES ? "Comercial / Ventas" : "Sales / Commercial",
    copy: isES
      ? "Sepa si su precio está sobre o bajo el mercado antes de negociar — benchmarking competitivo por categoría."
      : "Know if your price is above or below market before you negotiate — competitive benchmarking by category.",
  },
  {
    id: "pricing-revenue",
    label: isES ? "Pricing / Revenue" : "Pricing / Revenue",
    copy: isES
      ? "Spreads e inflación por categoría, listos para su modelo de forecast — señal de mercado antes que el IPC oficial."
      : "Category spreads and inflation, ready for your forecast model — market signal ahead of official CPI.",
  },
  {
    id: "growth",
    label: isES ? "Growth / Prensa" : "Growth / Press",
    copy: isES
      ? "Datos verificados y citables para su próxima campaña o nota de prensa, con atribución — sin costo de research propio."
      : "Verified, citable data for your next campaign or press piece, with attribution — no research cost of your own.",
  },
];

const PILOT_TIERS = (isES: boolean) => [
  {
    name: "Pilot S",
    price: "$300",
    scope: isES ? "1 país · export semanal" : "1 country · weekly export",
  },
  {
    name: "Pilot M",
    price: "$400",
    scope: isES ? "1–2 países · API + export" : "1–2 countries · API + export",
  },
  {
    name: "Pilot L",
    price: "$500",
    scope: isES ? "Multi-país · SLA 48h" : "Multi-country · 48h SLA",
  },
];

export default function IntelligenceSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const signalsRef = useRef(null);
  const inView = useInView(signalsRef, { once: true, margin: "-80px" });

  const bullets = isES
    ? [
        "Spreads entre retailers",
        "Inflación por categoría (7 / 30 / 90 días)",
        "Canasta básica con reglas de comparabilidad",
        "Agentic Commerce Pulse semanal publicable",
      ]
    : [
        "Cross-retailer spreads",
        "Category inflation (7 / 30 / 90 days)",
        "Basic basket with comparability rules",
        "Publishable weekly Agentic Commerce Pulse",
      ];

  return (
    <>
      <section
        id="commerce-pulse"
        className="landing-section landing-section-alt scroll-mt-24 !pt-12"
      >
        <div className="landing-container-wide">
          <CommercePulseEmbed country="PE" lang={isES ? "es" : "en"} />
        </div>
      </section>

      <section ref={signalsRef} id="intelligence-signals" className="landing-section scroll-mt-24">
        <div className="landing-container-wide">
          <div className="landing-section-header text-center mb-10">
            <p className="section-eyebrow mb-4">{isES ? "SEÑALES Y PILOTOS" : "SIGNALS & PILOTS"}</p>
            <h2 className="section-title">
              {isES ? (
                <>
                  Datos de góndola para <span className="text-gradient-orange">decisiones de pricing</span>
                </>
              ) : (
                <>
                  Shelf data for <span className="text-gradient-orange">pricing decisions</span>
                </>
              )}
            </h2>
            <p className="mt-4 text-sm text-[var(--cm-on-surface-variant)] max-w-2xl mx-auto">
              {isES
                ? "Lo que ves arriba en el pulso semanal es la punta del iceberg: así se ve el acceso completo — spreads en vivo, alertas de inflación por categoría, y un pilot con SLA para tu equipo."
                : "What you see above in the weekly pulse is the tip of the iceberg: here's what full access looks like — live spreads, category inflation alerts, and an SLA-backed pilot for your team."}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
            {AUDIENCE_LENSES(isES).map((lens) => (
              <div
                key={lens.id}
                className="card-cyber rounded-xl p-5 text-left border border-[var(--cm-outline-variant)]/25"
              >
                <p className="text-xs font-bold uppercase tracking-widest text-[var(--cm-mint)]">
                  {lens.label}
                </p>
                <p className="mt-2 text-xs text-[var(--cm-on-surface-variant)] leading-relaxed">
                  {lens.copy}
                </p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
            <motion.ul
              className="space-y-3"
              initial={{ opacity: 0, x: -16 }}
              animate={inView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              {bullets.map((b) => (
                <li key={b} className="flex items-start gap-2.5 text-sm text-[var(--cm-on-surface-variant)]">
                  <svg
                    className="w-4 h-4 shrink-0 mt-0.5"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="var(--cm-mint)"
                    strokeWidth="2.5"
                  >
                    <path d="M20 6L9 17l-5-5" />
                  </svg>
                  {b}
                </li>
              ))}
            </motion.ul>

            <motion.div
              className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3 gap-4"
              initial={{ opacity: 0, x: 16 }}
              animate={inView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.5, delay: 0.15 }}
            >
              {PILOT_TIERS(isES).map((tier) => (
                <div
                  key={tier.name}
                  className="card-cyber rounded-xl p-5 text-left border border-[var(--cm-signal)]/20"
                >
                  <p className="text-xs font-bold uppercase tracking-widest text-[var(--cm-signal)]">
                    {tier.name}
                  </p>
                  <p className="mt-2 text-2xl font-semibold text-[var(--cm-on-surface)]">
                    {tier.price}
                    <span className="text-sm font-normal text-[var(--cm-on-surface-variant)]">/mo</span>
                  </p>
                  <p className="mt-2 text-xs text-[var(--cm-on-surface-variant)] leading-relaxed">
                    {tier.scope}
                  </p>
                </div>
              ))}
            </motion.div>
          </div>
        </div>
      </section>
    </>
  );
}
