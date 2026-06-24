"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { recordPipInstallIntent } from "@/lib/funnel";
import { PRICING_BUILD_HASH } from "@/lib/siteNav";
import { CTA } from "@/lib/ctaCopy";

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
      className="landing-section animate-fade-in relative overflow-hidden hero-stripe-mesh"
      style={{ borderBottom: "1px solid #27272A" }}
    >
      <div className="landing-container-wide pt-20 pb-16 sm:pt-24 sm:pb-20 relative z-10">
        <div className="flex flex-col lg:flex-row lg:items-center lg:gap-12 xl:gap-16">

          {/* Left column — copy */}
          <div className="flex-1 min-w-0">
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
              className="mt-5 text-base sm:text-lg max-w-[540px] leading-relaxed stripe-body"
            >
              {isES ? (
                <>
                  <code className="text-[#7CFF5B] font-mono text-sm">market optimize</code>{" "}
                  compara toda la canasta entre 41 retailers verificados, calcula TCO, sugiere sustitutos con ahorro y genera links de acción — una sola llamada.
                  <br /><br />
                  <span className="text-[#A1A1AA]">
                    Pago vía Yape, Plin o PayPal a través de una orden interna CLI Market —
                    no es checkout directo en Wong, Rappi ni Mercado Libre.
                  </span>
                </>
              ) : (
                <>
                  <code className="text-[#7CFF5B] font-mono text-sm">market optimize</code>{" "}
                  compares your full basket across 41 verified retailers, calculates TCO, suggests substitutes with savings, and generates action links — one call.
                  <br /><br />
                  <span className="text-[#A1A1AA]">
                    Payment via Yape, Plin, or PayPal through an internal CLI Market order —
                    not direct checkout on Wong, Rappi, or Mercado Libre.
                  </span>
                </>
              )}
            </motion.p>

            {mounted && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.18 }}
                className="mt-6 flex flex-wrap gap-2"
                aria-hidden="true"
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

            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.28 }}
              className="mt-8 flex flex-wrap gap-3"
            >
              <a
                href={CTA.getApiKey.href}
                onClick={() => recordPipInstallIntent("landing_hero")}
                className="inline-flex items-center rounded-[10px] bg-[#7CFF5B] text-[#09090B] text-base font-semibold px-6 py-2.5 hover:bg-[#8fff6e] active:bg-[#5be041] transition-colors"
              >
                {isES ? CTA.getApiKey.es : CTA.getApiKey.en}
              </a>
              <a
                href={CTA.watchDemo.href}
                className="inline-flex items-center rounded-[10px] border border-[#27272A] text-[#FAFAFA] text-base font-normal px-6 py-2.5 hover:border-[#7CFF5B] hover:text-[#7CFF5B] transition-colors bg-transparent"
              >
                {isES ? CTA.watchDemo.es : CTA.watchDemo.en}
              </a>
            </motion.div>
          </div>

          {/* Right column — terminal */}
          <motion.div
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.32 }}
            className="mt-10 lg:mt-0 lg:shrink-0 lg:w-[420px] xl:w-[460px]"
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
      </div>
    </section>
  );
}
