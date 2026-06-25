"use client";
import { useLang } from "@/lib/LanguageContext";

export default function WhyNowSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  const cards = [
    {
      title: isES ? "Los agentes de IA pueden razonar" : "AI agents can reason",
      body: isES
        ? "Los modelos modernos pueden planificar, comparar y tomar decisiones."
        : "Modern models can plan, compare, and make decisions.",
    },
    {
      title: isES ? "El comercio sigue fragmentado" : "Commerce is still fragmented",
      body: isES
        ? "Los sistemas retail permanecen desconectados y difíciles de integrar."
        : "Retail systems remain disconnected and difficult to integrate.",
    },
    {
      title: isES ? "El dinero se vuelve programable" : "Money is becoming programmable",
      body: isES
        ? "Aprobaciones, procurement y pagos avanzan hacia la automatización basada en políticas."
        : "Approvals, procurement, and payments are moving toward policy-driven automation.",
    },
  ];

  return (
    <section id="why-now" className="landing-section animate-fade-in scroll-mt-24" style={{ backgroundColor: "#ffffff" }}>
      <div className="landing-container-wide text-center">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-4">{isES ? "POR QUÉ AHORA" : "WHY NOW"}</p>
          <h2 className="section-title text-[var(--cm-on-surface)]">
            {isES
              ? "Por qué el comercio agéntico emerge ahora"
              : "Why agentic commerce is emerging now"}
          </h2>
          <p className="section-intro">
            {isES ? "Tres cambios estructurales convergen." : "Three structural shifts are converging."}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-8">
          {cards.map((card, i) => (
            <div key={i} className="card-cyber rounded-2xl p-6 text-left">
              <h3 className="text-base font-semibold text-[var(--cm-on-surface)] mb-3">{card.title}</h3>
              <p className="text-sm leading-relaxed text-[var(--cm-on-surface-variant)]">{card.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
