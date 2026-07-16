"use client";

import { useState, useEffect } from "react";
import {
  TrendingUp,
  TrendingDown,
  Globe,
  BarChart3,
  Zap,
  Calculator,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Percent,
  FileSpreadsheet,
  Copy,
} from "lucide-react";
import { useAdvisorPulse } from "@/hooks/useAdvisorPulse";

const COUNTRIES = [
  { key: "PE", label: "Perú (PE)" },
  { key: "MX", label: "México (MX)" },
  { key: "CO", label: "Colombia (CO)" },
  { key: "CL", label: "Chile (CL)" },
  { key: "AR", label: "Argentina (AR)" },
  { key: "BR", label: "Brasil (BR)" },
];

function fmtPct(value?: number | null, signed = true) {
  if (value === undefined || value === null || Number.isNaN(value)) return "—";
  const n = Number(value);
  if (signed) return `${n >= 0 ? "+" : ""}${n.toFixed(1)}%`;
  return `${n.toFixed(1)}%`;
}

export default function AdvisorHubSection() {
  const [selectedCountry, setSelectedCountry] = useState("PE");
  const { data, loading, error } = useAdvisorPulse(selectedCountry, "es");

  const [hourlyRate, setHourlyRate] = useState(80);
  const [clientCount, setClientCount] = useState(4);
  const [includeIntelReports, setIncludeIntelReports] = useState(true);
  const [currentRevenue, setCurrentRevenue] = useState(0);
  const [intelRevenue, setIntelRevenue] = useState(0);
  const [revenueMultiplier, setRevenueMultiplier] = useState(1);
  const [isCopied, setIsCopied] = useState(false);

  useEffect(() => {
    const baseline = hourlyRate * 10 * clientCount;
    setCurrentRevenue(baseline);

    if (includeIntelReports) {
      const premiumRetainer = hourlyRate * 2.2 * 12 * clientCount;
      setIntelRevenue(premiumRetainer);
      setRevenueMultiplier(Number((premiumRetainer / (baseline || 1)).toFixed(1)));
    } else {
      setIntelRevenue(baseline);
      setRevenueMultiplier(1.0);
    }
  }, [hourlyRate, clientCount, includeIntelReports]);

  const kpis = data?.kpis || {};
  const anomaly = data?.largest_anomaly || {};
  const moat = data?.moat || {};

  const advisorTactic = anomaly?.subcategory
    ? `La mayor anomalía está en ${anomaly.subcategory} (${fmtPct(anomaly.delta_pct)}). Recomienda a tu cliente revisar su posicionamiento de precio y canal en esa categoría antes de la próxima negociación.`
    : `Monitorea la inflación de estantería (${fmtPct(kpis.inflation_pct)}) y el PVI dispersión (${fmtPct(kpis.pvi, false)}) para detectar ventanas de renegociación con retailers.`;

  const handleCopyTactic = () => {
    navigator.clipboard.writeText(`[TÁCTICA DE ASESOR CLI MARKET] - País: ${selectedCountry}. ${advisorTactic}`);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <section id="advisor-hub" className="mb-16 scroll-mt-20">
      <div className="bg-gradient-to-r from-slate-900 via-emerald-950 to-slate-900 rounded-3xl p-8 sm:p-12 text-white mb-10 shadow-lg border border-slate-800 relative overflow-hidden">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:3rem_3rem] opacity-20 pointer-events-none" />
        <div className="absolute top-0 right-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-3xl relative z-10">
          <div className="flex flex-wrap items-center gap-2 mb-6">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-emerald-500/20 border border-emerald-500/35 text-emerald-300 uppercase tracking-widest">
              RADAR DE GÓNDOLA · DATOS EN VIVO
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 border border-emerald-500/30 text-emerald-300">
              <Zap className="w-3.5 h-3.5" /> Conectado a cli-market-api
            </span>
          </div>

          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight mb-4 leading-tight">
            CLI Market <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 to-emerald-400">for Advisors</span>
          </h2>

          <p className="text-base sm:text-lg text-slate-300 font-light mb-8 leading-relaxed">
            Conéctate a los datos verificados de <strong className="text-white font-medium">cli-market.dev/advisor</strong> para construir recomendaciones con respaldo empírico. Detecta inflación de estantería, dispersión de precios y anomalías antes de la competencia.
          </p>

          <div className="grid sm:grid-cols-3 gap-6 pt-6 border-t border-slate-800/80">
            <div>
              <p className="text-xs text-slate-400 uppercase font-mono tracking-wider">Ahorro y Eficiencia</p>
              <p className="text-sm font-semibold text-emerald-300 mt-1">Automatización de auditorías</p>
            </div>
            <div>
              <p className="text-xs text-slate-400 uppercase font-mono tracking-wider">Control Comercial</p>
              <p className="text-sm font-semibold text-emerald-300 mt-1">Señales antes del IPC</p>
            </div>
            <div>
              <p className="text-xs text-slate-400 uppercase font-mono tracking-wider">Ganancias Potenciales</p>
              <p className="text-sm font-semibold text-emerald-300 mt-1">Retainers de datos</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-12 gap-8 items-start">
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-emerald-50 text-emerald-700 rounded-lg">
                <Globe className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-base sm:text-lg">
                  Console: cli-market.dev/advisor
                </h3>
                <p className="text-xs text-slate-500">
                  Métricas de control en tiempo real para mitigación de riesgos, ahorro operativo y ganancias potenciales.
                </p>
              </div>
            </div>
            <span className="inline-flex items-center gap-1 text-[11px] font-mono text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> LIVE
            </span>
          </div>

          <div className="mb-6">
            <label className="block text-xs font-bold text-slate-600 mb-1">País seleccionado</label>
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="w-full text-xs sm:text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 outline-none focus:ring-1 focus:ring-emerald-700 focus:border-emerald-700 transition-all font-semibold text-slate-700 cursor-pointer"
            >
              {COUNTRIES.map((c) => (
                <option key={c.key} value={c.key}>
                  {c.label}
                </option>
              ))}
            </select>
          </div>

          {loading ? (
            <div className="p-8 text-center text-sm text-slate-500">Cargando señales de góndola…</div>
          ) : error ? (
            <div className="p-6 bg-rose-50 border border-rose-100 rounded-xl text-sm text-rose-700">
              No se pudieron cargar los datos en vivo. Verifica tu conexión o recarga la página.
            </div>
          ) : (
            <>
              {data?.headline && (
                <div className="mb-6 bg-slate-50 border border-slate-200 rounded-xl p-4">
                  <p className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider mb-1">Headline</p>
                  <p className="text-sm text-slate-700 leading-relaxed">{data.headline}</p>
                </div>
              )}

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3.5 text-center transition-all hover:bg-slate-100/50">
                  <span className="text-[10px] font-mono text-slate-400 font-bold uppercase block">Inflación retail</span>
                  <span className="text-sm sm:text-base font-extrabold text-slate-800 mt-1 block flex items-center justify-center gap-1">
                    {(kpis.inflation_pct ?? 0) >= 0 ? (
                      <TrendingUp className="w-3.5 h-3.5 text-rose-500 shrink-0" />
                    ) : (
                      <TrendingDown className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                    )}
                    {fmtPct(kpis.inflation_pct)}
                  </span>
                </div>

                <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3.5 text-center transition-all hover:bg-slate-100/50">
                  <span className="text-[10px] font-mono text-slate-400 font-bold uppercase block">PVI · dispersión</span>
                  <span className="text-sm sm:text-base font-extrabold text-emerald-700 mt-1 block">
                    {fmtPct(kpis.pvi, false)}
                  </span>
                </div>

                <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3.5 text-center transition-all hover:bg-slate-100/50">
                  <span className="text-[10px] font-mono text-slate-400 font-bold uppercase block">BAI · canasta</span>
                  <span className="text-sm sm:text-base font-extrabold text-slate-800 mt-1 block">
                    {kpis.bai ?? "—"}
                  </span>
                </div>

                <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3.5 text-center transition-all hover:bg-slate-100/50">
                  <span className="text-[10px] font-mono text-slate-400 font-bold uppercase block">RCS · fairness</span>
                  <span className="text-sm sm:text-base font-extrabold text-slate-800 mt-1 block">
                    {kpis.rcs ?? "—"}
                  </span>
                </div>
              </div>

              <div className="space-y-4 mb-6">
                {anomaly?.subcategory && (
                  <div className="bg-emerald-50/50 border border-emerald-100 rounded-xl p-4">
                    <div className="flex items-center gap-1.5 mb-2">
                      <BarChart3 className="w-4 h-4 text-emerald-700" />
                      <span className="text-xs font-mono font-bold text-emerald-900 uppercase tracking-wider">
                        Mayor anomalía detectada
                      </span>
                    </div>
                    <p className="text-sm font-extrabold text-emerald-950">
                      {anomaly.subcategory} {fmtPct(anomaly.delta_pct)}
                    </p>
                    <p className="text-xs text-slate-600 mt-1">
                      Variación vs mediana de la categoría. Oportunidad de negociación con retailers.
                    </p>
                  </div>
                )}

                {data?.executive_highlights && data.executive_highlights.length > 0 && (
                  <div className="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
                    <div className="flex items-center gap-1.5 mb-2 text-slate-700">
                      <AlertCircle className="w-4 h-4 text-emerald-700" />
                      <span className="text-xs font-semibold uppercase tracking-wider">Highlights ejecutivos</span>
                    </div>
                    <ul className="text-xs sm:text-sm text-slate-600 leading-relaxed font-medium space-y-2">
                      {data.executive_highlights.map((h, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-emerald-700">•</span>
                          <span>{h}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {moat.total_indexed !== undefined && (
                  <div className="grid grid-cols-3 gap-3 text-center">
                    <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3">
                      <span className="text-[10px] font-mono text-slate-400 font-bold uppercase block">Indexados</span>
                      <span className="text-sm font-extrabold text-slate-800">
                        {Number(moat.total_indexed).toLocaleString()}
                      </span>
                    </div>
                    <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3">
                      <span className="text-[10px] font-mono text-slate-400 font-bold uppercase block">Refresh 24h</span>
                      <span className="text-sm font-extrabold text-slate-800">
                        {Number(moat.snapshots_24h).toLocaleString()}
                      </span>
                    </div>
                    <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3">
                      <span className="text-[10px] font-mono text-slate-400 font-bold uppercase block">Cobertura 7d</span>
                      <span className="text-sm font-extrabold text-slate-800">
                        {fmtPct(moat.coverage_7d_pct, false)}
                      </span>
                    </div>
                  </div>
                )}
              </div>

              <div className="bg-gradient-to-br from-emerald-900 to-slate-900 rounded-xl p-5 sm:p-6 text-white relative overflow-hidden shadow-md">
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full blur-xl pointer-events-none" />
                <div className="flex items-center gap-2 mb-3">
                  <Zap className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest font-mono">
                    TÁCTICA RECOMENDADA
                  </span>
                </div>

                <h4 className="text-sm sm:text-base font-bold mb-2">Táctica comercial para control de riesgos y mayores ingresos:</h4>
                <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-light italic mb-4">
                  &ldquo;{advisorTactic}&rdquo;
                </p>

                <div className="flex items-center justify-between pt-3 border-t border-white/10">
                  <span className="text-[10px] text-slate-400">Perfecta para tu propuesta comercial</span>
                  <button
                    type="button"
                    onClick={handleCopyTactic}
                    className="flex items-center gap-1.5 text-[11px] bg-slate-800 hover:bg-slate-700 text-white px-3 py-1.5 rounded-lg border border-slate-700 transition-all cursor-pointer"
                  >
                    {isCopied ? (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-emerald-400 font-bold">¡Copiado!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span>Copiar Táctica</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </>
          )}
        </div>

        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs">
          <div className="flex items-center gap-2 mb-6 pb-4 border-b border-slate-100">
            <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
              <Calculator className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-base sm:text-lg">
                Calculadora de Retorno Esperado
              </h3>
              <p className="text-xs text-slate-500">
                Mide tus ingresos incrementales, tu ahorro de tiempo y tu control sobre decisiones.
              </p>
            </div>
          </div>

          <div className="space-y-5">
            <div>
              <div className="flex justify-between text-xs font-bold text-slate-600 mb-1">
                <span>Tu Tarifa por Hora Actual</span>
                <span className="text-emerald-700 font-mono">USD {hourlyRate} / h</span>
              </div>
              <input
                type="range"
                min="30"
                max="250"
                step="5"
                value={hourlyRate}
                onChange={(e) => setHourlyRate(Number(e.target.value))}
                className="w-full accent-emerald-700 h-1.5 bg-slate-100 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 font-medium mt-1">
                <span>USD 30/h</span>
                <span>USD 140/h</span>
                <span>USD 250/h</span>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold text-slate-600 mb-1">
                <span>Clientes Activos al Mes</span>
                <span className="text-emerald-700 font-mono">{clientCount} Clientes</span>
              </div>
              <input
                type="range"
                min="1"
                max="15"
                step="1"
                value={clientCount}
                onChange={(e) => setClientCount(Number(e.target.value))}
                className="w-full accent-emerald-700 h-1.5 bg-slate-100 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 font-medium mt-1">
                <span>1 cliente</span>
                <span>8 clientes</span>
                <span>15 clientes</span>
              </div>
            </div>

            <div className="bg-slate-50 border border-slate-200/60 rounded-xl p-4 flex items-center justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-slate-800">Incluir CLI Intelligence Reports</span>
                  <span className="text-[9px] bg-emerald-100 text-emerald-800 font-extrabold px-1.5 py-0.5 rounded uppercase font-mono">SaaS</span>
                </div>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Te permite cambiar de cobro por hora a cobrar un retainer premium recurrente de valor.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setIncludeIntelReports(!includeIntelReports)}
                className={`w-12 h-6 flex items-center rounded-full p-1 transition-colors duration-200 cursor-pointer shrink-0 ${
                  includeIntelReports ? "bg-emerald-700" : "bg-slate-300"
                }`}
              >
                <div className={`bg-white w-4 h-4 rounded-full shadow-md transform duration-200 ${
                  includeIntelReports ? "translate-x-6" : "translate-x-0"
                }`} />
              </button>
            </div>

            <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-4">
              <div>
                <span className="text-[10px] font-mono text-slate-400 font-bold uppercase block">Ingreso Consultor Convencional (Por Hora)</span>
                <span className="text-lg font-bold text-slate-600 font-mono mt-0.5 block">
                  USD {currentRevenue.toLocaleString()} / mes
                </span>
                <span className="text-[10px] text-slate-400 font-medium block">Promedio de 10h al mes por cliente</span>
              </div>

              <div className="pt-4 border-t border-slate-200">
                <div className="flex items-center gap-1.5 mb-1">
                  <span className="text-[10px] font-mono text-emerald-700 font-extrabold uppercase tracking-wider block">Ingreso Consultor Científico (Con CLI Intel)</span>
                  <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-extrabold bg-emerald-50 text-emerald-700 border border-emerald-100">
                    Súper ROI
                  </span>
                </div>
                <span className="text-3xl font-extrabold text-slate-900 font-mono block">
                  USD {intelRevenue.toLocaleString()} <span className="text-xs font-medium text-slate-500">/ mes</span>
                </span>
                <span className="text-[11px] text-emerald-700 font-bold block mt-1">
                  {includeIntelReports ? (
                    `⚡ ¡Generas ${revenueMultiplier}x más ingresos ofreciendo auditorías de datos continuas!`
                  ) : (
                    "💡 Activa el switch para ver el incremento de tus honorarios"
                  )}
                </span>
              </div>

              {includeIntelReports && (
                <div className="pt-3 border-t border-dashed border-slate-200 grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="text-slate-400 font-bold block text-[10px] uppercase font-mono">Costo Licencia CLI Intel</span>
                    <span className="font-semibold text-slate-700 font-mono mt-0.5 block">USD {(99 * clientCount).toLocaleString()} / mes</span>
                    <span className="text-[9px] text-slate-400">USD 99/mes por cliente</span>
                  </div>
                  <div>
                    <span className="text-emerald-600 font-bold block text-[10px] uppercase font-mono">Tu Margen Neto Extra</span>
                    <span className="font-extrabold text-emerald-600 font-mono mt-0.5 block">USD {(intelRevenue - (99 * clientCount) - currentRevenue).toLocaleString()} / mes</span>
                    <span className="text-[9px] text-emerald-500">100% de utilidad extra</span>
                  </div>
                </div>
              )}
            </div>

            <a
              href="#contact-form"
              className="w-full flex items-center justify-center gap-2 py-3 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl text-xs transition-all shadow-md shadow-emerald-100 cursor-pointer"
            >
              <span>Quiero licenciar CLI Intelligence</span>
              <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>

      <div className="mt-12 bg-slate-950 border border-slate-800 rounded-3xl p-6 sm:p-10 text-slate-100 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-700/10 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-3xl mb-8">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-mono font-bold bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 mb-4">
            🛡️ ESTRATEGIA DE BLINDAJE Y MONETIZACIÓN
          </span>
          <h3 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white mb-3">
            ¿Por qué tu cliente corporativo jamás podrá eliminarte?
          </h3>
          <p className="text-sm text-slate-300 leading-relaxed font-light">
            Las herramientas de software asustan a algunos asesores porque temen ser reemplazados. Con CLI Market es exactamente lo opuesto: <strong className="text-white">la data cruda sin criterio metodológico es solo ruido</strong>. Así blindamos tu posición y multiplicamos tus honorarios:
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 hover:border-slate-700 transition-all">
            <div className="w-10 h-10 bg-emerald-500/10 text-emerald-400 rounded-xl flex items-center justify-center mb-4">
              <Zap className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-white mb-2 uppercase tracking-wide">1. Asimetría de Poder</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              El retail manager de tu cliente no tiene tiempo ni metodología para auditar crawlers. <strong className="text-slate-200">Tú posees el control de la interpretación</strong>. La data es el insumo; tú eres el autor del plan estratégico que genera el retorno esperado.
            </p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 hover:border-slate-700 transition-all">
            <div className="w-10 h-10 bg-emerald-500/10 text-emerald-400 rounded-xl flex items-center justify-center mb-4">
              <Percent className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-white mb-2 uppercase tracking-wide">2. Cobro por Retorno</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              En lugar de justificar horas de trabajo, vendes <strong className="text-slate-200">mitigación de riesgos y ganancias potenciales</strong>. Al detectar que un competidor aumentó 15% su precio premium, el valor de esa sola señal supera por 10x tus honorarios mensuales.
            </p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 hover:border-slate-700 transition-all">
            <div className="w-10 h-10 bg-rose-500/10 text-rose-400 rounded-xl flex items-center justify-center mb-4">
              <AlertCircle className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-white mb-2 uppercase tracking-wide">3. Canal 100% Exclusivo</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Garantizamos contractualmente que <strong className="text-slate-200">no vendemos de forma directa a las marcas corporativas</strong>. Para acceder a CLI Intelligence, las empresas deben contratar a un consultor aliado certificado. Tu mercado está blindado por diseño.
            </p>
          </div>
        </div>

        <div className="border border-slate-800 bg-slate-900/30 rounded-2xl p-6">
          <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-300 mb-4 flex items-center gap-2">
            <FileSpreadsheet className="w-4 h-4" /> Glosario de Argumentación Comercial para tus Clientes
          </h4>

          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-6 text-xs text-slate-300">
            <div>
              <span className="text-[10px] uppercase font-mono font-bold text-slate-500 block mb-1">Ahorro y Eficiencia</span>
              <p className="font-semibold text-white mb-0.5">Reducción de Tiempos: -95%</p>
              <p className="text-slate-400">Automatiza la toma de precios de semanas de auditorías manuales a reportes listos en segundos.</p>
            </div>

            <div>
              <span className="text-[10px] uppercase font-mono font-bold text-slate-500 block mb-1">Mitigación de Riesgos</span>
              <p className="font-semibold text-white mb-0.5">Control Total sobre Mermas</p>
              <p className="text-slate-400">Detección oportuna de quiebres de stock virtuales y desvíos de precios que destruyen la rentabilidad.</p>
            </div>

            <div>
              <span className="text-[10px] uppercase font-mono font-bold text-slate-500 block mb-1">Retorno Esperado</span>
              <p className="font-semibold text-white mb-0.5">Ganancias Potenciales: +12%</p>
              <p className="text-slate-400">Captura de spreads de canal optimizando la fijación de precios en base a hechos de góndola en tiempo real.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
