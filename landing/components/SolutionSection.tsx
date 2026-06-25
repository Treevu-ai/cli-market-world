"use client";
import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function SolutionSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  const steps = [
    {
      n: "1",
      title_es: "Busca en todos los retailers a la vez",
      title_en: "Search every retailer at once",
      body_es: `Escribe el producto y CLI Market consulta ${MARKET_STATS.retailersVerified} tiendas verificadas en segundos. Sin abrir pestañas ni copiar precios.`,
      body_en: `Type the product and CLI Market queries ${MARKET_STATS.retailersVerified} verified stores in seconds. No tabs to open, no prices to copy.`,
    },
    {
      n: "2",
      title_es: "Precios normalizados, listos para comparar",
      title_en: "Normalized prices, ready to compare",
      body_es: "Cada precio se convierte a la misma unidad — por kg, por litro, por unidad — para que la comparación sea justa y sin cálculos manuales.",
      body_en: "Every price is converted to the same unit — per kg, per litre, per unit — so comparison is fair and calculation-free.",
    },
    {
      n: "3",
      title_es: "Integra en tu agente — API, MCP o Procure",
      title_en: "Integrate into your agent — API, MCP, or Procure",
      body_es: "Consume vía REST, Python SDK o MCP tools. Tu agente ejecuta con datos frescos; los equipos operativos usan Procure Copilot para aprobaciones y checkout.",
      body_en: "Consume via REST, Python SDK, or MCP tools. Your agent executes with fresh data; operational teams use Procure Copilot for approvals and checkout.",
    },
  ];

  return (
    <section ref={ref} id="solution" className="landing-section scroll-mt-24" style={{ backgroundColor: "#ffffff" }}>
      <div className="landing-container-wide">
        <motion.div
          className="landing-section-header text-center"
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        >
          <p className="section-eyebrow mb-4">{isES ? "CÓMO FUNCIONA" : "HOW IT WORKS"}</p>
          <h2 className="section-title text-[var(--cm-on-surface)]">
            {isES
              ? "De la consulta a la ejecución en segundos"
              : "From query to execution in seconds"}
          </h2>
          <p className="section-intro">
            {isES
              ? "CLI Market expone toda la infraestructura retail de LatAm a tu agente — una API, herramientas MCP y SDK. Sin scraping. Sin normalización manual."
              : "CLI Market exposes all of LatAm's retail infrastructure to your agent — one API, MCP tools, and SDK. No scraping. No manual normalization."}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10">
          {steps.map((step, i) => (
            <motion.div
              key={step.n}
              className="card-cyber rounded-2xl p-6"
              initial={{ opacity: 0, y: 32 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.55, delay: 0.1 + i * 0.1, ease: [0.16, 1, 0.3, 1] }}
            >
              <div className="flex items-center gap-3 mb-4">
                <span className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-xs font-bold text-white" style={{ background: "linear-gradient(180deg, #f97316 0%, #ea580c 100%)" }}>
                  {step.n}
                </span>
                <h3 className="text-base font-semibold text-[var(--cm-on-surface)]">
                  {isES ? step.title_es : step.title_en}
                </h3>
              </div>
              <p className="text-sm leading-relaxed text-[var(--cm-on-surface-variant)]">
                {isES ? step.body_es : step.body_en}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
