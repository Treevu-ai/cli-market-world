import { Terminal, ArrowRight, ShieldCheck, BarChart3 } from "lucide-react";
import { MARKET_STATS } from "@/lib/marketStats";

export default function HeroSection() {
  const stats = [
    {
      value: MARKET_STATS.pricesVerifiedLabel,
      label: "Precios verificados",
      detail: `Actualizados cada ${MARKET_STATS.pricesRefreshHours}h`,
    },
    {
      value: String(MARKET_STATS.retailersVerified),
      label: "Retailers activos",
      detail: `${MARKET_STATS.retailersDefined} catálogo total`,
    },
    {
      value: String(MARKET_STATS.countries),
      label: "Países",
      detail: "Cobertura LATAM",
    },
    {
      value: String(MARKET_STATS.mcpTools),
      label: "Herramientas MCP",
      detail: "API + CLI + agentes",
    },
  ];

  return (
    <section className="relative overflow-hidden pt-14 pb-16 bg-white border border-slate-200 rounded-3xl mb-12 shadow-xs">
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#f1f5f9_1px,transparent_1px),linear-gradient(to_bottom,#f1f5f9_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-30 pointer-events-none" />

      <div className="max-w-5xl mx-auto px-6 sm:px-8 relative z-10">
        <div className="flex flex-wrap items-center gap-2 mb-6">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 border border-emerald-100 text-emerald-800">
            <Terminal className="w-3.5 h-3.5" /> CLI Market for Advisors
          </span>
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 border border-slate-200 text-slate-600">
            Exclusivo para Consultores y Asesores
          </span>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 border border-emerald-100 text-emerald-700">
            <ShieldCheck className="w-3.5 h-3.5" /> Blindaje de Recomendaciones
          </span>
        </div>

        <div className="max-w-3xl mb-10">
          <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 leading-none tracking-tight mb-6">
            Blinda tu consultoría de retail con <span className="text-emerald-700 italic">hechos de góndola irrefutables.</span>
          </h1>
          <p className="text-base sm:text-lg text-slate-600 leading-relaxed mb-8">
            Como asesor de negocios o consultor estratégico de marcas en retail, tus recomendaciones ganan valor por su precisión. Deja de basar tus reportes en suposiciones o auditorías manuales obsoletas. Conéctate a la góndola digital de América Latina en tiempo real, automatiza el análisis competitivo y entrega a tus clientes datos de anaquel imposibles de rebatir.
          </p>

          <div className="flex flex-wrap gap-4">
            <a
              href="#advisor-hub"
              className="px-5 py-3 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-semibold text-sm transition-all duration-200 shadow-sm flex items-center gap-2"
            >
              Probar el Market Radar <ArrowRight className="w-4 h-4" />
            </a>
            <a
              href="#ejemplos-casos"
              className="px-5 py-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm transition-all duration-200 border border-slate-200"
            >
              Ver Casos de Aplicación
            </a>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 border-t border-slate-100 pt-8 mt-12 text-left">
          {stats.map((s) => (
            <div key={s.label} className="p-4 bg-slate-50/50 rounded-xl border border-slate-100">
              <div className="flex items-center gap-1.5 text-slate-800 mb-1">
                <BarChart3 className="w-4 h-4 text-emerald-700" />
                <span className="text-2xl font-black">{s.value}</span>
              </div>
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">{s.label}</span>
              <span className="text-[11px] text-slate-400 mt-0.5 block leading-tight">{s.detail}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
