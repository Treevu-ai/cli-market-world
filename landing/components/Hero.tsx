"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { recordPipInstallIntent } from "@/lib/funnel";
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
      style={{ borderBottom: "1px solid #e2e8f0" }}
    >
      <div className="landing-container-wide pt-16 pb-10 sm:pt-20 sm:pb-14 relative z-10">
        <div className="flex flex-col lg:flex-row lg:items-center lg:gap-12 xl:gap-16">

          {/* Left — copy */}
          <div className="flex-1 min-w-0">
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="mb-4 stripe-tag-soft inline-flex"
            >
              {isES ? "COST-OF-LIVING OS PARA LATAM" : "COST-OF-LIVING OS FOR LATAM"}
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="hero-garamond-headline"
            >
              {isES ? (
                <>Optimiza tu compra en una llamada —{" "}<br className="hidden sm:block" />para toda <span className="text-gradient-orange">LatAm</span></>
              ) : (
                <>Optimize your purchase in one call —{" "}<br className="hidden sm:block" />across all of <span className="text-gradient-orange">LatAm</span></>
              )}
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
              className="mt-4 text-base sm:text-lg max-w-[500px] leading-relaxed stripe-body"
            >
              {isES
                ? "Busca, compara y ejecuta compras en 40 retailers verificados de LATAM — en segundos, con aprobaciones integradas."
                : "Search, compare, and execute purchases across 40 verified LATAM retailers — in seconds, with built-in approvals."}
            </motion.p>

            {mounted && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.18 }}
                className="mt-4 flex flex-wrap gap-2"
                aria-hidden="true"
              >
                {proofChips.map((chip, i) => (
                  <span
                    key={i}
                    className="text-xs font-mono text-[#64748b] bg-[#f1f5f9] border border-[#e2e8f0] rounded-full px-3 py-1"
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
              className="mt-6 flex flex-wrap gap-3"
            >
              <a
                href={CTA.getApiKey.href}
                onClick={() => recordPipInstallIntent("landing_hero")}
                className="btn-mint text-base px-6 py-2.5"
              >
                {isES ? CTA.getApiKey.es : CTA.getApiKey.en}
              </a>
              <a
                href={CTA.watchDemo.href}
                className="btn-outline text-base px-6 py-2.5"
              >
                {isES ? CTA.watchDemo.es : CTA.watchDemo.en}
              </a>
            </motion.div>
          </div>

          {/* Right — terminal (desktop only) */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.32 }}
            className="hidden lg:block mt-10 lg:mt-0 lg:shrink-0 lg:w-[440px] xl:w-[480px]"
          >
            <div className="rounded-xl overflow-hidden border border-[#30363d]" style={{ background: "#0d1117" }}>
              {/* Title bar */}
              <div className="flex items-center gap-2 px-4 py-2.5 border-b border-[#21262d]" style={{ background: "#161b22" }}>
                <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f57]" />
                <span className="w-2.5 h-2.5 rounded-full bg-[#febc2e]" />
                <span className="w-2.5 h-2.5 rounded-full bg-[#28c840]" />
                <span className="ml-3 text-xs text-[#484f58] font-mono">cli-market — bash</span>
              </div>

              {/* Terminal body */}
              <div className="p-4 font-mono text-xs leading-normal space-y-0.5">
                {/* Command */}
                <div>
                  <span style={{ color: "#3fb950" }}>❯</span>{" "}
                  <span style={{ color: "#e6edf3" }}>market optimize </span>
                  <span style={{ color: "#a5d6ff" }}>&quot;leche, arroz, aceite&quot;</span>{" "}
                  <span style={{ color: "#ff7b72" }}>--country</span>{" "}
                  <span style={{ color: "#ffa657" }}>PE</span>{" "}
                  <span style={{ color: "#ff7b72" }}>--stock</span>
                </div>

                <div style={{ color: "#484f58" }}>
                  {isES ? `▸ Escaneando ${MARKET_STATS.retailersVerified} retailers · verificando stock...` : `▸ Scanning ${MARKET_STATS.retailersVerified} retailers · checking stock...`}
                </div>

                <div className="pt-1" style={{ color: "#21262d" }}>{"─".repeat(44)}</div>

                {/* Column header */}
                <div className="flex justify-between text-xs pt-0.5">
                  <span style={{ color: "#8b949e" }}>{"  "}Retailer</span>
                  <div className="flex gap-5">
                    <span style={{ color: "#8b949e" }}>Stock</span>
                    <span style={{ color: "#8b949e" }}>Total (S/)</span>
                  </div>
                </div>

                {/* Winner */}
                <div className="flex justify-between items-center rounded px-1 py-0.5" style={{ background: "rgba(63,185,80,0.09)" }}>
                  <span><span style={{ color: "#3fb950" }}>★ </span><span style={{ color: "#e6edf3" }}>Tottus PE</span></span>
                  <div className="flex gap-5">
                    <span style={{ color: "#3fb950" }}>✓</span>
                    <span style={{ color: "#3fb950" }}>17.80</span>
                  </div>
                </div>

                <div className="flex justify-between px-1 py-0.5">
                  <span style={{ color: "#c9d1d9" }}>{"  "}Metro PE</span>
                  <div className="flex gap-5">
                    <span style={{ color: "#3fb950" }}>✓</span>
                    <span style={{ color: "#c9d1d9" }}>18.40</span>
                  </div>
                </div>

                <div className="flex justify-between px-1 py-0.5">
                  <span style={{ color: "#8b949e" }}>{"  "}Plaza Vea</span>
                  <div className="flex gap-5">
                    <span style={{ color: "#3fb950" }}>✓</span>
                    <span style={{ color: "#8b949e" }}>19.10</span>
                  </div>
                </div>

                <div className="flex justify-between px-1 py-0.5">
                  <span style={{ color: "#8b949e" }}>{"  "}Wong PE</span>
                  <div className="flex gap-5">
                    <span style={{ color: "#e3b341" }}>~</span>
                    <span style={{ color: "#8b949e" }}>19.85</span>
                  </div>
                </div>

                <div className="flex justify-between px-1 py-0.5">
                  <span style={{ color: "#6e7681" }}>{"  "}Rappi PE</span>
                  <div className="flex gap-5">
                    <span style={{ color: "#3fb950" }}>✓</span>
                    <span style={{ color: "#6e7681" }}>21.50</span>
                  </div>
                </div>

                <div className="pt-1" style={{ color: "#21262d" }}>{"─".repeat(44)}</div>

                <div className="flex justify-between pt-0.5">
                  <span style={{ color: "#8b949e" }}>
                    {"  "}{isES ? "Ahorro vs. promedio" : "Savings vs. avg"}
                  </span>
                  <span style={{ color: "#3fb950" }}>↓ S/ 1.18 (6.2%)</span>
                </div>

                <div className="pt-1 space-y-0.5">
                  <div style={{ color: "#484f58" }}>
                    {"  "}{isES ? "TCO calculado · sustitutos incluidos · entrega 2h" : "TCO calculated · substitutes included · 2h delivery"}
                  </div>
                  <div style={{ color: "#58a6ff" }}>
                    {"  "}{isES ? "→ Link Yape generado ✓" : "→ Yape payment link ready ✓"}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

        </div>
      </div>
    </section>
  );
}
