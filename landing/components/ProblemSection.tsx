"use client";
import { useLang } from "@/lib/LanguageContext";

export default function ProblemSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  const cards = [
    {
      title: isES ? "Precios que no se pueden comparar" : "Prices you can't actually compare",
      body: isES
        ? "Cada tienda usa presentaciones, unidades y categorías distintas. Comparar S/ 4.90 de 900 g contra S/ 5.20 de 1 kg a mano es lento y propenso a errores."
        : "Every store uses different pack sizes, units, and categories. Manually comparing S/ 4.90 for 900 g vs S/ 5.20 for 1 kg is slow and error-prone.",
    },
    {
      title: isES ? "Horas perdidas cada semana" : "Hours lost every week",
      body: isES
        ? "Los equipos de compras invierten entre 4 y 8 horas semanales cotizando en múltiples tiendas, actualizando hojas de cálculo y persiguiendo aprobaciones."
        : "Procurement teams spend 4–8 hours a week quoting across stores, updating spreadsheets, and chasing approvals.",
    },
    {
      title: isES ? "Sin visibilidad ni control" : "No visibility or control",
      body: isES
        ? "Sin historial de precios, sin alertas de subida, sin trazabilidad de quién aprobó qué. Las decisiones de compra quedan opacas para la gerencia."
        : "No price history, no spike alerts, no audit trail of who approved what. Purchasing decisions remain opaque to management.",
    },
  ];

  return (
    <section
      id="problem"
      className="landing-section animate-fade-in scroll-mt-24"
      style={{ backgroundColor: "#ffffff" }}
    >
      <div className="landing-container-wide text-center">
        <div className="landing-section-header">
          <h2 className="section-title text-[#0f172a]">
            {isES
              ? "Comprar bien no debería costar tanto tiempo"
              : "Buying smart shouldn't cost so much time"}
          </h2>
          <p className="section-intro text-[#64748b]">
            {isES
              ? "Los equipos de compras de LATAM comparan precios a mano, en múltiples tiendas, cada semana. Con datos que cambian cada pocas horas. Sin automatización que los ayude."
              : "LATAM procurement teams compare prices manually, across multiple stores, every week — with data that changes every few hours and no automation to help."}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-8">
          {cards.map((card, i) => (
            <div
              key={i}
              className="rounded-2xl p-6 text-left bg-[#f1f5f9] border border-[#e2e8f0]"
            >
              <h3 className="text-base font-semibold text-[#0f172a] mb-3">{card.title}</h3>
              <p className="text-sm leading-relaxed text-[#64748b]">{card.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
