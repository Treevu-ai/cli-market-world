"use client";
import { useEffect, useState } from "react";
import { useLang } from "@/lib/LanguageContext";

import { API_URL } from "@/lib/api";

interface MetricHelp {
  label?: string;
  description?: string;
  example?: string;
}

interface MoatLayer {
  id?: string;
  title?: string;
  question?: string;
  note?: string;
  metrics?: Record<string, string | number | boolean | null>;
  metric_help?: Record<string, MetricHelp>;
  surfaces?: { cmd?: string; use?: string }[];
}

interface DataStats {
  kpis?: {
    total_indexed?: number;
    total_snapshots?: number;
    snapshots_24h?: number;
    stores_indexed?: number;
    active_stores?: number;
    total_runs?: number;
    moat_age_hours?: number;
    coverage_7d_pct?: number;
  };
  moat_summary?: {
    collector_stale?: boolean;
    total_indexed?: number;
    coverage_7d_pct?: number;
  };
  moat_guide?: {
    headline?: string;
    mental_model?: string[];
    layers?: MoatLayer[];
  };
  generated_at?: string;
  by_country?: { country?: string; count?: number; stores?: number }[];
}

export default function DataSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [stats, setStats] = useState<DataStats>({});

  useEffect(() => {
    fetch(`${API_URL}/dashboard/data`)
      .then((r) => r.json())
      .then(setStats)
      .catch(() => {});
  }, []);

  const k = stats.kpis || {};
  const guide = stats.moat_guide;
  const indexed = k.total_indexed || k.total_snapshots || 0;
  const snap24 = k.snapshots_24h ?? k.total_snapshots ?? 0;
  const storesIndexed = k.stores_indexed || k.active_stores || 0;
  const coverage7d = k.coverage_7d_pct ?? stats.moat_summary?.coverage_7d_pct;
  const stale = stats.moat_summary?.collector_stale;
  const countries = stats.by_country?.length || 0;

  const inventoryLayer = guide?.layers?.find((l) => l.id === "inventory");
  const freshnessLayer = guide?.layers?.find((l) => l.id === "freshness");
  const agentsLayer = guide?.layers?.find((l) => l.id === "agents");

  return (
    <section id="data" className="relative bg-[var(--wise-ink)] py-24">
      <div className="max-w-[800px] mx-auto px-6 text-center">
        <p className="text-xs text-[var(--wise-mute)] font-medium uppercase tracking-[0.15em] mb-8">
          {isES ? "Data moat" : "Data moat"}
        </p>
        <h2 className="text-[clamp(28px,5vw,48px)] leading-[1.1] font-black text-[var(--wise-green)] mb-4 tracking-tight">
          {guide?.headline ||
            (isES ? "Precios reales, estructurados en capas." : "Real prices, structured in layers.")}
        </h2>
        <p className="text-base text-[var(--wise-body)] max-w-lg mx-auto mb-8 leading-relaxed">
          {isES
            ? "Inventario ≠ frescura. El moat acumula precios; el collector los renueva cada pocas horas."
            : "Inventory ≠ freshness. The moat accumulates prices; the collector refreshes them every few hours."}
        </p>

        {guide?.mental_model && guide.mental_model.length > 0 && (
          <ul className="text-left text-sm text-[var(--wise-body)] max-w-xl mx-auto mb-10 space-y-2 list-disc pl-5">
            {guide.mental_model.map((line, i) => (
              <li key={i}>{line}</li>
            ))}
          </ul>
        )}

        {stale && (
          <div className="inline-flex items-center gap-2 mb-6 bg-amber-500/10 rounded-full px-4 py-1.5">
            <span className="text-xs text-amber-200 font-medium">
              {isES
                ? "Moat con datos históricos — refresh 24h pendiente"
                : "Moat has historical data — 24h refresh pending"}
            </span>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-12 text-left">
          <div className="bg-[var(--wise-green-pale)] rounded-3xl p-5">
            <p className="text-[10px] uppercase tracking-widest text-[var(--wise-mute)] mb-1">
              {inventoryLayer?.title || (isES ? "1 · Inventario" : "1 · Inventory")}
            </p>
            <p className="text-xs text-[var(--wise-body)] mb-3">
              {inventoryLayer?.question ||
                (isES ? "¿Cuánto tenemos acumulado?" : "How much do we have stored?")}
            </p>
            <p className="text-3xl font-black text-[var(--wise-ink)]">{indexed ? indexed.toLocaleString() : "—"}</p>
            <p className="text-xs text-[var(--wise-mute)] mt-1">
              {storesIndexed} retailers · {isES ? "precios indexados" : "indexed prices"}
            </p>
            {inventoryLayer?.metric_help?.total_indexed?.description && (
              <p className="text-[10px] text-[var(--wise-mute)] mt-2 leading-relaxed">
                {inventoryLayer.metric_help.total_indexed.description}
              </p>
            )}
          </div>
          <div className="bg-[var(--wise-green-pale)] rounded-3xl p-5">
            <p className="text-[10px] uppercase tracking-widest text-[var(--wise-mute)] mb-1">
              {freshnessLayer?.title || (isES ? "2 · Frescura" : "2 · Freshness")}
            </p>
            <p className="text-xs text-[var(--wise-body)] mb-3">
              {freshnessLayer?.question ||
                (isES ? "¿Puedo confiar hoy?" : "Can I trust today's prices?")}
            </p>
            <p className="text-3xl font-black text-[var(--wise-ink)]">{snap24.toLocaleString()}</p>
            <p className="text-xs text-[var(--wise-mute)] mt-1">
              {isES ? "snapshots últimas 24h" : "snapshots in last 24h"}
              {k.moat_age_hours != null && ` · ${Math.round(k.moat_age_hours)}h ${isES ? "desde último dato" : "since last data"}`}
            </p>
            {freshnessLayer?.metric_help?.snapshots_24h?.description && (
              <p className="text-[10px] text-[var(--wise-mute)] mt-2 leading-relaxed">
                {freshnessLayer.metric_help.snapshots_24h.description}
              </p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-12">
          {[
            {
              label: isES ? "Cobertura 7d" : "7d coverage",
              val: coverage7d != null ? `${coverage7d}%` : "—",
              sub: isES ? "catálogo activo" : "active catalog",
            },
            { label: isES ? "Países" : "Countries", val: countries ? `${countries}` : "—", sub: isES ? "con datos" : "with data" },
            {
              label: isES ? "Para agentes" : "For agents",
              val: agentsLayer?.surfaces?.length ? `${agentsLayer.surfaces.length}` : "4",
              sub: isES ? "superficies CLI/API" : "CLI/API surfaces",
            },
          ].map((kpi) => (
            <div key={kpi.label} className="bg-white/5 rounded-3xl p-3 text-left">
              <p className="text-[10px] text-[var(--wise-body)] uppercase tracking-widest mb-1">{kpi.label}</p>
              <p className="text-lg font-black text-[var(--wise-green)]">{kpi.val}</p>
              <p className="text-[10px] text-[var(--wise-mute)]">{kpi.sub}</p>
            </div>
          ))}
        </div>

        {agentsLayer?.surfaces && agentsLayer.surfaces.length > 0 && (
          <div className="text-left mb-12 bg-white/5 rounded-3xl p-5">
            <p className="text-xs uppercase tracking-widest text-[var(--wise-mute)] mb-3">
              {agentsLayer.title || (isES ? "Para agentes" : "For agents")}
            </p>
            <ul className="space-y-2">
              {agentsLayer.surfaces.map((s: { cmd?: string; use?: string }, i: number) => (
                <li key={i} className="text-sm text-[var(--wise-body)]">
                  <code className="text-[var(--wise-green)] text-xs">{s.cmd}</code>
                  <span className="text-[var(--wise-mute)]"> — {s.use}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {stats.by_country && stats.by_country.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-12">
            {stats.by_country.slice(0, 8).map((c) => (
              <div key={c.country} className="flex items-center justify-between bg-white/5 rounded-3xl px-3 py-2.5 truncate">
                <span className="text-xs text-[var(--wise-body)] truncate">{c.country}</span>
                <span className="text-sm font-bold text-[var(--wise-green)] ml-2 shrink-0">
                  {c.count?.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8">
          <a
            href={`${API_URL}/dashboard`}
            target="_blank"
            rel="noopener"
            className="inline-flex items-center gap-2 rounded-3xl bg-[var(--wise-green)] text-[var(--wise-ink)] text-base font-semibold px-8 py-3.5 hover:bg-[var(--wise-green-hover)] transition-colors"
          >
            {isES ? "Ver dashboard en vivo" : "View live dashboard"}
            <span className="opacity-60">→</span>
          </a>
        </div>
      </div>
    </section>
  );
}
