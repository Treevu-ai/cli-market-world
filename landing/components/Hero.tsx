"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import ScrambleText from "@/components/ScrambleText";
import HeroPlayground from "@/components/HeroPlayground";
import HeroMetrics from "@/components/HeroMetrics";
import HeroPathCard from "@/components/HeroPathCard";
import { MARKET_STATS } from "@/lib/marketStats";
import { useLiveStats } from "@/hooks/useLiveStats";
import { recordPipInstallIntent } from "@/lib/funnel";
import { RETAILERS_PAGE, PRICING_BUILD_HASH } from "@/lib/siteNav";

export default function Hero() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { pypiChip } = useLiveStats();
  const [pathsOpen, setPathsOpen] = useState(false);

  return (
    <section
      id="hero"
      className="brand-mode-terminal hero-terminal landing-section animate-fade-in relative min-h-0 md:min-h-[88vh] flex flex-col overflow-hidden"
    >
      <div className="hero-terminal-grid absolute inset-0 pointer-events-none" aria-hidden="true" />
      <div className="hero-terminal-glow absolute inset-0 pointer-events-none" aria-hidden="true" />

      <div className="flex-1 flex flex-col justify-center items-center landing-container-wide pt-14 pb-10 sm:pt-20 sm:pb-20 lg:pt-24 lg:pb-28 text-center min-w-0 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="mb-4 inline-flex items-center gap-2 rounded-full border border-[var(--cm-data)]/30 bg-[var(--cm-data)]/8 px-3 py-1"
        >
          <span className="h-1.5 w-1.5 rounded-full bg-[var(--cm-data)] animate-pulse" aria-hidden="true" />
          <span className="text-[10px] font-mono uppercase tracking-widest text-[var(--cm-data)]">
            {isES ? "Capa de comercio para agentes de IA · LATAM" : "Commerce layer for AI agents · LATAM"}
          </span>
        </motion.div>

        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.05 }}
          className="hero-terminal-eyebrow mb-4"
        >
          CLI MARKET
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="hero-terminal-headline text-balance max-w-[820px]"
        >
          {isES ? (
            <>
              Obtén precios reales de góndola de {MARKET_STATS.retailersVerified} retailers en{" "}
              {MARKET_STATS.countries} países.
            </>
          ) : (
            <>
              Get real shelf prices from {MARKET_STATS.retailersVerified} retailers across{" "}
              {MARKET_STATS.countries} countries.
            </>
          )}
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
          className="hero-api-punch mt-5 sm:mt-6"
        >
          <ScrambleText
            text={isES ? "Una sola API" : "One API"}
            autoStart
            delay={550}
            duration={0.75}
          />
        </motion.p>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.18, ease: "easeOut" }}
          className="mt-5 text-base sm:text-lg text-[var(--cm-ink)] max-w-[640px] font-medium leading-relaxed"
        >
          {isES ? (
            <>
              La primera capa de inteligencia de precios para LatAm. Disponible vía API, CLI y MCP
              — ahora visible en claude.ai, ChatGPT y Cursor.
            </>
          ) : (
            <>
              The first shelf-price intelligence layer for LatAm. Available via API, CLI, and MCP
              — now discoverable in claude.ai, ChatGPT, and Cursor.
            </>
          )}
        </motion.p>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.12, ease: "easeOut" }}
          className="hero-terminal-subhead mt-3 max-w-[640px] text-sm"
        >
          {isES
            ? `Precios normalizados por kg/L · refresh cada ${MARKET_STATS.pricesRefreshHours}h.`
            : `Prices normalized per kg/L · refresh every ${MARKET_STATS.pricesRefreshHours}h.`}{" "}
          <a href="#coverage" className="text-[var(--cm-data)] underline underline-offset-2 hover:brightness-110">
            {isES ? "Cobertura →" : "Coverage →"}
          </a>
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-8 sm:mt-12 w-full"
        >
          <HeroMetrics />
        </motion.div>

        <a
          href="#story"
          className="mt-5 inline-flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-[var(--cm-data)] hover:brightness-110 transition-colors"
        >
          {isES ? "Ver historia góndola → agente ↓" : "See shelf → agent story ↓"}
        </a>

        <p className="mt-6 text-[10px] font-mono uppercase tracking-widest text-[var(--cm-on-surface-variant)]/60 hidden sm:block">
          {isES ? "Elige tu camino" : "Choose your path"}
        </p>

        <div className="mt-4 hidden sm:grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 w-full landing-content-rail items-stretch">
          <HeroPathCard
            href={PRICING_BUILD_HASH}
            variant="primary"
            onClick={() => recordPipInstallIntent("landing_hero")}
            eyebrow={isES ? "Para developers · Build" : "For developers · Build"}
            title={isES ? "Empezar con la API — gratis →" : "Start with the API — free →"}
            body={
              <>
                <code className="font-mono text-xs text-[var(--cm-on-mint)]/85 break-all leading-relaxed">
                  {MARKET_STATS.pipInstallCmd}
                </code>
                {pypiChip ? (
                  <span className="text-[10px] font-mono text-[var(--cm-on-mint)]/65 tabular-nums">
                    <span className="font-semibold text-[var(--cm-on-mint)]/80">{pypiChip}</span>{" "}
                    {isES ? "instalaciones PyPI" : "PyPI installs"}
                  </span>
                ) : (
                  <span className="text-xs text-[var(--cm-on-mint)]/55">
                    {isES ? "MIT · sin tarjeta" : "MIT · no card required"}
                  </span>
                )}
              </>
            }
            foot={`API · CLI · ${MARKET_STATS.mcpTools} API tools`}
          />

          <HeroPathCard
            href="#intelligence"
            variant="signal"
            eyebrow={isES ? "Para equipos comerciales · Intelligence" : "For commercial teams · Intelligence"}
            title={isES ? "Spreads e inflación desde góndola →" : "Shelf spreads & inflation →"}
            body={
              <>
                <span className="text-xs font-mono text-[var(--cm-signal)]/90 tabular-nums">
                  {MARKET_STATS.indicatorsCount} {isES ? "datos" : "data points"}
                  {MARKET_STATS.goldenLinkagePct > 0
                    ? ` · ${MARKET_STATS.goldenLinkagePct}% ${isES ? "linkage" : "linkage"}`
                    : ""}
                </span>
                <span className="text-xs text-[var(--cm-text-secondary)]">
                  {isES ? "Lista de espera · Q3 2026" : "Waitlist · Q3 2026"}
                </span>
              </>
            }
            foot={isES ? "Spreads · canastas · inflación API" : "Spreads · baskets · inflation API"}
          />

          <HeroPathCard
            href={RETAILERS_PAGE}
            variant="default"
            eyebrow={isES ? "Para retailers · Partner" : "For retailers · Partner"}
            title={isES ? "Tu góndola, visible — gratis →" : "Your shelf, visible — free →"}
            body={
              <>
                <span className="text-xs font-mono text-[var(--cm-ink)]/90 tabular-nums">
                  {MARKET_STATS.retailersVerified} {isES ? "retailers verificados" : "verified retailers"}
                </span>
                <span className="text-xs text-[var(--cm-text-secondary)]">
                  {isES ? "30 segundos · sin código" : "30 seconds · no code"}
                </span>
              </>
            }
            foot={isES ? MARKET_STATS.platformsPhraseEs : MARKET_STATS.platformsPhraseEn}
          />
        </div>

        <div className="mt-4 w-full landing-content-rail sm:hidden grid gap-2">
          <HeroPathCard
            href={PRICING_BUILD_HASH}
            variant="primary"
            onClick={() => recordPipInstallIntent("landing_hero")}
            eyebrow={isES ? "Para developers · Build" : "For developers · Build"}
            title={isES ? "Empezar con la API — gratis →" : "Start with the API — free →"}
            body={
              <code className="font-mono text-xs text-[var(--cm-on-mint)]/85 break-all">
                {MARKET_STATS.pipInstallCmd}
              </code>
            }
            foot={`API · CLI · ${MARKET_STATS.mcpTools} API tools`}
          />
          <button
            type="button"
            onClick={() => setPathsOpen((v) => !v)}
            className="w-full text-xs font-mono text-[var(--cm-on-surface-variant)] py-2"
            aria-expanded={pathsOpen}
          >
            {pathsOpen
              ? isES
                ? "Ocultar otros caminos ▲"
                : "Hide other paths ▲"
              : isES
                ? "Intelligence · Retailers ▼"
                : "Intelligence · Retailers ▼"}
          </button>
          {pathsOpen ? (
            <div className="grid grid-cols-1 gap-2">
              <HeroPathCard
                href="#intelligence"
                variant="signal"
                eyebrow={isES ? "Para equipos comerciales · Intelligence" : "For commercial teams · Intelligence"}
                title={isES ? "Spreads e inflación →" : "Spreads & inflation →"}
                body={
                  <span className="text-xs text-[var(--cm-text-secondary)]">
                    {MARKET_STATS.indicatorsCount} {isES ? "datos · Q3 2026" : "data points · Q3 2026"}
                  </span>
                }
                foot={isES ? "Spreads · canastas · inflación API" : "Spreads · baskets · inflation API"}
              />
              <HeroPathCard
                href={RETAILERS_PAGE}
                variant="default"
                eyebrow={isES ? "Para retailers · Partner" : "For retailers · Partner"}
                title={isES ? "Tu góndola, visible →" : "Your shelf, visible →"}
                body={
                  <span className="text-xs text-[var(--cm-text-secondary)]">
                    {isES ? "30 segundos · sin código" : "30 seconds · no code"}
                  </span>
                }
                foot={isES ? MARKET_STATS.platformsPhraseEs : MARKET_STATS.platformsPhraseEn}
              />
            </div>
          ) : null}
        </div>

        <div id="hero-playground" className="hidden md:block w-full scroll-mt-24">
          <HeroPlayground />
        </div>
      </div>
    </section>
  );
}
