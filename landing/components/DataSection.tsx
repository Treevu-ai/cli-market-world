"use client";
import { useEffect, useState } from "react";
import { useLang } from "@/lib/LanguageContext";

interface DataStats {
  total_prices?: number;
  total_runs?: number;
  stores_active?: number;
  last_run?: string;
  by_line?: { line_name?: string; count?: number }[];
}

export default function DataSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [stats, setStats] = useState<DataStats>({});

  useEffect(() => {
    fetch("https://cli-market-production.up.railway.app/dashboard/data")
      .then((r) => r.json())
      .then(setStats)
      .catch(() => {});
  }, []);

  const lineNames: Record<string, string> = {
    supermercados: isES ? "Supermercados" : "Supermarkets",
    farmacias: isES ? "Farmacias" : "Pharmacies",
    electro: isES ? "Electro" : "Electronics",
    moda: isES ? "Moda" : "Fashion",
    hogar: isES ? "Hogar" : "Home",
    departamentales: isES ? "Departamentales" : "Department",
  };

  const today = new Date().toLocaleDateString(isES ? "es-PE" : "en-US", { day: "numeric", month: "short" });

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
            ? "Nuestro collector corre cada 8 horas contra los 60 retailers y extrae precios reales de góndola."
            : "Our collector runs every 8 hours against 60 retailers and extracts real shelf prices."}
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-12">
          {[
            { label: isES ? "Precios" : "Prices", val: stats.total_prices?.toLocaleString() || "4,400+", sub: isES ? "verificados" : "verified" },
            { label: isES ? "Ciclos" : "Runs", val: stats.total_runs?.toString() || "3", sub: isES ? "cada 8h" : "every 8h" },
            { label: isES ? "Tiendas" : "Stores", val: stats.stores_active?.toString() || "60", sub: isES ? "activas" : "active" },
            { label: isES ? "Última" : "Last", val: stats.last_run ? new Date(stats.last_run).toLocaleDateString(isES ? "es-PE" : "en-US", { day: "numeric", month: "short" }) : today, sub: isES ? "actualización" : "update" },
          ].map((kpi) => (
            <div key={kpi.label} className="bg-[var(--wise-green-pale)] rounded-3xl p-3 text-left overflow-hidden">
              <p className="text-[10px] text-[var(--wise-body)] uppercase tracking-widest mb-1 truncate">{kpi.label}</p>
              <p className="text-lg sm:text-xl font-black text-[var(--wise-ink)] truncate">{kpi.val}</p>
              <p className="text-[10px] text-[var(--wise-mute)] truncate">{kpi.sub}</p>
            </div>
          ))}
        </div>

        {stats.by_line && stats.by_line.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-12">
            {stats.by_line.map((l) => (
              <div key={l.line_name} className="flex items-center justify-between bg-white/5 rounded-3xl px-3 py-2.5 truncate">
                <span className="text-xs text-[var(--wise-body)] truncate">{lineNames[l.line_name || ""] || l.line_name}</span>
                <span className="text-sm font-bold text-[var(--wise-green)] ml-2 shrink-0">{l.count?.toLocaleString()}</span>
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
              <p className="text-lg font-black text-[var(--wise-green)] mb-1">{f.icon}</p>
              <p className="text-xs sm:text-sm text-[var(--wise-body)] leading-relaxed break-words">{isES ? f.t_es : f.t_en}</p>
            </div>
          ))}
        </div>

        <div className="mt-12">
          <a href="https://cli-market-production.up.railway.app/dashboard"
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
