"use client";
import { useLang } from "@/lib/LanguageContext";

export default function DataSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="data" className="relative bg-[#e8ebe6] py-20 border-t border-[#c5edab]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[#868685] font-mono uppercase tracking-[0.15em] mb-8">Data</p>
        <h2 className="text-[24px] font-medium text-[#0e0f0c] mb-3 tracking-tight">
          {isES ? "Tu base de datos de precios de góndola." : "Your shelf-price database."}
        </h2>
        <p className="text-sm text-[#454745] max-w-lg mx-auto mb-12">
          {isES
            ? "Nuestro collector corre cada 8 horas contra los 60 retailers y extrae precios reales. Más de 4,400 precios verificados listos para análisis, dashboards y modelos de pricing."
            : "Our collector runs every 8 hours against all 60 retailers and extracts real shelf prices. Over 4,400 verified prices ready for analysis, dashboards, and pricing models."}
        </p>

        <div className="text-left max-w-[480px] mx-auto space-y-3">
          {[
            { icon: "↓", t_es: "Exporta precios en JSON/CSV con el plan Pro.", t_en: "Export prices in JSON/CSV with the Pro plan." },
            { icon: "📊", t_es: "Construye indicadores de canasta básica, inflación retail o paridad de poder de compra.", t_en: "Build basic-basket indicators, retail inflation, or purchasing power parity." },
            { icon: "🔗", t_es: "Conecta tus datos a BigQuery, Snowflake o notebooks para modelar pricing dinámico.", t_en: "Connect your data to BigQuery, Snowflake, or notebooks for dynamic pricing models." },
          ].map((b, i) => (
            <div key={i} className="flex items-start gap-3 px-4 py-3 bg-[#e2f6d5] border border-[#c5edab] rounded-lg">
              <span className="text-lg shrink-0">{b.icon}</span>
              <span className="text-sm text-[#454745] leading-relaxed">{isES ? b.t_es : b.t_en}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
