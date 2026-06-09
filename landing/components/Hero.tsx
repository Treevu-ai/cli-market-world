"use client";

import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import ScrambleText from "@/components/ScrambleText";
import HeroDemo from "@/components/HeroDemo";
import HeroMetrics from "@/components/HeroMetrics";
import { MARKET_STATS } from "@/lib/marketStats";
import { useLiveStats } from "@/hooks/useLiveStats";
import { recordPipInstallIntent } from "@/lib/funnel";
import { PRICING_LISTED_HASH, PRICING_BUILD_HASH } from "@/lib/siteNav";

export default function Hero() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { pypiChip } = useLiveStats();

  return (
    <section
      id="hero"
      className="brand-mode-terminal hero-terminal landing-section animate-fade-in relative min-h-0 md:min-h-[92vh] flex flex-col overflow-hidden"
    >
      <div className="hero-terminal-grid absolute inset-0 pointer-events-none" aria-hidden="true" />
      <div className="hero-terminal-glow absolute inset-0 pointer-events-none" aria-hidden="true" />

      <div className="flex-1 flex flex-col justify-center items-center landing-container pt-16 pb-16 sm:pt-20 sm:pb-20 lg:pt-24 lg:pb-28 text-center min-w-0 relative z-10">
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="hero-terminal-eyebrow mb-4"
        >
          CLI MARKET
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="hero-terminal-headline text-balance max-w-[720px]"
        >
          {isES ? (
            <>
              La primera capa de inteligencia de precios para LatAm.
              <br />
              <span className="text-[var(--cm-data)]">
                Obtén precios reales de góndola de {MARKET_STATS.retailersVerified} retailers en{" "}
                {MARKET_STATS.countries} países.
              </span>
              <br />
              Una sola API.
            </>
          ) : (
            <>
              The first shelf-price intelligence layer for LatAm.
              <br />
              <span className="text-[var(--cm-data)]">
                Get real shelf prices from {MARKET_STATS.retailersVerified} retailers across{" "}
                {MARKET_STATS.countries} countries.
              </span>
              <br />
              One API.
            </>
          )}
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.08, ease: "easeOut" }}
          className="mt-5 text-base sm:text-lg text-[var(--cm-ink)] max-w-[600px] font-medium"
        >
          {isES
            ? "Disponible vía API, CLI y MCP para agentes de IA."
            : "Available via API, CLI, and MCP for AI agents."}
        </motion.p>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.12, ease: "easeOut" }}
          className="hero-terminal-subhead mt-3 max-w-[640px] text-sm"
        >
          {isES
            ? `${MARKET_STATS.pricesVerifiedLabel} precios normalizados por kg/L · refresh cada ${MARKET_STATS.pricesRefreshHours}h.`
            : `${MARKET_STATS.pricesVerifiedLabel} prices normalized per kg/L · refresh every ${MARKET_STATS.pricesRefreshHours}h.`}{" "}
          <a href="#coverage" className="text-[var(--cm-data)] underline underline-offset-2 hover:brightness-110">
            {isES ? "Cobertura →" : "Coverage →"}
          </a>
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-10 sm:mt-12 w-full"
        >
          <HeroMetrics />
        </motion.div>

        <p className="mt-6 text-[10px] font-mono uppercase tracking-widest text-[var(--cm-on-surface-variant)]/60">
          {isES ? "Elige tu camino" : "Choose your path"}
        </p>

        <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 w-full max-w-[960px] mx-auto">
          <a
            href={PRICING_BUILD_HASH}
            onClick={() => recordPipInstallIntent("landing_hero")}
            className="btn-action hero-terminal-cta-primary group flex flex-col items-center gap-2 px-6 py-5 hover:scale-[1.02] transition-all duration-200 text-left sm:items-start shadow-[0_0_24px_rgba(200,255,0,0.15)]"
          >
            <span className="text-[10px] font-mono uppercase tracking-widest text-[var(--cm-on-mint)]/70">
              {isES ? "Para developers" : "For developers"} · Build
            </span>
            <span className="text-base font-semibold">
              <ScrambleText text={isES ? "Empezar con la API — gratis →" : "Start with the API — free →"} />
            </span>
            <code className="font-mono text-xs text-[var(--cm-on-mint)]/85">{MARKET_STATS.pipInstallCmd}</code>
            {pypiChip ? (
              <span className="text-[10px] font-mono text-[var(--cm-on-mint)]/65">
                {pypiChip} {isES ? "instalaciones PyPI" : "PyPI installs"}
              </span>
            ) : null}
            <span className="text-[10px] text-[var(--cm-on-mint)]/60">
              API · CLI · {MARKET_STATS.mcpTools} MCP tools
            </span>
          </a>

          <a
            href="#intelligence"
            className="hero-terminal-card group flex flex-col items-center gap-2 px-6 py-5 hover:scale-[1.02] transition-all duration-200 text-left sm:items-start ring-1 ring-[var(--cm-signal)]/25"
          >
            <span className="text-[10px] font-mono uppercase tracking-widest text-[var(--cm-signal)]/80">
              {isES ? "Para equipos comerciales" : "For commercial teams"} · Intelligence
            </span>
            <span className="text-base font-semibold text-[var(--cm-ink)]">
              {isES ? "Spreads e inflación desde góndola →" : "Shelf spreads & inflation →"}
            </span>
            <span className="text-xs text-[var(--cm-text-secondary)]">
              {isES ? `${MARKET_STATS.indicatorsCount} indicadores · lista de espera` : `${MARKET_STATS.indicatorsCount} indicators · waitlist`}
            </span>
          </a>

          <a
            href={PRICING_LISTED_HASH}
            className="hero-terminal-card group flex flex-col items-center gap-2 px-6 py-5 hover:scale-[1.02] transition-all duration-200 text-left sm:items-start"
          >
            <span className="text-[10px] font-mono uppercase tracking-widest text-[var(--cm-text-secondary)]">
              {isES ? "Para retailers" : "For retailers"} · Listed
            </span>
            <span className="text-base font-semibold text-[var(--cm-ink)]">
              {isES ? "Tu góndola, visible — gratis →" : "Your shelf, visible — free →"}
            </span>
            <span className="text-xs text-[var(--cm-text-secondary)]">
              {isES ? "30 segundos · sin código" : "30 seconds · no code"}
            </span>
          </a>
        </div>

        <HeroDemo />
      </div>
    </section>
  );
}
