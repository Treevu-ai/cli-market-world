"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { recordPipInstallIntent } from "@/lib/funnel";
import { PRICING_BUILD_HASH } from "@/lib/siteNav";

export default function Hero() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);

  const proofChips = [
    {
      label: isES
        ? `${MARKET_STATS.retailersVerified} retailers verificados`
        : `${MARKET_STATS.retailersVerified} verified retailers`,
    },
    {
      label: isES
        ? `${MARKET_STATS.pricesVerifiedLabel} precios normalizados`
        : `${MARKET_STATS.pricesVerifiedLabel} normalized prices`,
    },
    {
      label: isES
        ? `${MARKET_STATS.countries} países LATAM`
        : `${MARKET_STATS.countries} LATAM countries`,
    },
    {
      label: isES
        ? `Refresh cada ${MARKET_STATS.pricesRefreshHours}h`
        : `${MARKET_STATS.pricesRefreshHours}h refresh cycle`,
    },
  ];

  return (
    <section
      id="hero"
      className="landing-section animate-fade-in relative min-h-0 md:min-h-[88vh] flex flex-col overflow-hidden hero-stripe-mesh"
      style={{ borderBottom: "1px solid #27272A" }}
    >
      <div className="flex-1 flex flex-col justify-center landing-container-wide pt-14 pb-10 sm:pt-20 sm:pb-20 lg:pt-24 lg:pb-28 min-w-0 relative z-10">

        <div className="max-w-[860px]">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="mb-6 stripe-tag-soft inline-flex"
          >
            {isES ? "COST-OF-LIVING OS PARA LATAM" : "COST-OF-LIVING OS FOR LATAM"}
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="hero-garamond-headline"
          >
            {isES
              ? "Optimiza tu compra en una llamada — para toda LatAm"
              : "Optimize your purchase in one call — across all of LatAm"}
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
            className="mt-5 text-base sm:text-lg max-w-[620px] leading-relaxed stripe-body"
          >
            {isES ? (
              <>
                <code className="text-[#7CFF5B] font-mono text-sm">market optimize</code> compara toda la canasta entre 41 retailers, calcula TCO, sugiere sustitutos con ahorro y genera links de acción — una sola llamada. Checkout vía Yape, Plin o PayPal: orden interna CLI Market, no compra directa en Wong ni Rappi. 63,000+ precios verificados, actualizados cada 4h.
              </>
            ) : (
              <>
                <code className="text-[#7CFF5B] font-mono text-sm">market optimize</code> compares your full basket across 41 retailers, calculates TCO, suggests substitutes with savings, and generates action links — one call. Checkout via Yape, Plin, or PayPal: internal CLI Market order, not direct checkout on Wong or Rappi. 63,000+ verified prices, refreshed every 4h.
              </>
            )}
          </motion.p>

          {mounted && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.18 }}
              className="mt-6 flex flex-wrap gap-2"
            >
              {proofChips.map((chip, i) => (
                <span
                  key={i}
                  className="text-xs font-mono text-[#A1A1AA] bg-[#18181B] border border-[#27272A] rounded-full px-3 py-1"
                >
                  {chip.label}
                </span>
              ))}
            </motion.div>
          )}

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.22 }}
            className="mt-4 text-sm text-[#A1A1AA] max-w-[580px]"
          >
            {isES
              ? `La plataforma más completa para comercio agéntico en LATAM — API, CLI, herramientas MCP y flujos de compra empresarial.`
              : `Powered by the most complete toolkit for agentic commerce in LATAM — API, CLI, MCP tools, and procurement workflows.`}
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mt-8 flex flex-wrap gap-3"
          >
            <a
              href={PRICING_BUILD_HASH}
              onClick={() => recordPipInstallIntent("landing_hero")}
              className="inline-flex items-center rounded-[10px] bg-[#7CFF5B] text-[#09090B] text-base font-semibold px-6 py-2.5 hover:bg-[#8fff6e] active:bg-[#5be041] transition-colors"
            >
              {isES ? "Obtener API Key →" : "Get API Key →"}
            </a>
            <a
              href="/contact"
              className="inline-flex items-center rounded-[10px] border border-[#27272A] text-[#FAFAFA] text-base font-normal px-6 py-2.5 hover:border-[#7CFF5B] hover:text-[#7CFF5B] transition-colors bg-transparent"
            >
              {isES ? "Ver Demo →" : "Watch Demo →"}
            </a>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.42 }}
          className="mt-10 max-w-[480px]"
        >
          <div
            className="rounded-xl p-5 font-mono text-sm leading-relaxed"
            style={{ background: "#0d1117", color: "#8b949e" }}
          >
            <div style={{ color: "#57c453" }}>
              $ market optimize &quot;leche, arroz, aceite&quot; --country PE
            </div>
            <div className="mt-3" style={{ color: "#8b949e" }}>
              {isES ? "Mejor opción:" : "Best option:"}
            </div>
            <div className="mt-1 pl-2">
              <span style={{ color: "#e6edf3" }}>Metro PE</span>
              <span style={{ color: "#3fb950" }}>{"      S/ 18.40"}</span>
            </div>
            <div className="pl-2">
              <span style={{ color: "#e6edf3" }}>{isES ? "Sustituto" : "Substitute"}</span>
              <span style={{ color: "#3fb950" }}>{"   Tottus S/ 17.80 ↓"}</span>
            </div>
            <div className="mt-3" style={{ color: "#8b949e" }}>
              {isES ? "TCO calculado · Link Yape generado" : "TCO calculated · Yape link ready"}
            </div>
          </div>
        </motion.div>

      </div>
    </section>
  );
}
