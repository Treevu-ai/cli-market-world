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

/** Consistent marketing price labels (chip + long) from the same rounded value. */
export function formatMarketingPrices(indexed: number | null): { chip: string; long: string } {
  const fallback = 43_000;
  const n = indexed ?? fallback;
  const k = Math.round(n / 1000);
  return {
    chip: `${k}K+`,
    long: `${k.toLocaleString()},000+`,
  };
}

export function refreshLabel(isES: boolean): string {
  return isES
    ? `cada ${MARKET_STATS.pricesRefreshHours}h`
    : `every ${MARKET_STATS.pricesRefreshHours}h`;
}

/** Auto-refresh interval: re-fetch live KPIs every 5 minutes. */
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
    collectorIntervalH: null,
  });

  const fetchStats = () => {
    fetch(`${API_URL}/dashboard/data`)
      .then((r) => r.json())
      .then((d) => {
        const k = d.kpis || {};
        const c = d.collector || {};
        setStats({
          indexed: k.total_indexed ?? k.total_snapshots ?? null,
          snapshots24h: k.snapshots_24h ?? null,
          storesInCatalog: k.stores_indexed ?? k.active_stores ?? null,
          fresh24hPct: k.fresh_24h_pct ?? null,
          coverage7dPct: k.coverage_7d_pct ?? null,
          moatAgeHours: k.moat_age_hours ?? null,
          totalSnapshotsAll: d.total_snapshots_all ?? null,
          avgDaily7d: d.avg_daily_snapshots_7d ?? null,
          moatStart: d.moat_start ?? null,
          collectorStatus: c.status ?? null,
          collectorIntervalH: c.interval_hours ?? MARKET_STATS.pricesRefreshHours,
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
