"use client";
import { useEffect, useState } from "react";
import { useLang } from "@/lib/LanguageContext";

import { API_URL } from "@/lib/api";

interface DataStats {
  kpis?: { total_snapshots?: number; active_stores?: number; total_runs?: number; stores_24h?: number };
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
  const snapshots = k.total_snapshots || 0;
  const active = k.active_stores || 0;
  const runs = k.total_runs || 0;
  const live24h = k.stores_24h || 0;
  const countries = stats.by_country?.length || 0;
  
  let freshness = "";
  if (stats.generated_at) {
    const mins = Math.round((Date.now() - new Date(stats.generated_at).getTime()) / 60000);
    freshness = mins < 60 ? `${mins}min` : `${Math.round(mins/60)}h`;
  }

  return (
    <section id="data" className="relative bg-[var(--wise-ink)] py-24">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[var(--wise-mute)] font-medium uppercase tracking-[0.15em] mb-8">
          {isES ? "Cobertura y datos" : "Coverage and data"}
        </p>
        <h2 className="text-[clamp(28px,5vw,48px)] leading-[1.1] font-black text-[var(--wise-green)] mb-4 tracking-tight">
          {isES ? "Tu base de datos de precios reales." : "Your real-price database."}
        </h2>
        <p className="text-base text-[var(--wise-body)] max-w-lg mx-auto mb-12 leading-relaxed">
          {isES
            ? "Nuestro collector corre cada 8 horas contra 30 retailers y extrae precios reales de góndola."
            : "Our collector runs every 8 hours against 30 retailers and extracts real shelf prices."}
        </p>

        {freshness && (
          <div className="inline-flex items-center gap-2 mb-6 bg-[var(--wise-green-pale)] rounded-full px-4 py-1.5">
            <span className="w-2 h-2 rounded-full bg-[#2ead4b] animate-pulse" />
            <span className="text-xs text-[var(--wise-ink)] font-medium">
              {isES ? "Datos actualizados hace" : "Data refreshed"} {freshness}
            </span>
          </div>
        )}

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-12">
          {[
            { label: isES ? "Precios" : "Prices", val: snapshots ? snapshots.toLocaleString() : "9,000+", sub: isES ? "indexados" : "indexed" },
            { label: isES ? "Retailers" : "Retailers", val: active ? `${active}` : "27", sub: isES ? "activos" : "active" },
            { label: isES ? "Países" : "Countries", val: countries ? `${countries}` : "7", sub: isES ? "con cobertura" : "covered" },
            { label: isES ? "Ciclos" : "Cycles", val: runs ? `${runs}` : "4", sub: isES ? "cada 8h" : "every 8h" },
          ].map((kpi) => (
            <div key={kpi.label} className="bg-[var(--wise-green-pale)] rounded-3xl p-3 text-left overflow-hidden">
              <p className="text-[10px] text-[var(--wise-body)] uppercase tracking-widest mb-1 truncate">{kpi.label}</p>
              <p className="text-lg sm:text-xl font-black text-[var(--wise-ink)] truncate">{kpi.val}</p>
              <p className="text-[10px] text-[var(--wise-mute)] truncate">{kpi.sub}</p>
            </div>
          ))}
        </div>

        {stats.by_country && stats.by_country.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-12">
            {stats.by_country.slice(0, 8).map((c) => (
              <div key={c.country} className="flex items-center justify-between bg-white/5 rounded-3xl px-3 py-2.5 truncate">
                <span className="text-xs text-[var(--wise-body)] truncate">{c.country}</span>
                <span className="text-sm font-bold text-[var(--wise-green)] ml-2 shrink-0">{c.count?.toLocaleString()} <span className="text-[10px] font-normal text-[var(--wise-mute)]">precios</span></span>
              </div>
            ))}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
          {[
            { icon: "01", t_es: "Exporta precios en JSON/CSV con el plan Pro.", t_en: "Export prices in JSON/CSV with Pro." },
            { icon: "02", t_es: "Construye canasta básica, inflación retail, PPP.", t_en: "Build basic basket, retail inflation, PPP." },
            { icon: "03", t_es: "Conecta a BigQuery, Snowflake o notebooks.", t_en: "Connect to BigQuery, Snowflake, notebooks." },
          ].map((f, i) => (
            <div key={i} className="bg-[var(--wise-green-pale)] rounded-3xl p-4 text-left overflow-hidden">
              <p className="text-lg font-black text-[var(--wise-ink)] mb-1">{f.icon}</p>
              <p className="text-xs sm:text-sm text-[var(--wise-body)] leading-relaxed break-words">{isES ? f.t_es : f.t_en}</p>
            </div>
          ))}
        </div>

        <div className="mt-12">
          <a href={`${API_URL}/dashboard`}
             target="_blank" rel="noopener"
             className="inline-flex items-center gap-2 rounded-3xl bg-[var(--wise-green)] text-[var(--wise-ink)] text-base font-semibold px-8 py-3.5 hover:bg-[var(--wise-green-hover)] transition-colors">
            {isES ? "Ver dashboard en vivo" : "View live dashboard"}
            <span className="opacity-60">→</span>
          </a>
        </div>
      </div>
    </section>
  );
}
