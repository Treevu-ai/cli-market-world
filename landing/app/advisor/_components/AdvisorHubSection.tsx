"use client";

import { useState } from "react";
import {
  TrendingUp,
  TrendingDown,
  Globe,
  BarChart3,
  Zap,
  CheckCircle2,
  AlertCircle,
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
  const [isCopied, setIsCopied] = useState(false);

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

      <div className="max-w-3xl mx-auto">
        <div className="bg-[var(--cm-surface)] rounded-2xl border border-[var(--cm-outline-variant)] p-6 sm:p-8 shadow-xs">
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

              <div className="bg-[var(--cm-action-soft)]/60 border border-[var(--cm-mint)]/20 rounded-xl p-5 sm:p-6">
                <div className="flex items-center gap-2 mb-3">
                  <Zap className="w-4 h-4 text-[var(--cm-action-deep)]" />
                  <span className="text-xs font-bold text-[var(--cm-action-deep)] uppercase tracking-widest font-mono">
                    {isES ? "TÁCTICA RECOMENDADA" : "SUGGESTED TALKING POINT"}
                  </span>
                </div>

                <h4 className="text-sm sm:text-base font-bold text-[var(--cm-on-surface)] mb-2">
                  {isES ? "Punto de partida para tu propuesta comercial:" : "A starting point for your client proposal:"}
                </h4>
                <p className="text-xs sm:text-sm text-[var(--cm-on-surface-variant)] leading-relaxed italic mb-4">
                  &ldquo;{advisorTactic}&rdquo;
                </p>

                <div className="flex items-center justify-between pt-3 border-t border-[var(--cm-mint)]/15">
                  <span className="text-[10px] text-[var(--cm-text-secondary)]">
                    {isES ? "Cópialo directo a tu propuesta" : "Copy it straight into your proposal"}
                  </span>
                  <button
                    type="button"
                    onClick={handleCopyTactic}
                    className="flex items-center gap-1.5 text-[11px] bg-[var(--cm-surface)] hover:bg-[var(--cm-surface-high)] text-[var(--cm-on-surface-variant)] px-3 py-1.5 rounded-lg border border-[var(--cm-outline-variant)] transition-all cursor-pointer"
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
      </div>
      </div>
    </section>
  );
}
