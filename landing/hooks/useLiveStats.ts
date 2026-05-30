"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";
import { MARKET_STATS } from "@/lib/marketStats";

export interface LiveStats {
  indexed: number | null;
  snapshots24h: number | null;
  storesInCatalog: number | null;
}

/** Consistent marketing price labels (chip + long) from the same rounded value. */
export function formatMarketingPrices(indexed: number | null): { chip: string; long: string } {
  const fallback = 43_000;
  const n = indexed ?? fallback;
  const k = Math.max(Math.round(n / 1000), Math.round(fallback / 1000));
  return {
    chip: `${k}K+`,
    long: `${k.toLocaleString()},000+`,
  };
}

export function refreshLabel(isES: boolean): string {
  return isES
    ? `cada ${MARKET_STATS.pricesRefreshHours} horas`
    : `every ${MARKET_STATS.pricesRefreshHours} hours`;
}

export function useLiveStats() {
  const [stats, setStats] = useState<LiveStats>({
    indexed: null,
    snapshots24h: null,
    storesInCatalog: null,
  });

  useEffect(() => {
    fetch(`${API_URL}/dashboard/data`)
      .then((r) => r.json())
      .then((d) => {
        const k = d.kpis || {};
        setStats({
          indexed: k.total_indexed ?? k.total_snapshots ?? null,
          snapshots24h: k.snapshots_24h ?? null,
          storesInCatalog: k.stores_indexed ?? k.active_stores ?? null,
        });
      })
      .catch(() => {});
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
