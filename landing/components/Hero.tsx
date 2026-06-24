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
      style={{ borderBottom: "1px solid #27272A" }}
    >
      <div className="landing-container-wide pt-20 pb-16 sm:pt-24 sm:pb-20 relative z-10">
        <div className="flex flex-col lg:flex-row lg:items-center lg:gap-14 xl:gap-20">

          {/* Left — copy */}
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
              className="mt-5 text-base sm:text-lg max-w-[500px] leading-relaxed stripe-body"
            >
              {isES
                ? "API, CLI y herramientas MCP para buscar, comparar y ejecutar compras en 41 retailers verificados de LATAM."
                : "API, CLI, and MCP tools to search, compare, and execute purchases across 41 verified LATAM retailers."}
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

          {/* Right — terminal */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.32 }}
            className="mt-12 lg:mt-0 lg:shrink-0 lg:w-[480px] xl:w-[520px]"
          >
            {/* Window chrome */}
            <div className="rounded-xl overflow-hidden border border-[#30363d]" style={{ background: "#0d1117" }}>
              {/* Title bar */}
              <div className="flex items-center gap-2 px-4 py-3 border-b border-[#21262d]" style={{ background: "#161b22" }}>
                <span className="w-3 h-3 rounded-full bg-[#ff5f57]" />
                <span className="w-3 h-3 rounded-full bg-[#febc2e]" />
                <span className="w-3 h-3 rounded-full bg-[#28c840]" />
                <span className="ml-3 text-xs text-[#484f58] font-mono">cli-market — bash</span>
              </div>

              {/* Terminal body */}
              <div className="p-5 font-mono text-sm leading-relaxed space-y-1">
                {/* Command */}
                <div>
                  <span style={{ color: "#3fb950" }}>❯</span>{" "}
                  <span style={{ color: "#e6edf3" }}>market optimize </span>
                  <span style={{ color: "#a5d6ff" }}>&quot;leche, arroz, aceite&quot;</span>{" "}
                  <span style={{ color: "#ff7b72" }}>--country</span>{" "}
                  <span style={{ color: "#ffa657" }}>PE</span>
                </div>

                {/* Scanning */}
                <div className="pt-1" style={{ color: "#484f58" }}>
                  {isES ? "▸ Escaneando 41 retailers..." : "▸ Scanning 41 retailers..."}
                </div>

                {/* Separator */}
                <div className="pt-1" style={{ color: "#21262d" }}>{"─".repeat(44)}</div>

                {/* Results header */}
                <div className="pt-1 pb-0.5 flex justify-between">
                  <span style={{ color: "#8b949e" }}>{isES ? "  Retailer" : "  Retailer"}</span>
                  <span style={{ color: "#8b949e" }}>Total (S/)</span>
                </div>

                {/* Row 1 — winner */}
                <div className="flex justify-between items-center rounded px-1" style={{ background: "rgba(63,185,80,0.08)" }}>
                  <span>
                    <span style={{ color: "#3fb950" }}>★ </span>
                    <span style={{ color: "#e6edf3" }}>Tottus PE</span>
                  </span>
                  <span style={{ color: "#3fb950" }}>17.80</span>
                </div>

                {/* Row 2 */}
                <div className="flex justify-between px-1">
                  <span style={{ color: "#c9d1d9" }}>{"  "}Metro PE</span>
                  <span style={{ color: "#c9d1d9" }}>18.40</span>
                </div>

                {/* Row 3 */}
                <div className="flex justify-between px-1">
                  <span style={{ color: "#8b949e" }}>{"  "}Plaza Vea</span>
                  <span style={{ color: "#8b949e" }}>19.10</span>
                </div>

                {/* Row 4 */}
                <div className="flex justify-between px-1">
                  <span style={{ color: "#8b949e" }}>{"  "}Wong PE</span>
                  <span style={{ color: "#8b949e" }}>19.85</span>
                </div>

                {/* Separator */}
                <div className="pt-1" style={{ color: "#21262d" }}>{"─".repeat(44)}</div>

                {/* Savings */}
                <div className="pt-0.5 flex justify-between">
                  <span style={{ color: "#8b949e" }}>
                    {isES ? "  Ahorro vs. promedio" : "  Savings vs. avg"}
                  </span>
                  <span style={{ color: "#3fb950" }}>↓ S/ 1.18 (6.2%)</span>
                </div>

                {/* TCO + action */}
                <div className="pt-2 flex flex-col gap-1">
                  <span style={{ color: "#484f58" }}>
                    {isES ? "  TCO calculado · sustitutos incluidos" : "  TCO calculated · substitutes included"}
                  </span>
                  <span style={{ color: "#58a6ff" }}>
                    {isES ? "  → Link Yape generado ✓" : "  → Yape payment link ready ✓"}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>

        </div>
      </div>
    </section>
  );
}
