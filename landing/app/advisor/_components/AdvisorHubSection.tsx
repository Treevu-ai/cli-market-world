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
import { useLang } from "@/lib/LanguageContext";

const COUNTRIES = [
  { key: "PE", label_es: "Perú (PE)", label_en: "Peru (PE)" },
  { key: "MX", label_es: "México (MX)", label_en: "Mexico (MX)" },
  { key: "CO", label_es: "Colombia (CO)", label_en: "Colombia (CO)" },
  { key: "CL", label_es: "Chile (CL)", label_en: "Chile (CL)" },
  { key: "AR", label_es: "Argentina (AR)", label_en: "Argentina (AR)" },
  { key: "BR", label_es: "Brasil (BR)", label_en: "Brazil (BR)" },
];

function fmtPct(value?: number | null, signed = true) {
  if (value === undefined || value === null || Number.isNaN(value)) return "—";
  const n = Number(value);
  if (signed) return `${n >= 0 ? "+" : ""}${n.toFixed(1)}%`;
  return `${n.toFixed(1)}%`;
}

export default function AdvisorHubSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  const [selectedCountry, setSelectedCountry] = useState("PE");
  const { data, loading, error } = useAdvisorPulse(selectedCountry, lang);

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
    ? isES
      ? `La mayor anomalía está en ${anomaly.subcategory} (${fmtPct(anomaly.delta_pct)}). Recomienda a tu cliente revisar su posicionamiento de precio y canal en esa categoría antes de la próxima negociación.`
      : `The largest anomaly is in ${anomaly.subcategory} (${fmtPct(anomaly.delta_pct)}). Recommend your client review price and channel positioning in that category before the next negotiation.`
    : isES
      ? `Monitorea la inflación de estantería (${fmtPct(kpis.inflation_pct)}) y la dispersión PVI (${fmtPct(kpis.pvi, false)}) para detectar ventanas de renegociación con retailers.`
      : `Monitor shelf inflation (${fmtPct(kpis.inflation_pct)}) and PVI dispersion (${fmtPct(kpis.pvi, false)}) to spot renegotiation windows with retailers.`;

  const handleCopyTactic = () => {
    const label = isES ? "TÁCTICA DE ASESOR CLI MARKET" : "CLI MARKET ADVISOR TACTIC";
    const countryLabel = isES ? "País" : "Country";
    navigator.clipboard.writeText(`[${label}] - ${countryLabel}: ${selectedCountry}. ${advisorTactic}`);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <section id="advisor-hub" className="landing-section scroll-mt-20">
      <div className="landing-container-wide">
      <div className="landing-section-header text-center">
        <p className="section-eyebrow mb-4 inline-flex items-center gap-1.5">
          <Zap className="w-3.5 h-3.5" /> {isES ? "RADAR DE GÓNDOLA · DATOS EN VIVO" : "SHELF RADAR · LIVE DATA"}
        </p>
        <h2 className="section-title">
          {isES ? "Consola de radar en vivo" : "Live radar console"}
        </h2>
        <p className="section-intro">
          {isES ? (
            <>
              Conéctate a los datos verificados de <strong className="text-[var(--cm-on-surface)] font-medium">cli-market.dev/advisor</strong> para construir recomendaciones con respaldo empírico. Detecta inflación de estantería, dispersión de precios y anomalías con evidencia trazable.
            </>
          ) : (
            <>
              Connect to the verified data behind <strong className="text-[var(--cm-on-surface)] font-medium">cli-market.dev/advisor</strong> to back your recommendations with evidence. Track shelf inflation, price dispersion, and anomalies with traceable data.
            </>
          )}
        </p>
      </div>

      <div className="grid sm:grid-cols-3 gap-4 max-w-3xl mx-auto mt-10 mb-10">
        <div className="card-cyber rounded-xl p-4 text-center">
          <p className="text-xs text-[var(--cm-text-secondary)] uppercase font-mono tracking-wider">
            {isES ? "Ahorro y Eficiencia" : "Savings & Efficiency"}
          </p>
          <p className="text-sm font-semibold text-[var(--cm-action-deep)] mt-1">
            {isES ? "Automatización de auditorías" : "Automated audits"}
          </p>
        </div>
        <div className="card-cyber rounded-xl p-4 text-center">
          <p className="text-xs text-[var(--cm-text-secondary)] uppercase font-mono tracking-wider">
            {isES ? "Visibilidad Comercial" : "Commercial Visibility"}
          </p>
          <p className="text-sm font-semibold text-[var(--cm-action-deep)] mt-1">
            {isES ? "Señales antes del IPC" : "Signals ahead of CPI"}
          </p>
        </div>
        <div className="card-cyber rounded-xl p-4 text-center">
          <p className="text-xs text-[var(--cm-text-secondary)] uppercase font-mono tracking-wider">
            {isES ? "Nuevas Líneas de Ingreso" : "New Revenue Lines"}
          </p>
          <p className="text-sm font-semibold text-[var(--cm-action-deep)] mt-1">
            {isES ? "Retainers de datos" : "Data retainers"}
          </p>
        </div>
      </div>

      <div className="grid lg:grid-cols-12 gap-8 items-start">
        <div className="lg:col-span-7 bg-[var(--cm-surface)] rounded-2xl border border-[var(--cm-outline-variant)] p-6 sm:p-8 shadow-xs">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-[var(--cm-hairline-soft)]">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-[var(--cm-action-soft)] text-[var(--cm-action-deep)] rounded-lg">
                <Globe className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-[var(--cm-on-surface)] text-base sm:text-lg">
                  {isES ? "Consola: cli-market.dev/advisor" : "Console: cli-market.dev/advisor"}
                </h3>
                <p className="text-xs text-[var(--cm-text-secondary)]">
                  {isES
                    ? "Métricas de control en tiempo real para mitigación de riesgos y visibilidad comercial."
                    : "Real-time control metrics for risk mitigation and commercial visibility."}
                </p>
              </div>
            </div>
            <span className="inline-flex items-center gap-1 text-[11px] font-mono text-[var(--cm-action-deep)] bg-[var(--cm-action-soft)] px-2 py-0.5 rounded-full font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--cm-mint)] animate-pulse" /> LIVE
            </span>
          </div>

          <div className="mb-6">
            <label className="block text-xs font-bold text-[var(--cm-on-surface-variant)] mb-1">
              {isES ? "País seleccionado" : "Selected country"}
            </label>
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="w-full text-xs sm:text-sm bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-lg p-2.5 outline-none focus:ring-1 focus:ring-[var(--cm-mint)] focus:border-[var(--cm-mint)] transition-all font-semibold text-[var(--cm-on-surface-variant)] cursor-pointer"
            >
              {COUNTRIES.map((c) => (
                <option key={c.key} value={c.key}>
                  {isES ? c.label_es : c.label_en}
                </option>
              ))}
            </select>
          </div>

          {loading ? (
            <div className="p-8 text-center text-sm text-[var(--cm-text-secondary)]">
              {isES ? "Cargando señales de góndola…" : "Loading shelf signals…"}
            </div>
          ) : error ? (
            <div className="p-6 bg-rose-50 border border-rose-100 rounded-xl text-sm text-rose-700">
              {isES
                ? "No se pudieron cargar los datos en vivo. Verifica tu conexión o recarga la página."
                : "Live data couldn't be loaded. Check your connection or reload the page."}
            </div>
          ) : (
            <>
              {data?.headline && (
                <div className="mb-6 bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-xl p-4">
                  <p className="text-xs font-mono font-bold text-[var(--cm-text-secondary)] uppercase tracking-wider mb-1">Headline</p>
                  <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">{data.headline}</p>
                </div>
              )}

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <div className="bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)]/80 rounded-xl p-3.5 text-center transition-all hover:bg-[var(--cm-outline-variant)]/20">
                  <span className="text-[10px] font-mono text-[var(--cm-text-secondary)] font-bold uppercase block">
                    {isES ? "Inflación retail" : "Retail inflation"}
                  </span>
                  <span className="text-sm sm:text-base font-extrabold text-[var(--cm-on-surface)] mt-1 block flex items-center justify-center gap-1">
                    {(kpis.inflation_pct ?? 0) >= 0 ? (
                      <TrendingUp className="w-3.5 h-3.5 text-rose-500 shrink-0" />
                    ) : (
                      <TrendingDown className="w-3.5 h-3.5 text-[var(--cm-mint)] shrink-0" />
                    )}
                    {fmtPct(kpis.inflation_pct)}
                  </span>
                </div>

                <div className="bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)]/80 rounded-xl p-3.5 text-center transition-all hover:bg-[var(--cm-outline-variant)]/20">
                  <span className="text-[10px] font-mono text-[var(--cm-text-secondary)] font-bold uppercase block">
                    {isES ? "PVI · dispersión" : "PVI · dispersion"}
                  </span>
                  <span className="text-sm sm:text-base font-extrabold text-[var(--cm-action-deep)] mt-1 block">
                    {fmtPct(kpis.pvi, false)}
                  </span>
                </div>

                <div className="bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)]/80 rounded-xl p-3.5 text-center transition-all hover:bg-[var(--cm-outline-variant)]/20">
                  <span className="text-[10px] font-mono text-[var(--cm-text-secondary)] font-bold uppercase block">
                    {isES ? "BAI · canasta" : "BAI · basket"}
                  </span>
                  <span className="text-sm sm:text-base font-extrabold text-[var(--cm-on-surface)] mt-1 block">
                    {kpis.bai ?? "—"}
                  </span>
                </div>

                <div className="bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)]/80 rounded-xl p-3.5 text-center transition-all hover:bg-[var(--cm-outline-variant)]/20">
                  <span className="text-[10px] font-mono text-[var(--cm-text-secondary)] font-bold uppercase block">
                    {isES ? "RCS · fairness" : "RCS · fairness"}
                  </span>
                  <span className="text-sm sm:text-base font-extrabold text-[var(--cm-on-surface)] mt-1 block">
                    {kpis.rcs ?? "—"}
                  </span>
                </div>
              </div>

              <div className="space-y-4 mb-6">
                {anomaly?.subcategory && (
                  <div className="bg-[var(--cm-action-soft)]/60 border border-[var(--cm-mint)]/20 rounded-xl p-4">
                    <div className="flex items-center gap-1.5 mb-2">
                      <BarChart3 className="w-4 h-4 text-[var(--cm-action-deep)]" />
                      <span className="text-xs font-mono font-bold text-[var(--cm-action-deep)] uppercase tracking-wider">
                        {isES ? "Mayor anomalía detectada" : "Largest anomaly detected"}
                      </span>
                    </div>
                    <p className="text-sm font-extrabold text-[var(--cm-on-surface)]">
                      {anomaly.subcategory} {fmtPct(anomaly.delta_pct)}
                    </p>
                    <p className="text-xs text-[var(--cm-text-secondary)] mt-1">
                      {isES
                        ? "Variación vs mediana de la categoría. Punto de partida para revisar la negociación con retailers."
                        : "Variation vs. category median. A starting point for reviewing retailer negotiations."}
                    </p>
                  </div>
                )}

                {data?.executive_highlights && data.executive_highlights.length > 0 && (
                  <div className="border border-[var(--cm-outline-variant)] rounded-xl p-4 bg-[var(--cm-surface-high)]/60">
                    <div className="flex items-center gap-1.5 mb-2 text-[var(--cm-on-surface-variant)]">
                      <AlertCircle className="w-4 h-4 text-[var(--cm-action-deep)]" />
                      <span className="text-xs font-semibold uppercase tracking-wider">
                        {isES ? "Highlights ejecutivos" : "Executive highlights"}
                      </span>
                    </div>
                    <ul className="text-xs sm:text-sm text-[var(--cm-on-surface-variant)] leading-relaxed font-medium space-y-2">
                      {data.executive_highlights.map((h, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-[var(--cm-action-deep)]">•</span>
                          <span>{h}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {moat.total_indexed !== undefined && (
                  <div className="grid grid-cols-3 gap-3 text-center">
                    <div className="bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)]/80 rounded-xl p-3">
                      <span className="text-[10px] font-mono text-[var(--cm-text-secondary)] font-bold uppercase block">
                        {isES ? "Indexados" : "Indexed"}
                      </span>
                      <span className="text-sm font-extrabold text-[var(--cm-on-surface)]">
                        {Number(moat.total_indexed).toLocaleString()}
                      </span>
                    </div>
                    <div className="bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)]/80 rounded-xl p-3">
                      <span className="text-[10px] font-mono text-[var(--cm-text-secondary)] font-bold uppercase block">
                        {isES ? "Refresh 24h" : "24h refresh"}
                      </span>
                      <span className="text-sm font-extrabold text-[var(--cm-on-surface)]">
                        {Number(moat.snapshots_24h).toLocaleString()}
                      </span>
                    </div>
                    <div className="bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)]/80 rounded-xl p-3">
                      <span className="text-[10px] font-mono text-[var(--cm-text-secondary)] font-bold uppercase block">
                        {isES ? "Cobertura 7d" : "7d coverage"}
                      </span>
                      <span className="text-sm font-extrabold text-[var(--cm-on-surface)]">
                        {fmtPct(moat.coverage_7d_pct, false)}
                      </span>
                    </div>
                  </div>
                )}
              </div>

              <div className="bg-[var(--cm-ink)] rounded-xl p-5 sm:p-6 text-[var(--cm-surface)] relative overflow-hidden shadow-md">
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full blur-xl pointer-events-none" />
                <div className="flex items-center gap-2 mb-3">
                  <Zap className="w-4 h-4 text-[var(--cm-mint)]" />
                  <span className="text-xs font-bold text-[var(--cm-mint)] uppercase tracking-widest font-mono">
                    {isES ? "TÁCTICA RECOMENDADA" : "SUGGESTED TALKING POINT"}
                  </span>
                </div>

                <h4 className="text-sm sm:text-base font-bold mb-2">
                  {isES ? "Punto de partida para tu propuesta comercial:" : "A starting point for your client proposal:"}
                </h4>
                <p className="text-xs sm:text-sm text-[var(--cm-surface)]/80 leading-relaxed font-light italic mb-4">
                  &ldquo;{advisorTactic}&rdquo;
                </p>

                <div className="flex items-center justify-between pt-3 border-t border-white/10">
                  <span className="text-[10px] text-[var(--cm-surface)]/50">
                    {isES ? "Cópialo directo a tu propuesta" : "Copy it straight into your proposal"}
                  </span>
                  <button
                    type="button"
                    onClick={handleCopyTactic}
                    className="flex items-center gap-1.5 text-[11px] bg-[var(--cm-surface)]/10 hover:bg-[var(--cm-surface)]/15 text-[var(--cm-surface)] px-3 py-1.5 rounded-lg border border-[var(--cm-surface)]/15 transition-all cursor-pointer"
                  >
                    {isCopied ? (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5 text-[var(--cm-mint)]" />
                        <span className="text-[var(--cm-mint)] font-bold">{isES ? "¡Copiado!" : "Copied!"}</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span>{isES ? "Copiar táctica" : "Copy talking point"}</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </>
          )}
        </div>

        <div className="lg:col-span-5 bg-[var(--cm-surface)] rounded-2xl border border-[var(--cm-outline-variant)] p-6 sm:p-8 shadow-xs">
          <div className="flex items-center gap-2 mb-6 pb-4 border-b border-[var(--cm-hairline-soft)]">
            <div className="p-2 bg-[var(--cm-action-soft)] text-[var(--cm-action-deep)] rounded-lg">
              <Calculator className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-[var(--cm-on-surface)] text-base sm:text-lg">
                {isES ? "Calculadora de retorno esperado" : "Expected return calculator"}
              </h3>
              <p className="text-xs text-[var(--cm-text-secondary)]">
                {isES
                  ? "Estima el efecto de pasar de cobro por hora a un retainer de datos."
                  : "Estimate the effect of moving from hourly billing to a data retainer."}
              </p>
            </div>
          </div>

          <div className="space-y-5">
            <div>
              <div className="flex justify-between text-xs font-bold text-[var(--cm-on-surface-variant)] mb-1">
                <span>{isES ? "Tu tarifa por hora actual" : "Your current hourly rate"}</span>
                <span className="text-[var(--cm-action-deep)] font-mono">USD {hourlyRate} / h</span>
              </div>
              <input
                type="range"
                min="30"
                max="250"
                step="5"
                value={hourlyRate}
                onChange={(e) => setHourlyRate(Number(e.target.value))}
                className="w-full accent-[var(--cm-mint)] h-1.5 bg-[var(--cm-surface-high)] rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-[var(--cm-text-secondary)] font-medium mt-1">
                <span>USD 30/h</span>
                <span>USD 140/h</span>
                <span>USD 250/h</span>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold text-[var(--cm-on-surface-variant)] mb-1">
                <span>{isES ? "Clientes activos al mes" : "Active clients per month"}</span>
                <span className="text-[var(--cm-action-deep)] font-mono">
                  {clientCount} {isES ? "clientes" : "clients"}
                </span>
              </div>
              <input
                type="range"
                min="1"
                max="15"
                step="1"
                value={clientCount}
                onChange={(e) => setClientCount(Number(e.target.value))}
                className="w-full accent-[var(--cm-mint)] h-1.5 bg-[var(--cm-surface-high)] rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-[var(--cm-text-secondary)] font-medium mt-1">
                <span>{isES ? "1 cliente" : "1 client"}</span>
                <span>{isES ? "8 clientes" : "8 clients"}</span>
                <span>{isES ? "15 clientes" : "15 clients"}</span>
              </div>
            </div>

            <div className="bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)]/60 rounded-xl p-4 flex items-center justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-[var(--cm-on-surface)]">
                    {isES ? "Incluir CLI Intelligence Reports" : "Include CLI Intelligence Reports"}
                  </span>
                  <span className="text-[9px] bg-[var(--cm-action-soft)] text-[var(--cm-action-deep)] font-extrabold px-1.5 py-0.5 rounded uppercase font-mono">SaaS</span>
                </div>
                <p className="text-[11px] text-[var(--cm-text-secondary)] mt-0.5">
                  {isES
                    ? "Modela el paso de cobro por hora a un retainer de datos recurrente."
                    : "Models the shift from hourly billing to a recurring data retainer."}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setIncludeIntelReports(!includeIntelReports)}
                className={`w-12 h-6 flex items-center rounded-full p-1 transition-colors duration-200 cursor-pointer shrink-0 ${
                  includeIntelReports ? "bg-[var(--cm-mint)]" : "bg-[var(--cm-outline-variant)]"
                }`}
              >
                <div className={`bg-[var(--cm-surface)] w-4 h-4 rounded-full shadow-md transform duration-200 ${
                  includeIntelReports ? "translate-x-6" : "translate-x-0"
                }`} />
              </button>
            </div>

            <div className="bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-xl p-5 space-y-4">
              <div>
                <span className="text-[10px] font-mono text-[var(--cm-text-secondary)] font-bold uppercase block">
                  {isES ? "Ingreso por hora (modelo actual)" : "Hourly-billing revenue (current model)"}
                </span>
                <span className="text-lg font-bold text-[var(--cm-on-surface-variant)] font-mono mt-0.5 block">
                  USD {currentRevenue.toLocaleString()} {isES ? "/ mes" : "/ mo"}
                </span>
                <span className="text-[10px] text-[var(--cm-text-secondary)] font-medium block">
                  {isES ? "Promedio de 10h al mes por cliente" : "Average of 10h/month per client"}
                </span>
              </div>

              <div className="pt-4 border-t border-[var(--cm-outline-variant)]">
                <span className="text-[10px] font-mono text-[var(--cm-action-deep)] font-extrabold uppercase tracking-wider block mb-1">
                  {isES ? "Ingreso con retainer de datos (con CLI Intel)" : "Data-retainer revenue (with CLI Intel)"}
                </span>
                <span className="text-3xl font-extrabold text-[var(--cm-on-surface)] font-mono block">
                  USD {intelRevenue.toLocaleString()} <span className="text-xs font-medium text-[var(--cm-text-secondary)]">{isES ? "/ mes" : "/ mo"}</span>
                </span>
                <span className="text-[11px] text-[var(--cm-action-deep)] font-bold block mt-1">
                  {includeIntelReports
                    ? isES
                      ? `Proyecta ${revenueMultiplier}x más ingresos ofreciendo auditorías de datos continuas.`
                      : `Projects ${revenueMultiplier}x more revenue by offering ongoing data audits.`
                    : isES
                      ? "Activa el switch para ver el efecto en tus honorarios."
                      : "Toggle the switch to see the effect on your fees."}
                </span>
              </div>

              {includeIntelReports && (
                <div className="pt-3 border-t border-dashed border-[var(--cm-outline-variant)] grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="text-[var(--cm-text-secondary)] font-bold block text-[10px] uppercase font-mono">
                      {isES ? "Costo licencia CLI Intel" : "CLI Intel license cost"}
                    </span>
                    <span className="font-semibold text-[var(--cm-on-surface-variant)] font-mono mt-0.5 block">
                      USD {(99 * clientCount).toLocaleString()} {isES ? "/ mes" : "/ mo"}
                    </span>
                    <span className="text-[9px] text-[var(--cm-text-secondary)]">
                      {isES ? "USD 99/mes por cliente" : "USD 99/mo per client"}
                    </span>
                  </div>
                  <div>
                    <span className="text-[var(--cm-action-deep)] font-bold block text-[10px] uppercase font-mono">
                      {isES ? "Margen neto extra" : "Extra net margin"}
                    </span>
                    <span className="font-extrabold text-[var(--cm-action-deep)] font-mono mt-0.5 block">
                      USD {(intelRevenue - (99 * clientCount) - currentRevenue).toLocaleString()} {isES ? "/ mes" : "/ mo"}
                    </span>
                    <span className="text-[9px] text-[var(--cm-action-deep)]/80">
                      {isES ? "Sobre el modelo actual" : "Over the current model"}
                    </span>
                  </div>
                </div>
              )}
            </div>

            <a href="#contact-form" className="btn-mint w-full gap-2">
              <span>{isES ? "Quiero licenciar CLI Intelligence" : "I want to license CLI Intelligence"}</span>
              <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>

      <div className="mt-12 bg-[var(--cm-ink)] border border-[var(--cm-outline-variant)] rounded-3xl p-6 sm:p-10 text-[var(--cm-surface)] shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-[var(--cm-mint)]/10 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-3xl mb-8">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-mono font-bold bg-[var(--cm-mint)]/10 border border-[var(--cm-mint)]/20 text-[var(--cm-mint)] mb-4">
            {isES ? "POSICIONAMIENTO Y MODELO DE INGRESOS" : "POSITIONING & REVENUE MODEL"}
          </span>
          <h3 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-[var(--cm-surface)] mb-3">
            {isES ? "Por qué la data sola no reemplaza tu criterio" : "Why raw data doesn't replace your judgment"}
          </h3>
          <p className="text-sm text-[var(--cm-surface)]/70 leading-relaxed font-light">
            {isES ? (
              <>
                Algunos asesores dudan de las herramientas de software por temor a ser reemplazados. Con CLI Market ocurre lo contrario: <strong className="text-[var(--cm-surface)]">la data cruda sin criterio metodológico es solo ruido</strong>. Así es como el modelo protege tu posición y abre nuevas líneas de ingreso:
              </>
            ) : (
              <>
                Some advisors are wary of software tools out of fear of being replaced. With CLI Market it's the opposite: <strong className="text-[var(--cm-surface)]">raw data without methodological judgment is just noise</strong>. Here's how the model protects your position and opens new revenue lines:
              </>
            )}
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-[var(--cm-surface)]/5 border border-[var(--cm-surface)]/10 rounded-2xl p-5 hover:border-[var(--cm-surface)]/20 transition-all">
            <div className="w-10 h-10 bg-[var(--cm-mint)]/10 text-[var(--cm-mint)] rounded-xl flex items-center justify-center mb-4">
              <Zap className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-[var(--cm-surface)] mb-2 uppercase tracking-wide">
              {isES ? "1. Interpretación con criterio" : "1. Judgment-driven interpretation"}
            </h4>
            <p className="text-xs text-[var(--cm-surface)]/60 leading-relaxed">
              {isES ? (
                <>
                  El equipo de retail de tu cliente rara vez tiene tiempo o metodología para auditar datos de crawlers. <strong className="text-[var(--cm-surface)]/90">Tú aportas la interpretación</strong>: la data es el insumo, tú eres el autor del plan estratégico.
                </>
              ) : (
                <>
                  Your client's retail team rarely has the time or methodology to audit crawler data. <strong className="text-[var(--cm-surface)]/90">You provide the interpretation</strong> — the data is the input, you author the strategic plan.
                </>
              )}
            </p>
          </div>

          <div className="bg-[var(--cm-surface)]/5 border border-[var(--cm-surface)]/10 rounded-2xl p-5 hover:border-[var(--cm-surface)]/20 transition-all">
            <div className="w-10 h-10 bg-[var(--cm-mint)]/10 text-[var(--cm-mint)] rounded-xl flex items-center justify-center mb-4">
              <Percent className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-[var(--cm-surface)] mb-2 uppercase tracking-wide">
              {isES ? "2. Cobro por resultado" : "2. Value-based billing"}
            </h4>
            <p className="text-xs text-[var(--cm-surface)]/60 leading-relaxed">
              {isES ? (
                <>
                  En lugar de justificar horas de trabajo, vendes <strong className="text-[var(--cm-surface)]/90">mitigación de riesgos y visibilidad comercial</strong>. Detectar a tiempo que un competidor subió 15% su precio premium puede valer varias veces tus honorarios mensuales.
                </>
              ) : (
                <>
                  Instead of justifying hours worked, you sell <strong className="text-[var(--cm-surface)]/90">risk mitigation and commercial visibility</strong>. Catching a competitor's 15% premium-price increase early can be worth several times your monthly fee.
                </>
              )}
            </p>
          </div>

          <div className="bg-[var(--cm-surface)]/5 border border-[var(--cm-surface)]/10 rounded-2xl p-5 hover:border-[var(--cm-surface)]/20 transition-all">
            <div className="w-10 h-10 bg-rose-500/10 text-rose-400 rounded-xl flex items-center justify-center mb-4">
              <AlertCircle className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-[var(--cm-surface)] mb-2 uppercase tracking-wide">
              {isES ? "3. Canal cerrado" : "3. Closed channel"}
            </h4>
            <p className="text-xs text-[var(--cm-surface)]/60 leading-relaxed">
              {isES ? (
                <>
                  No vendemos de forma directa a las marcas corporativas: para acceder a CLI Intelligence, las empresas contratan a un consultor aliado. <strong className="text-[var(--cm-surface)]/90">Tu canal comercial no compite contigo.</strong>
                </>
              ) : (
                <>
                  We don't sell directly to corporate brands — to access CLI Intelligence, companies work through a partner consultant. <strong className="text-[var(--cm-surface)]/90">Your commercial channel doesn't compete with you.</strong>
                </>
              )}
            </p>
          </div>
        </div>

        <div className="border border-[var(--cm-surface)]/10 bg-[var(--cm-surface)]/5 rounded-2xl p-6">
          <h4 className="text-xs font-bold uppercase tracking-wider text-[var(--cm-mint)] mb-4 flex items-center gap-2">
            <FileSpreadsheet className="w-4 h-4" /> {isES ? "Glosario para tus propuestas comerciales" : "Glossary for your client proposals"}
          </h4>

          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-6 text-xs text-[var(--cm-surface)]/70">
            <div>
              <span className="text-[10px] uppercase font-mono font-bold text-[var(--cm-surface)]/45 block mb-1">
                {isES ? "Ahorro y eficiencia" : "Savings & efficiency"}
              </span>
              <p className="font-semibold text-[var(--cm-surface)] mb-0.5">
                {isES ? "Reducción de tiempos: -95%" : "Time reduction: -95%"}
              </p>
              <p className="text-[var(--cm-surface)]/55">
                {isES
                  ? "Automatiza la toma de precios, de semanas de auditorías manuales a reportes listos en segundos."
                  : "Automates price collection — from weeks of manual audits to reports ready in seconds."}
              </p>
            </div>

            <div>
              <span className="text-[10px] uppercase font-mono font-bold text-[var(--cm-surface)]/45 block mb-1">
                {isES ? "Mitigación de riesgos" : "Risk mitigation"}
              </span>
              <p className="font-semibold text-[var(--cm-surface)] mb-0.5">
                {isES ? "Visibilidad sobre mermas" : "Visibility into margin erosion"}
              </p>
              <p className="text-[var(--cm-surface)]/55">
                {isES
                  ? "Detección oportuna de quiebres de stock virtuales y desvíos de precios que afectan la rentabilidad."
                  : "Timely detection of phantom stock-outs and price deviations that hurt profitability."}
              </p>
            </div>

            <div>
              <span className="text-[10px] uppercase font-mono font-bold text-[var(--cm-surface)]/45 block mb-1">
                {isES ? "Retorno esperado" : "Expected return"}
              </span>
              <p className="font-semibold text-[var(--cm-surface)] mb-0.5">
                {isES ? "Ganancias potenciales: +12%" : "Potential upside: +12%"}
              </p>
              <p className="text-[var(--cm-surface)]/55">
                {isES
                  ? "Captura de spreads de canal optimizando la fijación de precios con hechos de góndola en tiempo real."
                  : "Captures channel spreads by optimizing pricing with real-time shelf data."}
              </p>
            </div>
          </div>
        </div>
      </div>
      </div>
    </section>
  );
}
