"use client";

import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { useLiveStats } from "@/hooks/useLiveStats";
import AnimatedMetricValue from "@/components/AnimatedMetricValue";

type Metric = {
  value: string;
  labelEs: string;
  labelEn: string;
  accent?: "data" | "signal";
};

export default function HeroMetrics() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { priceChip, stats, pypiChip } = useLiveStats();

  const freshness =
    stats.fresh24hPct != null
      ? `${stats.fresh24hPct.toFixed(0)}%`
      : `${MARKET_STATS.pricesRefreshHours}h`;

  const baseMetrics: Metric[] = [
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

  const metrics: Metric[] = pypiChip
    ? [
        ...baseMetrics,
        {
          value: pypiChip,
          labelEs: "DESCARGAS PYPI",
          labelEn: "PYPI DOWNLOADS",
          accent: "data",
        },
      ]
    : baseMetrics;

  const colClass = metrics.length === 5 ? "sm:grid-cols-5" : "sm:grid-cols-4";

  return (
    <div
      className={`hero-metrics grid grid-cols-2 ${colClass} gap-x-4 gap-y-8 sm:gap-x-6 sm:gap-y-0 w-full landing-content-rail justify-items-center`}
      aria-label={isES ? "Métricas de cobertura verificada" : "Verified coverage metrics"}
    >
      {metrics.map((m, i) => (
        <motion.div
          key={m.labelEn}
          className="hero-metric flex flex-col items-center justify-center text-center w-full min-w-0 px-2"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.15 + i * 0.08, ease: [0.22, 1, 0.36, 1] }}
        >
          <p
            className={`hero-metric-value tabular-nums ${
              m.accent === "signal" ? "text-[var(--cm-signal)]" : "text-[var(--cm-ink)]"
            }`}
          >
            <AnimatedMetricValue
              value={m.value}
              pulseSignal={m.accent === "signal" && m.value.includes("%")}
            />
          </p>
          <p className="hero-metric-label max-w-[9.5rem] sm:max-w-[10.5rem] text-balance">
            {isES ? m.labelEs : m.labelEn}
          </p>
        </motion.div>
      ))}
    </div>
  );
}
