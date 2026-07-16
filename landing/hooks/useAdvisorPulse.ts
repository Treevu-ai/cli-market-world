"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

export type PulseKpis = {
  inflation_pct?: number;
  pvi?: number;
  bai?: number;
  pdi?: number;
  rcs?: number;
};

export type PulseAnomaly = {
  subcategory?: string;
  delta_pct?: number;
};

export type PulseMoat = {
  total_indexed?: number;
  snapshots_24h?: number;
  coverage_7d_pct?: number;
};

export type AdvisorPulse = {
  country?: string;
  week?: string;
  headline?: string;
  title?: string;
  generated_at?: string;
  publishable?: boolean;
  executive_highlights?: string[];
  kpis?: PulseKpis;
  moat?: PulseMoat;
  largest_anomaly?: PulseAnomaly;
};

export function useAdvisorPulse(country = "PE", lang = "es") {
  const [data, setData] = useState<AdvisorPulse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);

    const base = API_URL.replace(/\/$/, "");
    const url = `${base}/public/intelligence/data?country=${encodeURIComponent(country)}&lang=${encodeURIComponent(lang)}`;

    fetch(url)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (!cancelled) setData(d);
        if (!cancelled && !d) setError(true);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [country, lang]);

  return { data, loading, error };
}
