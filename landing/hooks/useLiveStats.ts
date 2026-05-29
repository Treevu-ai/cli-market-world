"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

export interface LiveStats {
  indexed: number | null;
  snapshots24h: number | null;
  stores: number | null;
}

function formatCompact(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
  if (n >= 10_000) return `${Math.round(n / 1_000)}K`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1).replace(/\.0$/, "")}K`;
  return n.toLocaleString();
}

export function useLiveStats(): { stats: LiveStats; priceChip: string; priceLong: string } {
  const [stats, setStats] = useState<LiveStats>({ indexed: null, snapshots24h: null, stores: null });

  useEffect(() => {
    fetch(`${API_URL}/dashboard/data`)
      .then((r) => r.json())
      .then((d) => {
        const k = d.kpis || {};
        setStats({
          indexed: k.total_indexed ?? k.total_snapshots ?? null,
          snapshots24h: k.snapshots_24h ?? null,
          stores: k.stores_indexed ?? k.active_stores ?? null,
        });
      })
      .catch(() => {});
  }, []);

  const indexed = stats.indexed ?? 39_000;
  return {
    stats,
    priceChip: formatCompact(indexed),
    priceLong: indexed.toLocaleString(),
  };
}
