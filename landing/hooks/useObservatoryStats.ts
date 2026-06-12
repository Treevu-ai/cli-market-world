"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

export type ObservatoryRank = { name: string; count: number };

export type ObservatoryStats = {
  window_days: number;
  maa: number;
  maa_proxy?: number;
  maa_display?: number;
  telemetry_maturity?: "early" | "established";
  maa_public_threshold?: number;
  calls_success: number;
  countries_active: number;
  retailers_queried: number;
  telemetry_enabled: boolean;
  top_tools: ObservatoryRank[];
  top_retailers: ObservatoryRank[];
  top_countries: ObservatoryRank[];
};

/** Public subset for /stats — no success_rate, no PII (PRD §10). */
export const MAA_PUBLIC_THRESHOLD = 10;

export function useObservatoryStats(days = 30) {
  const [data, setData] = useState<ObservatoryStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(`${API_URL}/analytics/observatory?days=${days}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch(() => {
        if (!cancelled) setData(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [days]);

  const showMaa = !!data?.telemetry_enabled;

  const maaIsProxy =
    !!data && (data.maa ?? 0) < MAA_PUBLIC_THRESHOLD && (data.maa_proxy ?? 0) > 0;

  const maaValue =
    data && (data.maa ?? 0) >= MAA_PUBLIC_THRESHOLD
      ? data.maa
      : (data?.maa_display ?? data?.maa_proxy ?? data?.maa ?? 0);

  const showQueries =
    !!data?.telemetry_enabled && (data.calls_success ?? 0) > 0;

  return { data, loading, showMaa, showQueries, maaValue, maaIsProxy };
}
