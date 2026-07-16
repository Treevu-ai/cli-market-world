"use client";

import { motion } from "framer-motion";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import {
  CASE_STUDIES,
  CASE_STUDIES_CTA,
  CASE_STUDY_PRODUCT_LABELS,
  type CaseStudyProduct,
} from "@/lib/caseStudies";

const fadeUp = {
  initial: { opacity: 0, y: 20 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-40px" },
  transition: { duration: 0.45, ease: "easeOut" as const },
};

function productCta(product: CaseStudyProduct, isES: boolean) {
  const cta = CASE_STUDIES_CTA[product];
  const external = cta.href.startsWith("http");
  return (
    <a
      href={cta.href}
      className="text-xs font-mono text-[var(--cm-mint)] hover:underline mt-4 inline-block"
      {...(external ? { target: "_blank", rel: "noopener noreferrer" } : {})}
    >
      {isES ? cta.es : cta.en} →
    </a>
  );
}

export default function CaseStudiesPage() {
  const { lang } = useLang();
  const isES = lang === "es";

  const productCounts = CASE_STUDIES.reduce(
    (acc, c) => {
      acc[c.product] = (acc[c.product] ?? 0) + 1;
      return acc;
    },
    {} as Record<CaseStudyProduct, number>,
  );

  return (
    <main id="main-content" className="relative min-h-screen bg-[var(--cm-background)]">
      <div className="grid-bg fixed inset-0 opacity-40 pointer-events-none" aria-hidden="true" />
      <Navbar />

      <div className="relative z-10 pt-24 pb-16">
        <section className="landing-section">
          <div className="landing-container-wide">
            <div className="landing-section-header text-center mb-12">
              <p className="section-eyebrow mb-4">{isES ? "Prueba social" : "Social proof"}</p>
              <h1 className="section-title">{isES ? "Casos de estudio" : "Case studies"}</h1>
              <p className="section-intro mx-auto max-w-[640px]">
                {isES
                  ? `Equipos en fintech, trade, procurement y agentes IA usando la misma capa de precios — ${MARKET_STATS.pricesVerifiedLabel} precios verificados, refresh cada ${MARKET_STATS.pricesRefreshHours} h.`
                  : `Teams in fintech, trade, procurement, and AI agents on the same price layer — ${MARKET_STATS.pricesVerifiedLabel} verified prices, refreshed every ${MARKET_STATS.pricesRefreshHours}h.`}
              </p>
            </div>

            <div className="flex flex-wrap justify-center gap-3 mb-12">
              {(Object.keys(CASE_STUDY_PRODUCT_LABELS) as CaseStudyProduct[]).map((product) => {
                const label = CASE_STUDY_PRODUCT_LABELS[product];
                const count = productCounts[product] ?? 0;
                if (count === 0) return null;
                return (
                  <span
                    key={product}
                    className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-[11px] font-mono uppercase tracking-wider ${label.className}`}
                  >
                    {isES ? label.es : label.en}
                    <span className="opacity-70">{count}</span>
                  </span>
                );
              })}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5 landing-content-rail">
              {CASE_STUDIES.map((study, i) => {
                const productLabel = CASE_STUDY_PRODUCT_LABELS[study.product];
                return (
                  <motion.article
                    key={study.id}
                    {...fadeUp}
                    transition={{ ...fadeUp.transition, delay: i * 0.06 }}
                    className="card-cyber flex flex-col gap-4 p-6 text-left h-full"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <span className="text-2xl" aria-hidden="true">
                        {study.icon}
                      </span>
                      <span
                        className={`shrink-0 rounded-full border px-2.5 py-0.5 text-[10px] font-mono uppercase tracking-wider ${productLabel.className}`}
                      >
                        {isES ? productLabel.es : productLabel.en}
                      </span>
                    </div>

                    <div>
                      <h2 className="text-base font-bold text-[var(--cm-on-surface)] leading-snug">
                        {isES ? study.client_es : study.client_en}
                      </h2>
                    </div>

                    <div className="space-y-3 text-sm leading-relaxed flex-1">
                      <div>
                        <p className="font-mono text-[10px] uppercase tracking-wider text-[var(--cm-on-surface-variant)]/60 mb-1">
                          {isES ? "Problema" : "Problem"}
                        </p>
                        <p className="text-[var(--cm-on-surface-variant)]">
                          {isES ? study.problem_es : study.problem_en}
                        </p>
                      </div>
                      <div>
                        <p className="font-mono text-[10px] uppercase tracking-wider text-[var(--cm-mint)] mb-1">
                          {isES ? "Solución" : "Solution"}
                        </p>
                        <p className="text-[var(--cm-on-surface-variant)]">
                          {isES ? study.solution_es : study.solution_en}
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-2 pt-2 border-t border-[var(--cm-outline-variant)]/25">
                      {study.metrics.map((m) => (
                        <div key={m.label_es} className="text-center px-1">
                          <p className="text-sm font-bold text-[var(--cm-on-surface)] leading-tight">{m.value}</p>
                          <p className="text-[10px] text-[var(--cm-on-surface-variant)]/70 leading-snug mt-0.5">
                            {isES ? m.label_es : m.label_en}
                          </p>
                        </div>
                      ))}
                    </div>

                    {productCta(study.product, isES)}
                  </motion.article>
                );
              })}
            </div>

            <div className="mt-16 text-center rounded-2xl border border-[var(--cm-outline-variant)]/30 bg-[var(--cm-surface-low)]/40 px-6 py-10">
              <h2 className="section-title text-xl mb-3">
                {isES ? "¿Tu caso encaja aquí?" : "Does your use case fit?"}
              </h2>
              <p className="section-intro mx-auto max-w-[520px] mb-6">
                {isES
                  ? "Cuéntanos tu país, categorías y equipo — respondemos en el mismo día hábil."
                  : "Tell us your country, categories, and team — we reply the same business day."}
              </p>
              <div className="flex flex-wrap justify-center gap-3">
                <a href="/contact?topic=intelligence#contact-intelligence" className="btn-mint">
                  {isES ? "Asesores" : "Advisors"}
                </a>
                <a href="/contact?topic=procure#contact-procure" className="btn-outline">
                  {isES ? "Procure" : "Procure"}
                </a>
                <a href="/retailers" className="btn-outline">
                  {isES ? "Retailers" : "Retailers"}
                </a>
              </div>
            </div>
          </div>
        </section>

        <Footer />
      </div>
    </main>
  );
}
