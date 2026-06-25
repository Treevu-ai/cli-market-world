"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function MetricsSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  const pypiLabel = `${(MARKET_STATS.pypiDownloads / 1000).toFixed(1)}K+`;
  const usageMetrics = [
    { value: pypiLabel, label: isES ? "instalaciones PyPI" : "PyPI installs" },
    { value: `${MARKET_STATS.mcpTools}`, label: isES ? "herramientas MCP" : "MCP tools" },
    { value: "33,728", label: isES ? "snapshots diarios" : "daily snapshots" },
  ];

  const coverageMetrics = [
    { value: MARKET_STATS.pricesVerifiedLabel, label: isES ? "precios activos" : "active prices" },
    { value: `${MARKET_STATS.indicatorsCount}`, label: isES ? "indicadores" : "indicators" },
    { value: `${MARKET_STATS.platforms}`, label: isES ? "plataformas de comercio" : "commerce platforms" },
  ];

  const platforms = ["VTEX", "Shopify", "Magento", "WooCommerce"];

  return (
    <section
      id="metrics"
      className="landing-section animate-fade-in scroll-mt-24"
    >
      <div className="landing-container-wide text-center">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-4">
            {isES ? "MÉTRICAS" : "METRICS"}
          </p>
          <h2 className="section-title">
            {isES ? "Infraestructura real. Uso real." : "Real infrastructure. Real usage."}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-10">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-[var(--cm-on-surface-variant)] mb-6">
              {isES ? "Uso" : "Usage"}
            </p>
            <div className="grid grid-cols-3 gap-4">
              {usageMetrics.map((m, i) => (
                <div key={i} className="text-center">
                  <p className="text-3xl font-black font-mono tabular-nums text-[var(--cm-mint)]">{m.value}</p>
                  <p className="text-xs mt-1 text-[var(--cm-text-secondary)]">{m.label}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-[var(--cm-on-surface-variant)] mb-6">
              {isES ? "Cobertura" : "Coverage"}
            </p>
            <div className="grid grid-cols-3 gap-4">
              {coverageMetrics.map((m, i) => (
                <div key={i} className="text-center">
                  <p className="text-3xl font-black font-mono tabular-nums text-[var(--cm-on-surface)]">{m.value}</p>
                  <p className="text-xs mt-1 text-[var(--cm-text-secondary)]">{m.label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
          {platforms.map((p) => (
            <span
              key={p}
              className="text-xs font-semibold font-mono px-3 py-1.5 rounded-full bg-[var(--cm-surface-low)] border border-[var(--cm-outline-variant)] text-[var(--cm-text-secondary)]"
            >
              {p}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
