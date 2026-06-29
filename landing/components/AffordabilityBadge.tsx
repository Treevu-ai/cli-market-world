"use client";

import { useEffect, useState } from "react";

const API_BASE = (
  process.env.NEXT_PUBLIC_API_URL || "https://cli-market-production.up.railway.app"
).replace(/\/$/, "");

type Band = "comfortable" | "moderate" | "strained" | "critical";

type AffordabilityData = {
  affordability_score: number;
  affordability_band: Band;
  headline_es: string;
  headline_en: string;
  components: {
    canasta_min: number | null;
    canasta_currency: string;
  };
};

const BAND_COLOR: Record<Band, string> = {
  comfortable: "#00FF88",
  moderate: "#FFD700",
  strained: "#FF8C00",
  critical: "#FF4444",
};

const BAND_LABEL_ES: Record<Band, string> = {
  comfortable: "Asequible",
  moderate: "Moderado",
  strained: "Ajustado",
  critical: "Crítico",
};

const BAND_LABEL_EN: Record<Band, string> = {
  comfortable: "Comfortable",
  moderate: "Moderate",
  strained: "Strained",
  critical: "Critical",
};

type Props = {
  country?: string;
  lang?: "es" | "en";
  className?: string;
};

export default function AffordabilityBadge({ country = "PE", lang = "es", className = "" }: Props) {
  const [data, setData] = useState<AffordabilityData | null>(null);
  const [loading, setLoading] = useState(true);
  const isES = lang === "es";

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(`${API_BASE}/v1/intel/affordability?country=${encodeURIComponent(country)}&days=30`)
      .then((r) => r.json())
      .then((json) => {
        if (!cancelled) {
          const d = json?.data ?? json;
          setData(d);
        }
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [country]);

  if (loading) {
    return (
      <div className={`inline-flex items-center gap-2 ${className}`}>
        <div className="w-2 h-2 rounded-full bg-[var(--cm-on-surface-variant)]/30 animate-pulse" />
        <span className="text-xs font-mono text-[var(--cm-on-surface-variant)]/50">
          {isES ? "cargando..." : "loading..."}
        </span>
      </div>
    );
  }

  if (!data) return null;

  const band: Band = (data.affordability_band as Band) in BAND_COLOR
    ? (data.affordability_band as Band)
    : "moderate";
  const color = BAND_COLOR[band];
  const label = isES ? BAND_LABEL_ES[band] : BAND_LABEL_EN[band];
  const score = Math.round(data.affordability_score ?? 0);
  const canasta = data.components?.canasta_min;
  const currency = data.components?.canasta_currency ?? "PEN";

  return (
    <div className={`inline-flex flex-col gap-1 ${className}`}>
      <div className="inline-flex items-center gap-2">
        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
        <span className="text-xs font-mono" style={{ color }}>
          {label} · {score}/100
        </span>
      </div>
      {canasta != null && (
        <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]/60">
          {isES ? `canasta mín. ${currency} ${canasta.toFixed(2)}` : `min basket ${currency} ${canasta.toFixed(2)}`}
        </p>
      )}
    </div>
  );
}
