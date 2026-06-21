"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function MetricsSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  const usageMetrics = [
    { value: "40.9K+", label: isES ? "instalaciones PyPI" : "PyPI installs" },
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
      style={{ backgroundColor: "#0A2540" }}
    >
      <div className="landing-container-wide text-center">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-4" style={{ color: "rgba(255,255,255,0.5)" }}>
            {isES ? "MÉTRICAS" : "METRICS"}
          </p>
          <h2 className="section-title text-white">
            {isES ? "Infraestructura real. Uso real." : "Real infrastructure. Real usage."}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-10">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest mb-6" style={{ color: "rgba(255,255,255,0.4)" }}>
              {isES ? "Uso" : "Usage"}
            </p>
            <div className="grid grid-cols-3 gap-4">
              {usageMetrics.map((m, i) => (
                <div key={i} className="text-center">
                  <p className="text-3xl font-black font-mono tabular-nums text-[var(--cm-mint)]">{m.value}</p>
                  <p className="text-xs mt-1" style={{ color: "rgba(255,255,255,0.5)" }}>{m.label}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <p className="text-xs font-semibold uppercase tracking-widest mb-6" style={{ color: "rgba(255,255,255,0.4)" }}>
              {isES ? "Cobertura" : "Coverage"}
            </p>
            <div className="grid grid-cols-3 gap-4">
              {coverageMetrics.map((m, i) => (
                <div key={i} className="text-center">
                  <p className="text-3xl font-black font-mono tabular-nums text-white">{m.value}</p>
                  <p className="text-xs mt-1" style={{ color: "rgba(255,255,255,0.5)" }}>{m.label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
          {platforms.map((p) => (
            <span
              key={p}
              className="text-xs font-semibold font-mono px-3 py-1.5 rounded-full"
              style={{
                background: "rgba(255,255,255,0.07)",
                border: "1px solid rgba(255,255,255,0.15)",
                color: "rgba(255,255,255,0.7)",
              }}
            >
              {p}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
