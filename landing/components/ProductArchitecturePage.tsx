"use client";

import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

const LAYERS = [
  { n: "01", es: "Ingestión", en: "Ingestion", descEs: "Scrapers nativos VTEX, Shopify, Magento y WooCommerce capturan precios de góndola cada 4 horas en 8 países. Sin APIs de retailers — leemos lo que ve el comprador.", descEn: "Native VTEX, Shopify, Magento, and WooCommerce scrapers capture shelf prices every 4 hours across 8 countries. No retailer APIs — we read what the buyer sees." },
  { n: "02", es: "Normalización", en: "Normalization", descEs: "Precios normalizados por kg/L. Entity resolution cross-retailer. Golden Records con linkage de identical products. Filtros de calidad por confianza de snapshot.", descEn: "Prices normalized per kg/L. Cross-retailer entity resolution. Golden Records with identical-product linkage. Quality filters by snapshot confidence." },
  { n: "03", es: "Inteligencia", en: "Intelligence", descEs: "Inflación desde góndola, spreads por categoría, basket stress index, retail aggression scores. Todo calculado sobre datos reales, no encuestas.", descEn: "Shelf inflation, category spreads, basket stress index, retail aggression scores. All computed from real data, not surveys." },
  { n: "04", es: "Workflows", en: "Workflows", descEs: "API + CLI + tools. Search, compare, basket optimization, checkout. Integrable en agentes de IA, dashboards y sistemas de procurement.", descEn: "API + CLI + tools. Search, compare, basket optimization, checkout. Integrable into AI agents, dashboards, and procurement systems." },
];

export default function ProductArchitecturePage() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <main className="min-h-screen bg-[var(--cm-background)] pt-24 pb-20">
      <div className="landing-container-wide max-w-[880px] mx-auto">
        <section className="text-center mb-20">
          <p className="section-eyebrow mb-4">
            {isES ? "Arquitectura" : "Architecture"}
          </p>
          <h1 className="font-display text-[clamp(2rem,5vw,3.5rem)] font-bold text-[var(--cm-on-surface)] mb-4 tracking-tight">
            {isES ? "Cómo CLI Market convierte góndolas en inteligencia" : "How CLI Market turns shelves into intelligence"}
          </h1>
          <p className="text-lg text-[var(--cm-on-surface-variant)] max-w-[640px] mx-auto leading-relaxed">
            {isES
              ? `Cuatro capas que transforman ${MARKET_STATS.pricesVerifiedLabel} precios de góndola en ${MARKET_STATS.retailersVerified} retailers de ${MARKET_STATS.countries} países en datos accionables para desarrolladores, equipos de compras y agentes de IA.`
              : `Four layers that transform ${MARKET_STATS.pricesVerifiedLabel} shelf prices across ${MARKET_STATS.retailersVerified} retailers in ${MARKET_STATS.countries} countries into actionable data for developers, procurement teams, and AI agents.`}
          </p>
        </section>

        <section className="mb-20">
          <div className="grid gap-1">
            {LAYERS.map((layer) => (
              <div
                key={layer.n}
                className="flex items-start gap-6 p-8 rounded-lg border border-[var(--cm-outline-variant)]/20 hover:border-[var(--cm-mint)]/30 transition-colors"
              >
                <span className="font-mono text-3xl font-bold text-[var(--cm-mint)]/30 shrink-0 w-14">
                  {layer.n}
                </span>
                <div>
                  <h3 className="font-semibold text-[var(--cm-on-surface)] text-xl mb-2">
                    {isES ? layer.es : layer.en}
                  </h3>
                  <p className="text-[var(--cm-on-surface-variant)] leading-relaxed text-base">
                    {isES ? layer.descEs : layer.descEn}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="text-center py-16 rounded-2xl bg-gradient-to-b from-[var(--cm-surface-low)] to-[var(--cm-background)] border border-[var(--cm-outline-variant)]/20">
          <p className="text-xs font-mono text-[var(--cm-mint)]/60 mb-4">
            {isES ? `${MARKET_STATS.retailersPhraseEs} · ${MARKET_STATS.platformsPhraseEs}` : `${MARKET_STATS.retailersPhraseEn} · ${MARKET_STATS.platformsPhraseEn}`}
          </p>
          <h2 className="font-display text-2xl font-bold text-[var(--cm-on-surface)] mb-4">
            {isES ? "Una plataforma. Cero scraping." : "One platform. Zero scraping."}
          </h2>
          <a
            href="/build#pricing"
            className="inline-flex items-center rounded-3xl bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-sm font-semibold px-6 py-3 hover:brightness-110 transition-all"
          >
            {isES ? "Ver planes →" : "See plans →"}
          </a>
        </section>
      </div>
    </main>
  );
}
