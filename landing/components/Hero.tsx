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
    { label: isES ? "41 retailers verificados" : "41 verified retailers" },
    { label: isES ? "61K+ precios normalizados" : "61K+ normalized prices" },
    { label: isES ? "8 países LATAM" : "8 LATAM countries" },
    { label: isES ? "Refresh cada 4h" : "4h refresh cycle" },
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
            {isES ? "INFRAESTRUCTURA PARA COMERCIO AGÉNTICO" : "INFRASTRUCTURE FOR AGENTIC COMMERCE"}
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="hero-garamond-headline"
          >
            {isES
              ? "La capa de ejecución comercial para agentes de IA"
              : "The commerce execution layer for AI agents"}
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
            className="mt-5 text-base sm:text-lg max-w-[620px] leading-relaxed stripe-body"
          >
            {isES ? (
              <>
                Permite que los agentes de IA busquen, comparen y ejecuten comercio real en retailers LATAM a través de una sola API. CLI Market transforma sistemas retail fragmentados en infraestructura lista para agentes — dando acceso a precios verificados, optimización de canasta, flujos de procurement y ejecución comercial sin scraping ni integraciones manuales.
              </>
            ) : (
              <>
                Enable AI agents to search, compare, and execute real-world commerce across LATAM retailers using one API. CLI Market transforms fragmented retail systems into agent-ready infrastructure — giving AI agents access to verified pricing, basket optimization, procurement workflows, and commerce execution without scraping or manual integrations.
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
              ? `Powered by el toolkit más completo para comercio agéntico en LATAM — API, CLI, herramientas MCP y flujos de procurement.`
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
              $ market basket &quot;rice:1kg milk:1L oil:1L&quot; --country PE
            </div>
            <div className="mt-3" style={{ color: "#8b949e" }}>
              {isES ? "Mejor canasta:" : "Best basket:"}
            </div>
            <div className="mt-1 pl-2">
              <span style={{ color: "#e6edf3" }}>Metro PE</span>
              <span style={{ color: "#3fb950" }}>{"      S/ 18.40"}</span>
            </div>
            <div className="pl-2">
              <span style={{ color: "#e6edf3" }}>{isES ? "Ahorro" : "Savings"}</span>
              <span style={{ color: "#3fb950" }}>{"       S/ 2.30"}</span>
            </div>
            <div className="mt-3" style={{ color: "#8b949e" }}>
              {isES ? "Completado en 0.82s" : "Completed in 0.82s"}
            </div>
          </div>
        </motion.div>

      </div>
    </section>
  );
}
