"use client";

import { useEffect, useState } from "react";
import { useLang } from "@/lib/LanguageContext";

type DashboardData = {
  generated_at: string;
  kpis: {
    total_indexed: number;
    unique_products: number;
    stores_indexed: number;
    coverage_7d_pct: number;
    stores_fresh_24h: number;
    active_stores: number;
    moat_age_hours: number;
    linkage_pct: number;
    golden_records_distinct: number;
  };
  moat_summary: {
    refresh_hours: number;
    stale_stores: string[];
    marketing_gate_pass: boolean;
  };
};

let cache: DashboardData | null = null;

export default function DataMoatHealth() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [data, setData] = useState<DashboardData | null>(cache);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (cache) return;
    fetch("https://cli-market-api.fly.dev/dashboard/data")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => {
        cache = d;
        setData(d);
      })
      .catch(() => setError(true));
  }, []);

  if (error) {
    return (
      <p className="text-sm text-[var(--cm-on-surface-variant)]/70">
        {isES ? "No se pudo cargar el estado del data moat." : "Could not load data moat health."}
      </p>
    );
  }
  if (!data) {
    return (
      <p className="text-sm text-[var(--cm-on-surface-variant)]/70">
        {isES ? "Cargando estado del data moat…" : "Loading data moat health…"}
      </p>
    );
  }

  const { kpis, moat_summary } = data;
  const tiles = [
    {
      n: kpis.total_indexed.toLocaleString(isES ? "es-PE" : "en-US"),
      l: isES ? "Precios indexados" : "Prices indexed",
    },
    {
      n: `${kpis.coverage_7d_pct}%`,
      l: isES ? "Cobertura 7d (tiendas frescas 24h / activas)" : "7d coverage (fresh 24h / active stores)",
    },
    {
      n: `${kpis.moat_age_hours.toFixed(1)}h`,
      l: isES ? "Antigüedad del último dato" : "Latest data age",
    },
    {
      n: `${kpis.linkage_pct}%`,
      l: isES ? "Golden linkage" : "Golden linkage",
    },
  ];

  return (
    <div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        {tiles.map((t) => (
          <div key={t.l} className="card-cyber p-4 text-center">
            <div className="text-2xl font-mono text-[var(--cm-mint)] tabular-nums">{t.n}</div>
            <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">{t.l}</div>
          </div>
        ))}
      </div>
      <p className="text-xs text-[var(--cm-on-surface-variant)]/70">
        {isES
          ? `Refresh del collector cada ${moat_summary.refresh_hours}h. `
          : `Collector refreshes every ${moat_summary.refresh_hours}h. `}
        {moat_summary.stale_stores.length > 0
          ? isES
            ? `Tiendas con datos viejos ahora mismo: ${moat_summary.stale_stores.join(", ")}.`
            : `Currently stale stores: ${moat_summary.stale_stores.join(", ")}.`
          : isES
            ? "Sin tiendas con datos viejos ahora mismo."
            : "No stale stores right now."}
      </p>
      <p className="text-xs text-[var(--cm-on-surface-variant)]/50 mt-2">
        {isES ? "Mismos indicadores que usan las MCP tools (market_intel_brief, market_stats) — " : "Same indicators the MCP tools use (market_intel_brief, market_stats) — "}
        <a href="/docs#mcp" className="text-[var(--cm-mint)] hover:underline">
          /docs#mcp
        </a>
      </p>
    </div>
  );
}
