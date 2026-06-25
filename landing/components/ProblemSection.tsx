"use client";
import { useLang } from "@/lib/LanguageContext";

export default function ProblemSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  const cards = [
    {
      title: isES ? "Sistemas retail fragmentados" : "Fragmented retail systems",
      body: isES
        ? "Cada retailer usa catálogos, formatos de empaque, unidades y taxonomías distintas. Comparar precios de forma confiable se vuelve imposible."
        : "Each retailer uses different catalogs, packaging formats, units, and product taxonomies. Comparable pricing becomes difficult.",
    },
    {
      title: isES ? "Integraciones frágiles" : "Fragile integrations",
      body: isES
        ? "Los scrapers se rompen. Los parsers degradan. Las integraciones acumulan deuda de mantenimiento. Los equipos pierden tiempo manteniendo pipelines vivos."
        : "Scrapers break. Parsers degrade. Integrations become maintenance debt. Engineering teams waste time keeping pipelines alive.",
    },
    {
      title: isES ? "Rieles de ejecución faltantes" : "Missing execution rails",
      body: isES
        ? "Los agentes pueden recomendar compras. Todavía no pueden comparar, armar canastas, aprobar y ejecutar transacciones de forma confiable."
        : "Agents can recommend purchases. They still cannot reliably compare, basket, approve, and execute transactions.",
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
              ? "Los agentes de IA pueden razonar. Todavía no pueden transaccionar."
              : "AI agents can reason. They still cannot transact."}
          </h2>
          <p className="section-intro text-[#64748b]">
            {isES
              ? "Los modelos de lenguaje pueden analizar productos, recomendar proveedores y optimizar decisiones. Pero el comercio real sigue fragmentado. Esa fragmentación crea una brecha mayor entre inteligencia y ejecución."
              : "Large language models can analyze products, recommend suppliers, and optimize decisions. But real-world commerce remains fragmented. That fragmentation creates a major gap between intelligence and execution."}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-8">
          {cards.map((card, i) => (
            <div
              key={i}
              className="rounded-2xl p-6 text-left bg-[#f1f5f9] border border-[#e2e8f0]"
            >
              <h3 className="text-base font-semibold text-[#0f172a] mb-3">{card.title}</h3>
              <p className="text-sm leading-relaxed text-[#64748b]">
                {card.body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
