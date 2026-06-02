"use client";

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

/** Consistent marketing price labels from MARKET_STATS. */
export function formatMarketingPrices(_indexed: number | null): { chip: string; long: string } {
  const label = MARKET_STATS.pricesVerifiedLabel.replace(",", "").replace("+", "");
  const n = parseInt(label, 10) || 45_000;
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

/** Static stats — no live dashboard fetch (dashboard lives in private backend). */
export function useLiveStats() {
  const stats: LiveStats = {
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
  };

  const { chip: priceChip, long: priceLong } = formatMarketingPrices(null);

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
