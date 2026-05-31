"use client";
import { useLang } from "@/lib/LanguageContext";

const cases = [
  {
    icon: "📊",
    title_es: "Pricing & market intelligence",
    title_en: "Pricing & market intelligence",
    desc_es: "Spreads, inflación y canasta con capa clean/flagged/citable. Piloto Intelligence desde USD 300/mes.",
    desc_en: "Spreads, inflation, and basket with clean/flagged/citable layer. Intelligence pilot from USD 300/mo.",
    href: "#pricing-intelligence",
  },
  {
    icon: "🏛",
    title_es: "Bureaus & inteligencia comercial",
    title_en: "Bureaus & commercial intelligence",
    desc_es: "Multi-retailer y multi-país por una API — enriquece reportes sin panel legacy de USD 500+/mes.",
    desc_en: "Multi-retailer, multi-country via one API — enrich reports without legacy USD 500+/mo panels.",
    href: "#pricing-intelligence",
  },
  {
    icon: "💳",
    title_es: "Fintech & modelos de riesgo",
    title_en: "Fintech & risk models",
    desc_es: "Canasta e inflación alimentaria con refresh cada 8 h — alternativa a fuentes con 30–45 días de retraso.",
    desc_en: "Basket and food inflation with 8 h refresh — alternative to sources lagging 30–45 days.",
    href: "#pricing-intelligence",
  },
  {
    icon: "🤖",
    title_es: "Agentes de compra",
    title_en: "Shopping agents",
    desc_es: "Search, compare y canastas con 36 herramientas MCP. Build Free/Pro — checkout autónomo en roadmap.",
    desc_en: "Search, compare, and baskets with 36 MCP tools. Build Free/Pro — autonomous checkout on the roadmap.",
    href: "#pricing-build",
  },
];

export default function UseCasesSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="casos" className="landing-section animate-fade-in">
      <div className="landing-container text-center">
        <p className="section-eyebrow mb-4">
          {isES ? "Casos de uso" : "Use cases"}
        </p>
        <h2 className="section-title mb-2">
          {isES ? "Mismo moat. Dos caminos." : "Same moat. Two paths."}
        </h2>
        <p className="text-sm text-[var(--cm-on-surface-variant)] max-w-xl mx-auto mb-10">
          {isES
            ? "Intelligence para equipos comerciales; Build para quien integra agentes — sobre los mismos precios verificados."
            : "Intelligence for commercial teams; Build for agent integrators — on the same verified prices."}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-[800px] mx-auto text-left mb-10">
          {cases.map((c) => (
            <a
              key={c.title_es}
              href={c.href}
              className="card-cyber p-6 flex flex-col gap-3 hover:border-[var(--cm-mint)]/30 transition-colors"
            >
              <span className="text-2xl" aria-hidden="true">{c.icon}</span>
              <h3 className="text-sm font-bold text-white">
                {isES ? c.title_es : c.title_en}
              </h3>
              <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed flex-1">
                {isES ? c.desc_es : c.desc_en}
              </p>
              <span className="text-xs font-mono text-[var(--cm-mint)]">
                {isES ? "Ver planes →" : "View plans →"}
              </span>
            </a>
          ))}
        </div>

        <a
          href="#pricing"
          className="btn-mint"
        >
          {isES ? "Ver planes Build + Intelligence →" : "View Build + Intelligence plans →"}
        </a>
      </div>
    </section>
  );
}
