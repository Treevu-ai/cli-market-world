"use client";
import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { PROCURE_SITE_URL } from "@/lib/procurePlans";

export default function WhoItsForSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  const cards = [
    {
      title_es: "Builders",
      title_en: "Builders",
      body_es: "MCP y API para agentes que consultan precios en código.",
      body_en: "MCP and API for agents that query prices in code.",
      cta_es: "Explorar Docs →",
      cta_en: "Explore Docs →",
      href: "/docs",
    },
    {
      title_es: "Equipos de compras",
      title_en: "Procurement teams",
      body_es: "Comparar precios entre retailers sin hojas de cálculo.",
      body_en: "Compare prices across retailers without spreadsheets.",
      cta_es: "Ver Procure →",
      cta_en: "See Procure →",
      href: `${PROCURE_SITE_URL}/procure`,
      external: true,
    },
    {
      title_es: "Analistas y fintech",
      title_en: "Analysts & fintech",
      body_es: "Datos estructurados, índices y reportes para decisiones.",
      body_en: "Structured data, indices, and reports for decisions.",
      cta_es: "Explorar Intelligence →",
      cta_en: "Explore Intelligence →",
      href: "/intelligence",
    },
  ];

  return (
    <section ref={ref} id="who-its-for" className="landing-section landing-section-alt scroll-mt-24">
      <div className="landing-container-wide text-center">
        <motion.div
          className="landing-section-header"
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        >
          <p className="section-eyebrow mb-4">{isES ? "PARA QUIÉN ES" : "WHO IT'S FOR"}</p>
          <h2 className="section-title text-[var(--cm-on-surface)]">
            {isES ? "Tres puertas, tres perfiles" : "Three doors, three profiles"}
          </h2>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mt-8 max-w-4xl mx-auto">
          {cards.map((card, i) => (
            <motion.div
              key={i}
              className="card-cyber rounded-2xl p-6 text-left flex flex-col"
              initial={{ opacity: 0, y: 32 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.55, delay: 0.1 + i * 0.08, ease: [0.16, 1, 0.3, 1] }}
            >
              <h3 className="text-base font-semibold text-[var(--cm-on-surface)] mb-3">
                {isES ? card.title_es : card.title_en}
              </h3>
              <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed mb-6 flex-1">
                {isES ? card.body_es : card.body_en}
              </p>
              <a
                href={card.href}
                className="text-sm font-semibold text-[var(--cm-mint)] hover:underline"
                {...("external" in card && card.external
                  ? { target: "_blank", rel: "noopener noreferrer" }
                  : {})}
              >
                {isES ? card.cta_es : card.cta_en}
              </a>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
