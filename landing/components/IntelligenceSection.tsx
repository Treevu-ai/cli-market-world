"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { API_URL } from "@/lib/api";
import LegalConsentCheckbox from "@/components/LegalConsentCheckbox";

const BENEFITS_ES = [
  { icon: "▸", text: `Precios de góndola cada ${MARKET_STATS.pricesRefreshHours}h — no estimaciones con 30 días de retraso` },
  { icon: "●", text: "Precios normalizados por kg/L para comparar categorías entre cadenas y países" },
  { icon: "▲", text: `${MARKET_STATS.indicatorsCount} indicadores intel: spread entre cadenas, inflación real, tendencias (CLI: market intel)` },
  { icon: "▸", text: `${MARKET_STATS.retailersVerified} retailers verificados en ${MARKET_STATS.countries} países — sin scraping, APIs públicas de catálogo` },
];

const BENEFITS_EN = [
  { icon: "▸", text: `Shelf prices every ${MARKET_STATS.pricesRefreshHours}h — not 30-day-lagged estimates` },
  { icon: "●", text: "Prices normalized per kg/L to compare categories across chains and countries" },
  { icon: "▲", text: `${MARKET_STATS.indicatorsCount} intel indicators: chain spread, real inflation, historical trends (CLI: market intel)` },
  { icon: "▸", text: `${MARKET_STATS.retailersVerified} verified retailers across ${MARKET_STATS.countries} countries — no scraping, public catalog APIs` },
];

export default function IntelligenceSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  const [email, setEmail] = useState("");
  const [role, setRole] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [legal, setLegal] = useState(false);

  const benefits = isES ? BENEFITS_ES : BENEFITS_EN;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!legal) {
      setError(
        isES
          ? "Debe aceptar los términos y la política de privacidad."
          : "You must accept the terms and privacy policy.",
      );
      return;
    }
    if (!email.includes("@")) {
      setError(isES ? "Email inválido" : "Invalid email");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/v1/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          plan: "intelligence",
          email,
          use_case: role ? `waitlist · role=${role}` : "waitlist",
          lang: isES ? "es" : "en",
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "error");
      }
      setSent(true);
    } catch {
      setError(
        isES
          ? "No pudimos guardar tu email. Escribe a hello@cli-market.dev"
          : "Could not save your email. Write to hello@cli-market.dev",
      );
    }
    setLoading(false);
  };

  return (
    <section
      id="intelligence"
      className="brand-mode-terminal landing-section landing-section-glow animate-fade-in scroll-mt-20"
    >
      <div className="landing-container-wide">
        <div className="landing-section-header">
          <div className="inline-flex items-center justify-center gap-2 mb-3">
            <p className="section-eyebrow text-[var(--cm-mint)]">Intelligence</p>
            <span className="text-xs font-semibold bg-[var(--cm-mint)]/15 text-[var(--cm-mint)] border border-[var(--cm-mint)]/30 px-2 py-0.5 rounded-full">
              {isES ? "Próximamente" : "Coming soon"}
            </span>
          </div>
          <h2 className="section-title">
            {isES
              ? "Precios reales de góndola. No estimaciones de 30 días."
              : "Real shelf prices. Not 30-day estimates."}
          </h2>
          <p className="section-intro">
            {isES
              ? "Para equipos de pricing, trade marketing y análisis en CPG, retail y fintech. Los catálogos son públicos; el valor está en agregar, normalizar y mantener la serie lista para análisis."
              : "For pricing, trade marketing, and analytics teams in CPG, retail, and fintech. Catalogs are public; the value is aggregating, normalizing, and keeping the series analysis-ready."}
          </p>
        </div>

        <div className="landing-content-rail grid grid-cols-1 lg:grid-cols-2 gap-10 items-start">
          <div className="space-y-5">
            <div className="code-block-cyber px-4 py-3 text-left font-mono text-xs text-[var(--cm-on-surface-variant)]">
              <p className="text-[10px] uppercase tracking-wider text-[var(--cm-mint)]/70 mb-2">
                {isES ? "spread · aceite 900ml · PE" : "spread · oil 900ml · PE"}
              </p>
              <p>Wong <span className="text-[var(--cm-data)]">S/ 18.90</span> /L</p>
              <p>Metro <span className="text-[var(--cm-data)]">S/ 17.40</span> /L</p>
              <p>Plaza Vea <span className="text-[var(--cm-data)]">S/ 19.20</span> /L</p>
              <p className="mt-2 text-[var(--cm-signal)]">
                {isES ? "Spread entre cadenas" : "Cross-chain spread"} · {isES ? "refresh cada" : "refresh every"} {MARKET_STATS.pricesRefreshHours}h
              </p>
              <p className="text-[10px] text-[var(--cm-on-surface-variant)]/50 mt-2">
                {isES ? "Ilustración · precios normalizados por litro" : "Illustration · prices normalized per liter"}
              </p>
            </div>
            {benefits.map((b) => (
              <div key={b.text} className="flex items-start gap-3">
                <span className="text-sm shrink-0 mt-0.5 font-mono text-[var(--cm-data)]">{b.icon}</span>
                <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
                  {b.text}
                </p>
              </div>
            ))}

            <div className="rounded-xl border border-[var(--cm-mint)]/35 bg-[var(--cm-mint)]/5 p-5 space-y-3">
              <p className="text-xs font-semibold text-[var(--cm-mint)] uppercase tracking-wider">
                {isES ? "Hoy en Build" : "Available in Build today"}
              </p>
              <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
                {isES
                  ? "Intel MCP y export ya están en planes Build: Starter ($9/mes) para export CSV/JSON; Pro ($49/mes) para checkout retail, alertas y el bundle intel completo."
                  : "Intel MCP and export are already on Build plans: Starter ($9/mo) for CSV/JSON export; Pro ($49/mo) for retail checkout, alerts, and the full intel bundle."}
              </p>
              <div className="flex flex-wrap gap-3">
                <a href="/#pricing" className="btn-mint text-xs px-4 py-2">
                  {isES ? "Ver Build →" : "See Build →"}
                </a>
                <a
                  href="/docs#intel"
                  className="text-xs font-mono text-[var(--cm-mint)] hover:underline self-center"
                >
                  {isES ? "Docs market intel →" : "market intel docs →"}
                </a>
              </div>
            </div>

            <div className="mt-8 rounded-xl border border-[var(--cm-outline-variant)]/30 p-5 space-y-3">
              <p className="text-xs font-semibold text-[var(--cm-on-surface-variant)]/60 uppercase tracking-wider mb-3">
                {isES ? "vs. el status quo" : "vs. the status quo"}
              </p>
              {(isES ? [
                ["×", "IPC oficial — 30 días de retraso"],
                ["×", "Encuestas de campo — costosas y puntuales"],
                ["×", "Scraping propio — frágil, legal gray zone"],
                ["✓", `CLI Market Intelligence — 4h refresh, APIs públicas de catálogo`],
              ] : [
                ["×", "Official CPI — 30-day lag"],
                ["×", "Field price surveys — expensive and one-off"],
                ["×", "In-house scraping — fragile, legal gray zone"],
                ["✓", `CLI Market Intelligence — 4h refresh, public catalog APIs`],
              ]).map(([icon, text]) => (
                <div key={text} className="flex items-start gap-2">
                  <span className="text-sm shrink-0 font-mono">{icon}</span>
                  <p className={`text-sm ${icon === "✓" ? "text-[var(--cm-mint)] font-medium" : "text-[var(--cm-on-surface-variant)]/60 line-through"}`}>
                    {text}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div id="contact-intelligence" className="card-cyber p-6 sm:p-8 scroll-mt-24">
            {sent ? (
              <div className="text-center py-6 space-y-3">
                <p className="text-2xl">✅</p>
                <p className="text-base font-semibold text-white">
                  {isES ? "¡Anotado!" : "You're on the list!"}
                </p>
                <p className="text-sm text-[var(--cm-on-surface-variant)]">
                  {isES
                    ? `Te escribiremos a ${email} cuando abramos el acceso.`
                    : `We'll reach out to ${email} when we open access.`}
                </p>
              </div>
            ) : (
              <form onSubmit={submit} className="space-y-5">
                <div>
                  <p className="text-xs font-label-caps text-[var(--cm-on-surface-variant)]/60 mb-1">
                    Intelligence
                  </p>
                  <h3 className="text-lg font-bold text-white">
                    {isES ? "Únete a la lista de espera" : "Join the waitlist"}
                  </h3>
                  <p className="text-sm text-[var(--cm-on-surface-variant)] mt-1">
                    {isES
                      ? "Acceso anticipado para equipos comerciales. Sin costo hasta el lanzamiento."
                      : "Early access for commercial teams. No cost until launch."}
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-white mb-1">
                    Email *
                  </label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="input-cyber"
                    placeholder="tu@empresa.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-white mb-1">
                    {isES ? "¿Cuál es tu rol?" : "What's your role?"}{" "}
                    <span className="text-[var(--cm-on-surface-variant)] font-normal">
                      ({isES ? "opcional" : "optional"})
                    </span>
                  </label>
                  <input
                    type="text"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="input-cyber"
                    placeholder={isES ? "Ej. Gerente de Pricing, CPG S.A." : "e.g. Pricing Manager, CPG Co."}
                  />
                </div>

                <LegalConsentCheckbox checked={legal} onChange={setLegal} />

                {error && <p className="text-sm text-[#ffb4ab]">{error}</p>}

                <button
                  type="submit"
                  disabled={loading || !legal}
                  className="btn-mint w-full disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading
                    ? isES ? "Enviando…" : "Sending…"
                    : isES ? "Notifícame al lanzar →" : "Notify me at launch →"}
                </button>

                <p className="text-xs text-center text-[var(--cm-on-surface-variant)]/60">
                  {isES
                    ? "Sin spam. Solo el aviso de lanzamiento."
                    : "No spam. Just the launch notification."}
                </p>
              </form>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}