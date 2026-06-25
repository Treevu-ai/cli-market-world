"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function SolutionSection() {
  const { lang } = useLang();
  const isES = lang === "es";

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
      title_es: "Aprueba y paga en un solo flujo",
      title_en: "Approve and pay in one flow",
      body_es: "La mejor canasta va directo al flujo de aprobación. El gerente aprueba, el equipo paga con Yape o PayPal. Todo trazado.",
      body_en: "The best basket goes straight to an approval flow. Manager approves, team pays via Yape or PayPal. Fully audited.",
    },
  ];

  return (
    <section id="solution" className="landing-section animate-fade-in scroll-mt-24" style={{ backgroundColor: "#ffffff" }}>
      <div className="landing-container-wide">
        <div className="landing-section-header text-center">
          <p className="section-eyebrow mb-4">{isES ? "CÓMO FUNCIONA" : "HOW IT WORKS"}</p>
          <h2 className="section-title text-[var(--cm-on-surface)]">
            {isES
              ? "Del presupuesto a la orden en minutos"
              : "From budget to order in minutes"}
          </h2>
          <p className="section-intro">
            {isES
              ? "CLI Market conecta datos de precios en tiempo real con los flujos de aprobación y pago de tu equipo."
              : "CLI Market connects real-time price data with your team's approval and payment workflows."}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10">
          {steps.map((step) => (
            <div key={step.n} className="card-cyber rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <span className="w-7 h-7 rounded-full bg-[var(--cm-mint)] text-[#f8fafc] text-xs font-bold flex items-center justify-center shrink-0">
                  {step.n}
                </span>
                <h3 className="text-base font-semibold text-[var(--cm-on-surface)]">
                  {isES ? step.title_es : step.title_en}
                </h3>
              </div>
              <p className="text-sm leading-relaxed text-[var(--cm-on-surface-variant)]">
                {isES ? step.body_es : step.body_en}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
