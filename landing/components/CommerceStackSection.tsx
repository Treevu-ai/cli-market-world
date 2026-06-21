"use client";
import { useLang } from "@/lib/LanguageContext";

const STEPS = [
  {
    num: "1",
    title_en: "Intelligence",
    title_es: "Inteligencia",
    question_en: "What should be bought?",
    question_es: "¿Qué debe comprarse?",
    desc_en: "Track price spreads, inflation signals, and product availability.",
    desc_es: "Monitorea spreads de precio, señales de inflación y disponibilidad de productos.",
  },
  {
    num: "2",
    title_en: "Decision",
    title_es: "Decisión",
    question_en: "Where should it be bought?",
    question_es: "¿Dónde debe comprarse?",
    desc_en: "Compare retailers and optimize total basket cost.",
    desc_es: "Compara retailers y optimiza el costo total de la canasta.",
  },
  {
    num: "3",
    title_en: "Execution",
    title_es: "Ejecución",
    question_en: "Can the purchase be approved and completed?",
    question_es: "¿Puede la compra ser aprobada y completada?",
    desc_en: "Run approvals, checkout, and procurement workflows.",
    desc_es: "Ejecuta aprobaciones, checkout y flujos de procurement.",
  },
  {
    num: "4",
    title_en: "Settlement (emerging)",
    title_es: "Liquidación (en desarrollo)",
    question_en: "Can funds move under policy constraints?",
    question_es: "¿Pueden moverse los fondos bajo restricciones de política?",
    desc_en: "Enable programmable approvals and payment orchestration.",
    desc_es: "Habilita aprobaciones programables y orquestación de pagos.",
  },
];

export default function CommerceStackSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="architecture" className="landing-section animate-fade-in scroll-mt-24">
      <div className="landing-container-wide text-center">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-4">{isES ? "ARQUITECTURA" : "ARCHITECTURE"}</p>
          <h2 className="section-title text-[var(--cm-on-surface)]">
            {isES ? "El stack de comercio agéntico" : "The agentic commerce stack"}
          </h2>
          <p className="section-intro">
            {isES
              ? "CLI Market impulsa la capa de decisión antes de que el dinero se mueva."
              : "CLI Market powers the decision layer before money moves."}
          </p>
        </div>

        <div className="mx-auto mt-10 max-w-lg">
          {STEPS.map((step, i) => (
            <div key={i}>
              <div className="card-cyber rounded-2xl p-6 text-left">
                <div className="flex items-start gap-4">
                  <span className="w-8 h-8 rounded-full bg-[var(--cm-mint)] text-[#09090B] text-sm font-bold flex items-center justify-center shrink-0 mt-0.5">
                    {step.num}
                  </span>
                  <div>
                    <h3 className="text-base font-semibold text-[var(--cm-on-surface)] mb-1">
                      {isES ? step.title_es : step.title_en}
                    </h3>
                    <p className="text-xs font-mono text-[var(--cm-on-surface-variant)] mb-2">
                      {isES ? step.question_es : step.question_en}
                    </p>
                    <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
                      {isES ? step.desc_es : step.desc_en}
                    </p>
                  </div>
                </div>
              </div>
              {i < STEPS.length - 1 && (
                <div className="flex justify-center my-2" aria-hidden="true">
                  <svg width="16" height="24" viewBox="0 0 16 24" fill="none">
                    <path d="M8 0v20M2 14l6 8 6-8" stroke="var(--cm-mint)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
