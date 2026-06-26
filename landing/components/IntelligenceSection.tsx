"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";

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
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  const bullets = isES
    ? [
        "Spreads entre retailers (mismo producto comparable)",
        "Inflación por línea y país (7 / 30 / 90 días)",
        "Canasta básica con reglas de comparabilidad explícitas",
        "Capa clean / flagged / citable — sin outliers sin filtrar",
      ]
    : [
        "Cross-retailer spreads (comparable products)",
        "Category inflation by country (7 / 30 / 90 days)",
        "Basic basket with explicit comparability rules",
        "Clean / flagged / citable layer — no unfiltered outliers",
      ];

  return (
    <section
      ref={ref}
      id="intelligence"
      className="landing-section scroll-mt-24"
      style={{ backgroundColor: "#ffffff" }}
    >
      <div className="landing-container-wide">
        <motion.div
          className="landing-section-header text-center"
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        >
          <p className="section-eyebrow mb-4">INTELLIGENCE</p>
          <h2 className="section-title text-[var(--cm-on-surface)]">
            {isES ? (
              <>
                Señales de retail <span className="text-gradient-orange">antes del IPC</span>
              </>
            ) : (
              <>
                Retail signals <span className="text-gradient-orange">before CPI</span>
              </>
            )}
          </h2>
          <p className="section-intro text-[var(--cm-on-surface-variant)] max-w-[640px] mx-auto">
            {isES
              ? "Para pricing, trade marketing, fintech y consultoras — spreads, inflación y canasta desde góndola real."
              : "For pricing, trade marketing, fintech, and consultancies — spreads, inflation, and basket from real shelf data."}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-10 items-start">
          <motion.ul
            className="space-y-3"
            initial={{ opacity: 0, x: -16 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            {bullets.map((b) => (
              <li key={b} className="flex items-start gap-2.5 text-sm text-[var(--cm-on-surface-variant)]">
                <svg
                  className="w-4 h-4 shrink-0 mt-0.5 text-[#0369a1]"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
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
              <div key={tier.name} className="card-cyber rounded-xl p-5 text-left border border-[#0369a1]/15">
                <p className="text-xs font-bold uppercase tracking-widest text-[#0369a1]">{tier.name}</p>
                <p className="mt-2 text-2xl font-semibold text-[#0f172a]">
                  {tier.price}
                  <span className="text-sm font-normal text-[#64748b]">/mo</span>
                </p>
                <p className="mt-2 text-xs text-[#64748b] leading-relaxed">{tier.scope}</p>
              </div>
            ))}
          </motion.div>
        </div>

        <motion.div
          className="mt-10 flex flex-wrap justify-center gap-3"
          initial={{ opacity: 0, y: 12 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <a href="/contact#contact-intelligence" className="btn-mint">
            {isES ? "Solicitar piloto →" : "Request pilot →"}
          </a>
          <a
            href="/intelligence-pilot-es.md"
            className="btn-outline"
            target="_blank"
            rel="noopener noreferrer"
          >
            {isES ? "One-pager Intelligence →" : "Intelligence one-pager →"}
          </a>
        </motion.div>
      </div>
    </section>
  );
}
