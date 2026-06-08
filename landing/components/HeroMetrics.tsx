"use client";

import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { useLiveStats } from "@/hooks/useLiveStats";

type Metric = {
  value: string;
  labelEs: string;
  labelEn: string;
  accent?: "data" | "signal";
};

export default function HeroMetrics() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { priceChip, pypiChip } = useLiveStats();

  const metrics: Metric[] = [
    {
      value: priceChip,
      labelEs: "PRECIOS VERIFICADOS",
      labelEn: "VERIFIED SHELF PRICES",
      accent: "data",
    },
    {
      value: String(MARKET_STATS.retailersDefined),
      labelEs: "RETAILERS",
      labelEn: "RETAILERS",
    },
    {
      value: String(MARKET_STATS.countries),
      labelEs: "PAÍSES",
      labelEn: "COUNTRIES",
    },
    {
      value: String(MARKET_STATS.mcpTools),
      labelEs: "HERRAMIENTAS MCP",
      labelEn: "MCP TOOLS",
      accent: "data",
    },
  ];

  if (pypiChip) {
    metrics.push({
      value: pypiChip,
      labelEs: "DESCARGAS PYPI",
      labelEn: "PYPI DOWNLOADS",
      accent: "signal",
    });
  }

  return (
    <div
      className="hero-metrics grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 sm:gap-6 w-full max-w-[1100px] mx-auto"
      aria-label={isES ? "Métricas del moat de datos" : "Data moat metrics"}
    >
      {metrics.map((m) => (
        <div key={m.labelEn} className="hero-metric text-center sm:text-left">
          <p
            className={`hero-metric-value ${
              m.accent === "signal" ? "text-[var(--cm-signal)]" : "text-[var(--cm-ink)]"
            }`}
          >
            {m.value}
          </p>
          <p className="hero-metric-label">{isES ? m.labelEs : m.labelEn}</p>
        </div>
      ))}
    </div>
  );
}