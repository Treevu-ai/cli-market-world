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
    fetch("https://cli-market-api.onrender.com/dashboard/data")
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

  return (
    <section id="data" className="relative bg-[#0e0f0c] py-24">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[#868685] font-medium uppercase tracking-[0.15em] mb-8">Data</p>
        <h2 className="text-[clamp(28px,5vw,48px)] leading-[1.1] font-black text-[#9fe870] mb-4 tracking-tight">
          {isES ? "Tu base de datos de precios reales." : "Your real-price database."}
        </h2>
        <p className="text-base text-[#c5edab] max-w-lg mx-auto mb-12 leading-relaxed">
          {isES
            ? "Nuestro collector corre cada 8 horas contra los 60 retailers y extrae precios reales de góndola."
            : "Our collector runs every 8 hours against 60 retailers and extracts real shelf prices."}
        </p>

        {/* Live KPIs */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-12">
          {[
            { label: isES ? "Precios" : "Prices", value: stats.total_prices?.toLocaleString() || "4,400+", sub: isES ? "verificados" : "verified" },
            { label: isES ? "Ciclos" : "Runs", value: stats.total_runs?.toString() || "—", sub: isES ? "cada 8h" : "every 8h" },
            { label: isES ? "Tiendas" : "Stores", value: stats.stores_active?.toString() || "60", sub: isES ? "en 11 países" : "in 11 countries" },
            { label: isES ? "Última" : "Last", value: stats.last_run ? new Date(stats.last_run).toLocaleDateString() : "—", sub: isES ? "actualización" : "update" },
          ].map((kpi) => (
            <div key={kpi.label} className="bg-[#e2f6d5] rounded-3xl p-5 text-left">
              <p className="text-[10px] text-[#454745] uppercase tracking-widest mb-1">{kpi.label}</p>
              <p className="text-2xl font-black text-[#0e0f0c]">{kpi.value}</p>
              <p className="text-[11px] text-[#868685]">{kpi.sub}</p>
            </div>
          ))}
        </div>

        {/* Lines breakdown */}
        {stats.by_line && stats.by_line.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-12">
            {stats.by_line.map((l) => (
              <div key={l.line_name} className="flex items-center justify-between bg-white/5 rounded-3xl px-4 py-3">
                <span className="text-sm text-[#c5edab]">{lineNames[l.line_name || ""] || l.line_name}</span>
                <span className="text-sm font-bold text-white">{l.count?.toLocaleString()}</span>
              </div>
            ))}
          </div>
        )}

        {/* Features */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
          {[
            { icon: "01", t_es: "Exporta precios en JSON/CSV con el plan Pro.", t_en: "Export prices in JSON/CSV with Pro." },
            { icon: "02", t_es: "Construye canasta básica, inflación retail, PPP.", t_en: "Build basic basket, retail inflation, PPP." },
            { icon: "03", t_es: "Conecta a BigQuery, Snowflake o notebooks.", t_en: "Connect to BigQuery, Snowflake, notebooks." },
          ].map((f, i) => (
            <div key={i} className="bg-[#e2f6d5] rounded-3xl p-5">
              <p className="text-lg font-black text-[#9fe870] mb-2">{f.icon}</p>
              <p className="text-sm text-[#454745] leading-relaxed">{isES ? f.t_es : f.t_en}</p>
            </div>
          ))}
        </div>

        <div className="mt-12">
          <a href="https://cli-market-api.onrender.com/dashboard"
             target="_blank" rel="noopener"
             className="inline-flex items-center gap-2 rounded-3xl bg-[#9fe870] text-[#0e0f0c] text-base font-semibold px-8 py-3.5 hover:bg-[#cdffad] transition-colors">
            {isES ? "Ver dashboard en vivo" : "View live dashboard"}
            <span className="opacity-60">→</span>
          </a>
        </div>
      </div>
    </section>
  );
}
