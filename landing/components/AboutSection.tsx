"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function AboutSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="about" className="landing-section landing-section-alt animate-fade-in">
      <div className="landing-container-wide text-center">
        <p className="section-eyebrow mb-4 text-[var(--cm-mint)]">{isES ? "Sobre nosotros" : "About us"}</p>
        <h2 className="font-display text-[clamp(2rem,5vw,3rem)] leading-[1.1] font-bold text-[var(--cm-mint)] mb-6 tracking-tight">
          {isES ? (
            <>
              Construido en Perú.
              <br />
              Operando en {MARKET_STATS.countries} países.
            </>
          ) : (
            <>
              Built in Peru.
              <br />
              Operating in {MARKET_STATS.countries} countries.
            </>
          )}
        </h2>

        <div className="text-base text-[var(--cm-on-surface-variant)] max-w-lg mx-auto mb-12 leading-relaxed space-y-4">
          <p>
            {isES ? (
              <>
                CLI Market es un producto de Sinapsis Innovadora S.A.C. Construimos la capa programable del retail
                físico de LatAm: una sola API sobre {MARKET_STATS.retailersVerified} retailers verificados en{" "}
                {MARKET_STATS.countries} países, con {MARKET_STATS.pricesVerifiedLabel} precios de góndola normalizados
                por kg/L y refrescados cada {MARKET_STATS.pricesRefreshHours} horas.
              </>
            ) : (
              <>
                CLI Market is a product of Sinapsis Innovadora S.A.C. We build the programmable layer for LatAm
                physical retail: one API across {MARKET_STATS.retailersVerified} verified retailers in{" "}
                {MARKET_STATS.countries} countries, with {MARKET_STATS.pricesVerifiedLabel} shelf prices normalized per
                kg/L and refreshed every {MARKET_STATS.pricesRefreshHours} hours.
              </>
            )}
          </p>
          <p>
            {isES ? (
              <>
                Donde antes había scraping frágil y datos con semanas de retraso, entregamos precios verificados como
                infraestructura — para equipos de pricing que necesitan spreads e inflación, y para builders que
                integran agentes de IA.
              </>
            ) : (
              <>
                Where fragile scraping and weeks-old data used to be the norm, we deliver verified prices as
                infrastructure — for pricing teams that need spreads and inflation, and for builders integrating AI
                agents.
              </>
            )}
          </p>
          <p className="text-white font-medium">
            {isES ? "Un solo moat de datos, dos productos: Intelligence y Build." : "One data moat, two products: Intelligence and Build."}
          </p>
        </div>

        <div className="card-cyber energy-border-active p-6 sm:p-8 w-full max-w-sm mx-auto min-w-0 overflow-hidden">
          <div className="flex flex-col items-center gap-4 text-center">
            <img
              src="/grok-image-b03d62b8-7a6d-4610-82f0-1475243924d3.png"
              alt={isES ? "Ricardo Cuba, founder de CLI Market" : "Ricardo Cuba, founder of CLI Market"}
              className="w-20 h-20 rounded-full object-cover shrink-0 ring-2 ring-[var(--cm-mint)]/40"
            />
            <div className="min-w-0 w-full space-y-1">
              <div className="inline-flex flex-wrap items-center justify-center gap-x-1.5 gap-y-1 max-w-full">
                <h3 className="text-lg font-bold text-white leading-tight">Ricardo Cuba</h3>
                <svg width="18" height="18" viewBox="0 0 22 22" fill="#1d9bf0" aria-hidden="true" className="shrink-0">
                  <title>Verified</title>
                  <path d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.854-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.706-1.443 1.248-.355.54-.553 1.17-.57 1.814.018.645.216 1.273.57 1.814.356.54.856.97 1.444 1.242-.224.607-.274 1.263-.144 1.894.13.633.436 1.22.882 1.692.47.445 1.053.75 1.687.882.633.13 1.29.08 1.9-.14.27.586.702 1.084 1.24 1.438.54.355 1.168.55 1.815.568.646-.018 1.273-.216 1.814-.57.543-.354.974-.852 1.245-1.44.608.22 1.26.27 1.89.14.633-.13 1.22-.436 1.692-.882.446-.47.75-1.055.88-1.688.13-.634.085-1.293-.14-1.896.586-.274 1.084-.706 1.44-1.248.355-.54.55-1.17.567-1.814zM9.78 15.67l-3.39-3.39 1.41-1.41 1.98 1.98 4.6-4.6 1.41 1.41-6.01 6.01z"/>
                </svg>
              </div>
              <p className="text-sm text-[var(--cm-on-surface-variant)] leading-snug">Founder &amp; Product Owner</p>
              <p className="text-sm font-medium text-white leading-snug">CLI Market</p>
              <p className="pt-1 text-xs text-[var(--cm-on-surface-variant)] leading-relaxed">
                {isES ? "Gerente General" : "General Manager"}
                <br />
                <span className="text-[var(--cm-mint)]/80">SINAPSIS INNOVADORA S.A.C. · RUC 20613045563</span>
              </p>
            </div>
          </div>

          <div className="mt-5 pt-4 border-t border-[var(--cm-outline-variant)]/30 grid grid-cols-1 gap-2">
            {[
              { href: "https://instagram.com/cli.market", label: "Instagram", icon: "instagram" },
              { href: "https://x.com/cli_market_dev", label: "X / Twitter", icon: "x" },
              { href: "https://www.linkedin.com/company/cli-market/", label: "LinkedIn", icon: "linkedin" },
            ].map(({ href, label }) => (
              <a
                key={href}
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex w-full items-center justify-center gap-2 rounded border border-[var(--cm-outline-variant)]/40 px-4 py-2.5 text-xs font-medium text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] hover:border-[var(--cm-mint)]/40 transition-colors"
              >
                {label}
              </a>
            ))}
          </div>
        </div>

        <p className="mt-6 font-mono text-xs text-[var(--cm-on-surface-variant)]/70">
          {isES
            ? "Sinapsis Innovadora S.A.C. · RUC 20613045563 · Lima, Perú · Infraestructura para agentes."
            : "Sinapsis Innovadora S.A.C. · Peru · Infrastructure for agents."}
        </p>

        <div className="mt-10">
          <a href="#contact" className="btn-mint cyber-glow-mint">
            {isES ? "Trabajemos juntos →" : "Let's work together →"}
          </a>
        </div>
      </div>
    </section>
  );
}
