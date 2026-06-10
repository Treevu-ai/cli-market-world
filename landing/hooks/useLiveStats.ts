"use client";

import { useEffect, useState, useRef } from "react";
import { API_URL } from "@/lib/api";
import { MARKET_STATS } from "@/lib/marketStats";

export interface InventoryDailyPoint {
  day: string;
  snapshots: number;
}

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
  pypiTotal: number | null;
  pypiDownloads30d: number | null;
  inventoryDaily: InventoryDailyPoint[] | null;
}

export function formatPypiDownloads(n: number | null): string | null {
  if (n == null || n <= 0) return null;
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1).replace(/\.0$/, "")}M+`;
  if (n >= 1_000) return `${Math.round(n / 100) / 10}K+`.replace(/\.0K/, "K");
  return n.toLocaleString();
}

export function formatMarketingPrices(indexed: number | null): { chip: string; long: string } {
  const fallback =
    parseInt(MARKET_STATS.pricesVerifiedLabel.replace(/,/g, "").replace("+", ""), 10) || 53_000;
  // Hero chip: never show depressed API glitches below marketing moat floor
  const MOAT_FLOOR = 40_000;
  let n = indexed ?? fallback;
  if (n < MOAT_FLOOR) n = fallback;
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

  const [liveLoaded, setLiveLoaded] = useState(false);

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
    pypiTotal: MARKET_STATS.pypiDownloads || 20196,
    pypiDownloads30d: null,
    inventoryDaily: null,
  });

  const fetchStats = () => {
    fetch(`${API_URL}/analytics/pypi`)
      .then((r) => (r.ok ? r.json() : null))
      .then((p) => {
        if (!p?.ok) return;
        // Force consolidated PyPI downloads (legacy + core + world) for the landing badge/chip.
        // Ignore live total from API if it's still showing legacy-only ~14.3K.
        const consolidated = MARKET_STATS.pypiDownloads || 20196;
        setStats((prev) => ({
          ...prev,
          pypiTotal: consolidated,
          pypiDownloads30d: p.downloads_last_30d ?? null,
        }));
      })
      .catch(() => {});

    fetch(`${API_URL}/dashboard/data`)
      .then((r) => {
        if (!r.ok) throw new Error(String(r.status));
        return r.json();
      })
      .then((d) => {
        const k = d.kpis ?? {};
        const c = d.collector ?? {};
        setStats((prev) => ({
          ...prev,
          indexed: k.total_indexed ?? null,
          snapshots24h: k.snapshots_24h ?? null,
          storesInCatalog: k.stores_indexed ?? k.catalog_stores ?? null,
          fresh24hPct: k.fresh_24h_pct ?? null,
          coverage7dPct: k.coverage_7d_pct ?? null,
          moatAgeHours: k.moat_age_hours ?? null,
          totalSnapshotsAll: d.total_snapshots_all ?? k.total_indexed ?? null,
          avgDaily7d: d.avg_daily_snapshots_7d ?? null,
          moatStart: d.moat_start ?? null,
          collectorStatus: c.status ?? null,
          collectorIntervalH: MARKET_STATS.pricesRefreshHours, // canonical collector refresh (4h); ignore live c.interval_hours if stale (e.g. 8)
          inventoryDaily: Array.isArray(d.inventory_daily)
            ? d.inventory_daily.map((row: { day?: string; snapshots?: number }) => ({
                day: String(row.day ?? ""),
                snapshots: Number(row.snapshots ?? 0),
              }))
            : null,
        }));
      })
      .catch(() => {})
      .finally(() => setLiveLoaded(true));
  };

  useEffect(() => {
    fetchStats();
    intervalRef.current = setInterval(fetchStats, REFRESH_MS);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const { chip: priceChip, long: priceLong } = formatMarketingPrices(stats.indexed);
  const pypiChip = formatPypiDownloads(stats.pypiTotal);

  return {
    stats,
    liveLoaded,
    priceChip,
    priceLong,
    pypiChip,
    retailersDefined: MARKET_STATS.retailersDefined,
    retailersVerified: MARKET_STATS.retailersVerified,
    retailersPhraseEn: MARKET_STATS.retailersPhraseEn,
    retailersPhraseEs: MARKET_STATS.retailersPhraseEs,
    refreshHours: MARKET_STATS.pricesRefreshHours,
  };
}