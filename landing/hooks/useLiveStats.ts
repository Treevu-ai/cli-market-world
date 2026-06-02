"use client";

import { useEffect, useState, useRef } from "react";
import { API_URL } from "@/lib/api";
import { MARKET_STATS } from "@/lib/marketStats";

export interface LiveStats {
  indexed: number | null;
  snapshots24h: number | null;
  storesInCatalog: number | null;
  fresh24hPct: number | null;
  coverage7dPct: number | null;
  moatAgeHours: number | null;
  totalSnapshotsAll: number | null;
  avgDaily7d: number | null;
  moatStart: string | null;
  collectorStatus: string | null;
  collectorIntervalH: number | null;
}

export function formatMarketingPrices(indexed: number | null): { chip: string; long: string } {
  const fallback = parseInt(MARKET_STATS.pricesVerifiedLabel.replace(/,/g, "").replace("+", ""), 10) || 45_000;
  const n = indexed ?? fallback;
  const k = Math.round(n / 1000);
  return {
    chip: `${k}K+`,
    long: n >= 1000 ? `${(n / 1000).toFixed(1).replace(/\.0$/, "")}K` : n.toLocaleString(),
  };
}

export function refreshLabel(isES: boolean): string {
  return isES
    ? `cada ${MARKET_STATS.pricesRefreshHours}h`
    : `every ${MARKET_STATS.pricesRefreshHours}h`;
}

const REFRESH_MS = 5 * 60 * 1000;

export function useLiveStats() {
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const [stats, setStats] = useState<LiveStats>({
    indexed: null,
    snapshots24h: null,
    storesInCatalog: null,
    fresh24hPct: null,
    coverage7dPct: null,
    moatAgeHours: null,
    totalSnapshotsAll: null,
    avgDaily7d: null,
    moatStart: null,
    collectorStatus: null,
    collectorIntervalH: MARKET_STATS.pricesRefreshHours,
  });

  const fetchStats = () => {
    fetch(`${API_URL}/dashboard/data`)
      .then((r) => r.json())
      .then((d) => {
        setStats({
          indexed: (d.kpis || {}).total_indexed ?? null,
          snapshots24h: (d.kpis || {}).snapshots_24h ?? null,
          storesInCatalog: (d.kpis || {}).stores_indexed ?? null,
          fresh24hPct: (d.kpis || {}).fresh_24h_pct ?? null,
          coverage7dPct: (d.kpis || {}).coverage_7d_pct ?? null,
          moatAgeHours: (d.kpis || {}).moat_age_hours ?? null,
          totalSnapshotsAll: (d.kpis || {}).total_indexed ?? null,
          avgDaily7d: (d.kpis || {}).avg_daily_7d ?? null,
          moatStart: d.generated_at ?? null,
          collectorStatus: (d.collector || {}).status ?? null,
          collectorIntervalH: MARKET_STATS.pricesRefreshHours,
        });
      })
      .catch(() => {});
  };

  useEffect(() => {
    fetchStats();
    intervalRef.current = setInterval(fetchStats, REFRESH_MS);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const { chip: priceChip, long: priceLong } = formatMarketingPrices(stats.indexed);

  return {
    stats,
    priceChip,
    priceLong,
    retailersDefined: MARKET_STATS.retailersDefined,
    retailersVerified: MARKET_STATS.retailersVerified,
    retailersPhraseEn: MARKET_STATS.retailersPhraseEn,
    retailersPhraseEs: MARKET_STATS.retailersPhraseEs,
    refreshHours: MARKET_STATS.pricesRefreshHours,
  };
}
