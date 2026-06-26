"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { USE_CASE_DEMOS, type UseCaseId } from "@/lib/useCaseDemos";
import UseCaseDemoModal from "@/components/UseCaseDemoModal";

export default function UseCasesSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [activeId, setActiveId] = useState<UseCaseId | null>(null);
  const activeCase = USE_CASE_DEMOS.find((c) => c.id === activeId) ?? null;
  const visibleCases = USE_CASE_DEMOS.filter((c) => ["agents", "procure", "inflation"].includes(c.id));

  return (
    <section id="use-cases" className="landing-section landing-section-glow animate-fade-in bg-white">
      <div className="landing-container-wide text-center">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-4">{isES ? "Casos de uso" : "Use cases"}</p>
          <h2 className="section-title">{isES ? "Tres puertas, mismos precios" : "Three doors, same prices"}</h2>
          <p className="section-intro">
            {isES
              ? "Developers, equipos de compras y analistas — misma data verificada, distinta superficie."
              : "Developers, procurement teams, and analysts — same verified data, different surface."}
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 landing-content-rail text-left mb-12">
          {visibleCases.map((c, i) => (
            <motion.button
              key={c.id}
              type="button"
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              onClick={() => setActiveId(c.id)}
              className="card-cyber card-cyber-interactive p-6 flex flex-col gap-3 hover:border-[var(--cm-mint)]/30 transition-colors text-left w-full cursor-pointer"
              aria-haspopup="dialog"
              aria-label={
                isES ? `Explorar demo: ${c.title_es}` : `Explore demo: ${c.title_en}`
              }
            >
              <span className="text-2xl" aria-hidden="true">
                {c.icon}
              </span>
              <h3 className="text-sm font-bold text-gray-900">{isES ? c.title_es : c.title_en}</h3>
              <div className="space-y-2 text-sm leading-relaxed flex-1">
                <p className="text-[var(--cm-on-surface-variant)]/60">
                  <span className="font-mono text-[10px] uppercase tracking-wider mr-2">
                    {isES ? "Antes" : "Before"}
                  </span>
                  {isES ? c.before_es : c.before_en}
                </p>
                <p className="text-[var(--cm-on-surface-variant)]">
                  <span className="font-mono text-[10px] uppercase tracking-wider text-[var(--cm-mint)] mr-2">
                    {isES ? "Con CLI Market" : "With CLI Market"}
                  </span>
                  {isES ? c.after_es : c.after_en}
                </p>
              </div>
              <span className="text-xs font-mono text-[var(--cm-mint)]">{isES ? "Explorar →" : "Explore →"}</span>
            </motion.button>
          ))}
        </div>

        <div className="flex flex-wrap justify-center gap-3">
          <a href="/#pricing" className="btn-mint">
            {isES ? "Planes Build →" : "Build plans →"}
          </a>
          <a href="/#intelligence" className="btn-outline">
            {isES ? "Intelligence →" : "Intelligence →"}
          </a>
        </div>
      </div>

      <UseCaseDemoModal open={activeId !== null} useCase={activeCase} onClose={() => setActiveId(null)} />
    </section>
  );
}
