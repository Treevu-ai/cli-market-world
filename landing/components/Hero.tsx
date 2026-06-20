"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import ScrambleText from "@/components/ScrambleText";
import HeroPathCard from "@/components/HeroPathCard";
import { MARKET_STATS } from "@/lib/marketStats";
import { useLiveStats } from "@/hooks/useLiveStats";
import { recordPipInstallIntent } from "@/lib/funnel";
import { RETAILERS_PAGE, PRICING_BUILD_HASH, PRICING_PROCURE_HASH } from "@/lib/siteNav";
import { formatFreeHeroChip } from "@/lib/buildPricingTiers";
import { procurePriceRangeLabel } from "@/lib/procurePlans";

export default function Hero() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { pypiChip } = useLiveStats();
  const [pathsOpen, setPathsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);

  return (
    <section
      id="hero"
      className="landing-section animate-fade-in relative min-h-0 md:min-h-[88vh] flex flex-col overflow-hidden bg-white"
      style={{ borderBottom: "1px solid #f3f4f6" }}
    >
      <div className="flex-1 flex flex-col justify-center items-center landing-container-wide pt-14 pb-10 sm:pt-20 sm:pb-20 lg:pt-24 lg:pb-28 text-center min-w-0 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="mb-4 inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1"
        >
          <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-pulse" aria-hidden="true" />
          <span className="text-[10px] font-mono uppercase tracking-widest text-indigo-600">
            {isES ? "Deja de comprar por WhatsApp · LATAM" : "Stop buying on WhatsApp · LATAM"}
          </span>
        </motion.div>

        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.05 }}
          className="hero-terminal-eyebrow mb-4 mt-2"
        >
          CLI MARKET
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="hero-garamond-headline text-balance max-w-[820px]"
        >
          {isES ? (
            <>Infraestructura de comercio para agentes de IA.</>
          ) : (
            <>Commerce infrastructure for AI agents.</>
          )}
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
          className="hero-api-punch mt-5 sm:mt-6"
        >
          <ScrambleText
            text={isES ? `${MARKET_STATS.retailersVerified} retailers. Una API.` : `${MARKET_STATS.retailersVerified} retailers. One API.`}
            autoStart
            delay={550}
            duration={0.75}
          />
        </motion.p>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.18, ease: "easeOut" }}
          className="mt-5 text-base sm:text-lg text-gray-600 max-w-[640px] font-medium leading-relaxed"
        >
          {isES ? (
            <>Tu agente busca, compara y compra en {MARKET_STATS.retailersVerified} retailers de {MARKET_STATS.countries} países. Sin scraping. Sin integraciones manuales.</>
          ) : (
            <>Your agent searches, compares, and buys across {MARKET_STATS.retailersVerified} retailers in {MARKET_STATS.countries} countries. Zero scraping. Zero manual integrations.</>
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
          <a href="#how-it-works" className="text-indigo-600 underline underline-offset-2 hover:text-indigo-700">
            {isES ? "Cómo funciona →" : "How it works →"}
          </a>
        </motion.p>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.22 }}
          className="mt-8 sm:mt-10 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-gray-400"
          aria-label={isES ? "Señales de tracción" : "Traction signals"}
        >
          {mounted && pypiChip && (
            <>
              <span className="tabular-nums">
                <span className="font-semibold text-gray-700">{pypiChip}</span>{" "}
                {isES ? "instalaciones PyPI" : "PyPI installs"}
              </span>
              <span className="hidden sm:inline text-gray-200" aria-hidden="true">|</span>
            </>
          )}
          <span>
            <span className="font-semibold text-gray-700">&lt;&nbsp;5&nbsp;min</span>{" "}
            {isES ? "de pip install a precios reales" : "from pip install to live prices"}
          </span>
          <span className="hidden sm:inline text-gray-200" aria-hidden="true">|</span>
          <span>
            <span className="font-semibold text-gray-700">{MARKET_STATS.countries}</span>{" "}
            {isES ? "países LATAM" : "LATAM countries"}
          </span>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.38 }}
          className="mt-5 flex flex-wrap justify-center gap-1.5 landing-content-rail"
          aria-label={isES ? "Muestra de retailers integrados" : "Sample of integrated retailers"}
        >
          {["Metro PE", "Wong PE", "Plaza Vea PE", "Carrefour AR", "Jumbo AR", "Chedraui MX", "HEB MX", "Éxito CO", "Falabella CL", "Ripley CL"].map((r) => (
            <span
              key={r}
              className="text-[11px] font-mono text-gray-400 bg-gray-50 border border-gray-200 rounded-full px-2.5 py-0.5"
            >
              {r}
            </span>
          ))}
          <span className="text-[11px] font-mono text-gray-300 px-1 py-0.5">
            +{MARKET_STATS.retailersVerified - 10} {isES ? "más →" : "more →"}
          </span>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.42 }}
          className="mt-8 flex justify-center gap-3"
        >
          <a
            href={PRICING_BUILD_HASH}
            className="inline-flex items-center rounded-full bg-indigo-600 text-white text-sm font-semibold px-6 py-3 hover:bg-indigo-700 transition-colors shadow-sm"
          >
            {isES ? "Sandbox gratis →" : "Free Sandbox →"}
          </a>
          <a
            href="#how-it-works"
            className="inline-flex items-center rounded-full bg-gray-100 text-gray-700 text-sm font-semibold px-6 py-3 hover:bg-gray-200 transition-colors"
          >
            {isES ? "Cómo funciona" : "How it works"}
          </a>
        </motion.div>

        <p className="mt-8 text-[10px] font-mono uppercase tracking-widest text-gray-400 hidden sm:block">
          {isES ? "Elige tu camino" : "Choose your path"}
        </p>

        <div className="mt-4 hidden sm:grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 w-full landing-content-rail items-stretch">
          <HeroPathCard
            href={PRICING_BUILD_HASH}
            variant="primary"
            onClick={() => recordPipInstallIntent("landing_hero")}
            eyebrow={isES ? "Para developers · API" : "For developers · API"}
            title={isES ? "Plan Free →" : "Free plan →"}
            body={
              <>
                <span className="text-xs text-white/90 leading-snug">
                  {isES
                    ? `${MARKET_STATS.retailersVerified} retailers · precios normalizados por kg/L`
                    : `${MARKET_STATS.retailersVerified} retailers · prices normalized per kg/L`}
                </span>
                {mounted && pypiChip ? (
                  <span className="text-[10px] font-mono text-white/70 tabular-nums">
                    <span className="font-semibold text-white/85">{pypiChip}</span>{" "}
                    {isES ? "instalaciones PyPI" : "PyPI installs"}
                  </span>
                ) : (
                  <span className="text-[10px] text-white/60">
                    {formatFreeHeroChip(isES)}
                  </span>
                )}
                <code className="font-mono text-[10px] text-white/50 break-all leading-relaxed">
                  {MARKET_STATS.pipInstallCmd}
                </code>
              </>
            }
            foot={`API · CLI · ${MARKET_STATS.mcpTools} API tools`}
          />

          <HeroPathCard
            href={PRICING_PROCURE_HASH}
            variant="signal"
            eyebrow={isES ? "Para equipos de compras · Procure" : "For procurement teams · Procure"}
            title={isES ? "Compra mejor. Más rápido →" : "Buy better. Faster →"}
            body={
              <>
                <span className="text-xs font-mono text-amber-700 tabular-nums">
                  {MARKET_STATS.retailersVerified} {isES ? "retailers · data-gate" : "retailers · data-gate"}
                </span>
                <span className="text-xs text-gray-500">
                  {procurePriceRangeLabel(isES)}
                </span>
              </>
            }
            foot={isES ? "Aprobaciones · ahorro · trazabilidad" : "Approvals · savings · audit trail"}
          />

          <HeroPathCard
            href={RETAILERS_PAGE}
            variant="default"
            eyebrow={isES ? "Para retailers · Partner" : "For retailers · Partner"}
            title={isES ? "Tu góndola, visible — gratis →" : "Your shelf, visible — free →"}
            body={
              <>
                <span className="text-xs font-mono text-gray-700 tabular-nums">
                  {MARKET_STATS.retailersVerified} {isES ? "retailers verificados" : "verified retailers"}
                </span>
                <span className="text-xs text-gray-500">
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
            eyebrow={isES ? "Para developers · API" : "For developers · API"}
            title={isES ? "Plan Free →" : "Free plan →"}
            body={
              <>
                <span className="text-xs text-white/90">
                  {isES
                    ? `${MARKET_STATS.retailersVerified} retailers · sin tarjeta`
                    : `${MARKET_STATS.retailersVerified} retailers · no card required`}
                </span>
                <code className="font-mono text-[10px] text-white/50 break-all">
                  {MARKET_STATS.pipInstallCmd}
                </code>
              </>
            }
            foot={`API · CLI · ${MARKET_STATS.mcpTools} API tools`}
          />
          <button
            type="button"
            onClick={() => setPathsOpen((v) => !v)}
            className="w-full text-xs font-mono text-gray-400 py-2"
            aria-expanded={pathsOpen}
          >
            {pathsOpen
              ? isES ? "Ocultar otros caminos ▲" : "Hide other paths ▲"
              : isES ? "Procure · Retailers ▼" : "Procure · Retailers ▼"}
          </button>
          {pathsOpen ? (
            <div className="grid grid-cols-1 gap-2">
              <HeroPathCard
                href={PRICING_PROCURE_HASH}
                variant="signal"
                eyebrow={isES ? "Para equipos de compras · Procure" : "For procurement teams · Procure"}
                title={isES ? "Compra mejor →" : "Buy better →"}
                body={
                  <span className="text-xs text-gray-500">
                    {procurePriceRangeLabel(isES)}
                  </span>
                }
                foot={isES ? "Aprobaciones · ahorro · trazabilidad" : "Approvals · savings · audit trail"}
              />
              <HeroPathCard
                href={RETAILERS_PAGE}
                variant="default"
                eyebrow={isES ? "Para retailers · Partner" : "For retailers · Partner"}
                title={isES ? "Tu góndola, visible →" : "Your shelf, visible →"}
                body={
                  <span className="text-xs text-gray-500">
                    {isES ? "30 segundos · sin código" : "30 seconds · no code"}
                  </span>
                }
                foot={isES ? MARKET_STATS.platformsPhraseEs : MARKET_STATS.platformsPhraseEn}
              />
            </div>
          ) : null}
        </div>

      </div>
    </section>
  );
}
