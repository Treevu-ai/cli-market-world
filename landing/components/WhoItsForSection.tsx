"use client";
import { useLang } from "@/lib/LanguageContext";

export default function WhoItsForSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  const cards = [
    {
      title_en: "Developers",
      title_es: "Desarrolladores",
      body_en: "Build shopping agents, copilots, and AI-native commerce products.",
      body_es: "Construye agentes de compras, copilots y productos de comercio nativos para IA.",
      features_en: ["Python SDK", "CLI", "REST API", "MCP tools"],
      features_es: ["Python SDK", "CLI", "REST API", "Herramientas MCP"],
      cta_en: "Explore Docs →",
      cta_es: "Explorar Docs →",
      href: "/docs",
    },
    {
      title_en: "Procurement Teams",
      title_es: "Equipos de Procurement",
      body_en: "Reduce sourcing time and automate approvals.",
      body_es: "Reduce el tiempo de abastecimiento y automatiza las aprobaciones.",
      features_en: ["basket optimization", "approval workflows", "integrated payment", "audit trail"],
      features_es: ["optimización de canasta", "flujos de aprobación", "pago integrado", "trazabilidad"],
      cta_en: "Explore Procure →",
      cta_es: "Explorar Procure →",
      href: "/procure",
    },
    {
      title_en: "Analysts & Funds",
      title_es: "Analistas y Fondos",
      body_en: "Track retail signals before traditional datasets update.",
      body_es: "Monitorea señales de retail antes de que los datasets tradicionales se actualicen.",
      features_en: ["historical pricing", "spread analysis", "market indicators"],
      features_es: ["historial de precios", "análisis de spreads", "indicadores de mercado"],
      cta_en: "Explore Intelligence →",
      cta_es: "Explorar Intelligence →",
      href: "/#intelligence",
    },
  ];

  return (
    <section id="who-its-for" className="landing-section animate-fade-in scroll-mt-24" style={{ backgroundColor: "#ffffff" }}>
      <div className="landing-container-wide text-center">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-4">{isES ? "PARA QUIÉN ES" : "WHO IT'S FOR"}</p>
          <h2 className="section-title text-[var(--cm-on-surface)]">
            {isES ? "Para equipos que ejecutan compras a escala" : "For teams that execute purchasing at scale"}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-8">
          {cards.map((card, i) => (
            <div key={i} className="card-cyber rounded-2xl p-6 text-left flex flex-col">
              <h3 className="text-base font-semibold text-[var(--cm-on-surface)] mb-3">
                {isES ? card.title_es : card.title_en}
              </h3>
              <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed mb-4">
                {isES ? card.body_es : card.body_en}
              </p>
              <ul className="space-y-1.5 mb-6 flex-1">
                {(isES ? card.features_es : card.features_en).map((f, j) => (
                  <li key={j} className="flex items-center gap-2 text-xs text-[var(--cm-on-surface-variant)]">
                    <svg className="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="var(--cm-mint)" strokeWidth="2.5">
                      <path d="M20 6L9 17l-5-5" />
                    </svg>
                    {f}
                  </li>
                ))}
              </ul>
              <a
                href={card.href}
                className="text-sm font-semibold text-[var(--cm-mint)] hover:underline"
              >
                {isES ? card.cta_es : card.cta_en}
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
