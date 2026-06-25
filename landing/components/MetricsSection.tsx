"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

const BLOCKS = (isES: boolean) => [
  {
    id: "grafo",
    eyebrow: isES ? "Grafo Retail" : "Retail Graph",
    layers: [
      {
        value: `${MARKET_STATS.retailersDefined}`,
        label: isES ? "retailers descubiertos" : "retailers discovered",
        sub: isES ? "Retail Universe" : "Retail Universe",
        muted: true,
      },
      {
        value: `${MARKET_STATS.retailersVerified}`,
        label: isES ? "activos y healthy" : "active & healthy",
        sub: isES ? "Healthy Coverage" : "Healthy Coverage",
        muted: false,
      },
      {
        value: MARKET_STATS.pricesVerifiedLabel,
        label: isES ? "precios verificados" : "verified prices",
        sub: isES ? "Verified Catalog" : "Verified Catalog",
        muted: false,
      },
    ],
    footer: isES
      ? `${MARKET_STATS.countries} países · ${MARKET_STATS.platforms} plataformas`
      : `${MARKET_STATS.countries} countries · ${MARKET_STATS.platforms} platforms`,
  },
  {
    id: "motor",
    eyebrow: isES ? "Motor de Normalización" : "Normalization Engine",
    layers: [
      {
        value: "100%",
        label: isES ? "precios normalizados por kg/L/unidad" : "prices normalized per kg/L/unit",
        sub: isES ? "Calidad garantizada" : "Guaranteed quality",
        muted: false,
      },
      {
        value: `${MARKET_STATS.pricesRefreshHours}h`,
        label: isES ? "ciclo de refresh" : "refresh cycle",
        sub: isES ? "Datos frescos" : "Fresh data",
        muted: false,
      },
      {
        value: `${MARKET_STATS.indicatorsCount}`,
        label: isES ? "indicadores de mercado" : "market indicators",
        sub: isES ? "Intel continua" : "Continuous intel",
        muted: false,
      },
    ],
    footer: isES
      ? "Wikimedia · World Bank · IMF · Open-Meteo · Eurostat"
      : "Wikimedia · World Bank · IMF · Open-Meteo · Eurostat",
  },
  {
    id: "toolkit",
    eyebrow: isES ? "Toolkit para Agentes" : "Agent Toolkit",
    layers: [
      {
        value: `${MARKET_STATS.mcpTools}+`,
        label: isES ? "herramientas MCP (perfil default)" : "MCP tools (default profile)",
        sub: isES ? "Integración nativa" : "Native integration",
        muted: false,
      },
      {
        value: `${MARKET_STATS.mcpToolsFull}`,
        label: isES ? "tools en catálogo completo" : "tools in full catalog",
        sub: isES ? "Catálogo completo" : "Full catalog",
        muted: true,
      },
    ],
    badges: ["MCP", "REST API", "CLI", "SDK"],
    footer: isES
      ? "VTEX · Shopify · Magento · WooCommerce"
      : "VTEX · Shopify · Magento · WooCommerce",
  },
  {
    id: "inteligencia",
    eyebrow: isES ? "Inteligencia Histórica" : "Historical Intelligence",
    signals: isES
      ? [
          "Basket stress",
          "Inflation signals",
          "Price volatility",
          "Price Risk Index",
          "Procurement signals",
          "Macro gap vs CPI",
        ]
      : [
          "Basket stress",
          "Inflation signals",
          "Price volatility",
          "Price Risk Index",
          "Procurement signals",
          "Macro gap vs CPI",
        ],
    stat: {
      value: `${MARKET_STATS.indicatorsCount}`,
      label: isES ? "indicadores compuestos" : "composite indicators",
    },
    footer: isES
      ? "Antes que el IPC oficial · Para analistas y fondos"
      : "Before official CPI · For analysts and funds",
  },
];

export default function MetricsSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const blocks = BLOCKS(isES);

  return (
    <section
      id="metrics"
      className="landing-section animate-fade-in scroll-mt-24"
    >
      <div className="landing-container-wide">
        <div className="landing-section-header text-center">
          <p className="section-eyebrow mb-4">
            {isES ? "DEFENSABILIDAD" : "DEFENSIBILITY"}
          </p>
          <h2 className="section-title">
            {isES ? "El moat que no se copia." : "The moat that can't be copied."}
          </h2>
          <p className="section-intro">
            {isES
              ? "Cuatro capas de infraestructura que tardan años en construirse."
              : "Four infrastructure layers that take years to build."}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-10">
          {blocks.map((block) => (
            <div
              key={block.id}
              className="card-cyber p-6 flex flex-col gap-4"
            >
              <p className="text-xs font-bold uppercase tracking-widest text-[var(--cm-mint)]">
                {block.eyebrow}
              </p>

              {block.layers && (
                <div className="space-y-3">
                  {block.layers.map((layer) => (
                    <div key={layer.sub} className="flex items-baseline justify-between gap-3">
                      <div className="flex flex-col">
                        <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--cm-text-secondary)]">
                          {layer.sub}
                        </span>
                        <span className="text-xs text-[var(--cm-on-surface-variant)] leading-tight">
                          {layer.label}
                        </span>
                      </div>
                      <span
                        className={`text-2xl font-black font-mono tabular-nums shrink-0 ${
                          layer.muted
                            ? "text-[var(--cm-text-secondary)]"
                            : "text-[var(--cm-mint)]"
                        }`}
                      >
                        {layer.value}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {block.signals && (
                <div className="space-y-3">
                  <div className="flex items-baseline justify-between gap-3">
                    <span className="text-xs text-[var(--cm-on-surface-variant)]">
                      {block.stat!.label}
                    </span>
                    <span className="text-2xl font-black font-mono text-[var(--cm-mint)]">
                      {block.stat!.value}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {block.signals.map((s) => (
                      <span
                        key={s}
                        className="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--cm-surface-low)] border border-[var(--cm-outline-variant)] text-[var(--cm-on-surface-variant)]"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {block.badges && (
                <div className="flex flex-wrap gap-2">
                  {block.badges.map((b) => (
                    <span
                      key={b}
                      className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-[var(--cm-mint)]/10 border border-[var(--cm-mint)]/20 text-[var(--cm-mint)]"
                    >
                      {b}
                    </span>
                  ))}
                </div>
              )}

              {block.footer && (
                <p className="text-[10px] font-mono text-[var(--cm-text-secondary)] mt-auto pt-2 border-t border-[var(--cm-outline-variant)]">
                  {block.footer}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
