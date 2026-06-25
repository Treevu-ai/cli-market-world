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
      style={{ backgroundColor: "#ffffff" }}
    >
      <div className="landing-container-wide text-center">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-4">
            {isES ? "MÉTRICAS" : "METRICS"}
          </p>
          <h2 className="section-title text-[#0f172a]">
            {isES ? "Infraestructura real. Uso real." : "Real infrastructure. Real usage."}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-10">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-[#94a3b8] mb-6">
              {isES ? "Uso" : "Usage"}
            </p>
            <div className="grid grid-cols-3 gap-4">
              {usageMetrics.map((m, i) => (
                <div key={i} className="text-center">
                  <p className="text-3xl font-black font-mono tabular-nums text-[#ea580c]">{m.value}</p>
                  <p className="text-xs mt-1 text-[#64748b]">{m.label}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-[#94a3b8] mb-6">
              {isES ? "Cobertura" : "Coverage"}
            </p>
            <div className="grid grid-cols-3 gap-4">
              {coverageMetrics.map((m, i) => (
                <div key={i} className="text-center">
                  <p className="text-3xl font-black font-mono tabular-nums text-[#0f172a]">{m.value}</p>
                  <p className="text-xs mt-1 text-[#64748b]">{m.label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
          {platforms.map((p) => (
            <span
              key={p}
              className="text-xs font-semibold font-mono px-3 py-1.5 rounded-full bg-[#f1f5f9] border border-[#e2e8f0] text-[#64748b]"
            >
              {p}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
