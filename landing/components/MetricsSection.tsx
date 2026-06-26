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
        label: isES ? "descubiertos" : "discovered",
        muted: true,
      },
      {
        value: `${MARKET_STATS.retailersVerified}`,
        label: isES ? "activos y healthy" : "active & healthy",
        muted: false,
      },
      {
        value: MARKET_STATS.pricesVerifiedLabel,
        label: isES ? "precios verificados" : "verified prices",
        muted: false,
      },
    ],
  },
  {
    id: "motor",
    eyebrow: isES ? "Motor de Normalización" : "Normalization Engine",
    layers: [
      {
        value: "100%",
        label: isES ? "normalizados kg/L/unidad" : "normalized kg/L/unit",
        muted: false,
      },
      {
        value: `${MARKET_STATS.pricesRefreshHours}h`,
        label: isES ? "refresh" : "refresh",
        muted: false,
      },
    ],
  },
  {
    id: "toolkit",
    eyebrow: isES ? "Toolkit para Agentes" : "Agent Toolkit",
    layers: [
      {
        value: `${MARKET_STATS.mcpTools}+`,
        label: isES ? "herramientas MCP" : "MCP tools",
        muted: false,
      },
    ],
    badges: ["MCP", "REST API", "CLI", "SDK"],
  },
  {
    id: "inteligencia",
    eyebrow: isES ? "Inteligencia Histórica" : "Historical Intelligence",
    signals: isES
      ? ["Inflation", "Volatility", "Price Risk", "Macro vs CPI"]
      : ["Inflation", "Volatility", "Price Risk", "Macro vs CPI"],
    stat: {
      value: `${MARKET_STATS.indicatorsCount}`,
      label: isES ? "indicadores" : "indicators",
    },
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
                    <div key={layer.label} className="flex items-baseline justify-between gap-3">
                      <span className="text-xs text-[var(--cm-on-surface-variant)] leading-tight">
                        {layer.label}
                      </span>
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
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
