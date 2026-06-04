"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { API_URL } from "@/lib/api";

const BENEFITS_ES = [
  { icon: "⚡", text: `${MARKET_STATS.pricesVerifiedLabel} precios de góndola actualizados cada ${MARKET_STATS.pricesRefreshHours}h — no estimaciones con 30 días de retraso` },
  { icon: "📐", text: "Precios normalizados por kg/L para comparar categorías entre cadenas y países" },
  { icon: "📊", text: `${MARKET_STATS.indicatorsCount} indicadores de mercado: spread entre cadenas, inflación real, tendencias históricas` },
  { icon: "🌎", text: `${MARKET_STATS.retailersVerified} retailers verificados en ${MARKET_STATS.countries} países — sin scraping, APIs públicas de catálogo` },
];

const BENEFITS_EN = [
  { icon: "⚡", text: `${MARKET_STATS.pricesVerifiedLabel} shelf prices refreshed every ${MARKET_STATS.pricesRefreshHours}h — not 30-day-lagged estimates` },
  { icon: "📐", text: "Prices normalized per kg/L to compare categories across chains and countries" },
  { icon: "📊", text: `${MARKET_STATS.indicatorsCount} market indicators: chain spread, real inflation, historical trends` },
  { icon: "🌎", text: `${MARKET_STATS.retailersVerified} verified retailers across ${MARKET_STATS.countries} countries — no scraping, public catalog APIs` },
];

export default function IntelligenceSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  const [email, setEmail] = useState("");
  const [role, setRole] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const benefits = isES ? BENEFITS_ES : BENEFITS_EN;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.includes("@")) {
      setError(isES ? "Email inválido" : "Invalid email");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await fetch(`${API_URL}/v1/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          plan: "intelligence",
          email,
          use_case: role ? `waitlist · role=${role}` : "waitlist",
          lang: isES ? "es" : "en",
        }),
      });
    } catch {
      // Never block the user
    }
    setSent(true);
    setLoading(false);
  };

  return (
    <section
      id="intelligence"
      className="landing-section animate-fade-in scroll-mt-20"
    >
      <div className="landing-container-wide">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 mb-3">
            <p className="section-eyebrow text-[var(--cm-mint)]">Intelligence</p>
            <span className="text-xs font-semibold bg-[var(--cm-mint)]/15 text-[var(--cm-mint)] border border-[var(--cm-mint)]/30 px-2 py-0.5 rounded-full">
              {isES ? "Próximamente" : "Coming soon"}
            </span>
          </div>
          <h2 className="section-title mb-3">
            {isES
              ? "Precios reales de góndola. No estimaciones de 30 días."
              : "Real shelf prices. Not 30-day estimates."}
          </h2>
          <p className="text-sm text-[var(--cm-on-surface-variant)] max-w-xl mx-auto">
            {isES
              ? "Para equipos de pricing, trade marketing y análisis en CPG, retail y fintech."
              : "For pricing, trade marketing, and analytics teams in CPG, retail, and fintech."}
          </p>
        </div>

        {/* Two-column: benefits + form */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto items-start">

          {/* Benefits */}
          <div className="space-y-4">
            {benefits.map((b) => (
              <div key={b.icon} className="flex items-start gap-3">
                <span className="text-xl shrink-0 mt-0.5">{b.icon}</span>
                <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
                  {b.text}
                </p>
              </div>
            ))}

            {/* Pain contrast */}
            <div className="mt-6 rounded-xl border border-[var(--cm-outline-variant)]/30 p-4 space-y-2">
              <p className="text-xs font-semibold text-[var(--cm-on-surface-variant)]/60 uppercase tracking-wider mb-3">
                {isES ? "vs. el status quo" : "vs. the status quo"}
              </p>
              {(isES ? [
                ["❌", "IPC oficial — 30 días de retraso"],
                ["❌", "Encuestas de campo — costosas y puntuales"],
                ["❌", "Scraping propio — frágil, legal gray zone"],
                ["✅", "CLI Market Intelligence — 4h, 45k+ precios, APIs públicas"],
              ] : [
                ["❌", "Official CPI — 30-day lag"],
                ["❌", "Field price surveys — expensive and one-off"],
                ["❌", "In-house scraping — fragile, legal gray zone"],
                ["✅", "CLI Market Intelligence — 4h, 45k+ prices, public APIs"],
              ]).map(([icon, text]) => (
                <div key={text} className="flex items-start gap-2">
                  <span className="text-sm shrink-0">{icon}</span>
                  <p className={`text-sm ${icon === "✅" ? "text-[var(--cm-mint)] font-medium" : "text-[var(--cm-on-surface-variant)]/60 line-through"}`}>
                    {text}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Waitlist form */}
          <div className="card-cyber p-6 sm:p-8">
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

                {error && <p className="text-sm text-[#ffb4ab]">{error}</p>}

                <button
                  type="submit"
                  disabled={loading}
                  className="btn-mint w-full disabled:opacity-50"
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
