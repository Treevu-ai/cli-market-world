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
  const { priceChip, stats } = useLiveStats();

  const freshness =
    stats.fresh24hPct != null
      ? `${stats.fresh24hPct.toFixed(0)}%`
      : `${MARKET_STATS.pricesRefreshHours}h`;

  const metrics: Metric[] = [
    {
      value: priceChip,
      labelEs: "PRECIOS VERIFICADOS",
      labelEn: "VERIFIED SHELF PRICES",
      accent: "data",
    },
    {
      value: String(MARKET_STATS.retailersVerified),
      labelEs: "RETAILERS ACTIVOS",
      labelEn: "ACTIVE RETAILERS",
      accent: "data",
    },
    {
      value: String(MARKET_STATS.countries),
      labelEs: "PAÍSES",
      labelEn: "COUNTRIES",
    },
    {
      value: freshness,
      labelEs: stats.fresh24hPct != null ? "FRESCURA 24H" : "REFRESH",
      labelEn: stats.fresh24hPct != null ? "24H FRESHNESS" : "REFRESH",
      accent: "signal",
    },
  ];

  return (
    <div
      className="hero-metrics grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-6 w-full max-w-[900px] mx-auto"
      aria-label={isES ? "Métricas de cobertura verificada" : "Verified coverage metrics"}
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
