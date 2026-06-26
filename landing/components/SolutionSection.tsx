"use client";
import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";

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
      body_es: "Una consulta cruza tiendas verificadas en segundos — para un agente, un comprador o un analista.",
      body_en: "One query scans verified stores in seconds — for an agent, a buyer, or an analyst.",
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
      title_es: "Elige cómo consumirla",
      title_en: "Choose how to consume it",
      body_es: "Build: API y MCP. Procure: comparar y aprobar sin código. Intelligence: spreads e inflación.",
      body_en: "Build: API and MCP. Procure: compare and approve without code. Intelligence: spreads and inflation.",
    },
  ];

  return (
    <section ref={ref} id="solution" className="landing-section landing-section-alt scroll-mt-24">
      <div className="landing-container-wide">
        <motion.div
          className="landing-section-header text-center"
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        >
          <p className="section-eyebrow mb-4">{isES ? "CÓMO FUNCIONA" : "HOW IT WORKS"}</p>
          <h2 className="section-title text-[var(--cm-on-surface)]">
            {isES ? "De la góndola a tu producto" : "From shelf to your product"}
          </h2>
          <p className="section-intro">
            {isES
              ? "Una capa de precios verificados y normalizados — consumida vía API, dashboard de compras o feeds de inteligencia."
              : "One verified, normalized price layer — consumed via API, procurement dashboard, or intelligence feeds."}
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
