"use client";

import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function HeroDemo() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <div className="mt-12 w-full max-w-[920px]">
      <div
        className="rounded-xl border border-[var(--cm-mint)]/35 bg-[#0a0a0a] shadow-[0_0_40px_rgba(58,254,207,0.12)] overflow-hidden text-left"
        aria-label={isES ? "Demo terminal CLI Market" : "CLI Market terminal demo"}
      >
        <img
          src="/demo.gif"
          alt={
            isES
              ? "Demo CLI Market: compare y basket en Perú con 68 retailers y 38 verificados"
              : "CLI Market demo: compare and basket in Peru across 68 retailers, 38 verified"
          }
          width={920}
          height={520}
          className="w-full h-auto block"
          loading="eager"
          decoding="async"
        />
      </div>
      <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-2 font-mono text-center">
        {isES
          ? `Agente IA · compare + basket · ${MARKET_STATS.retailersDefined} retailers · ${MARKET_STATS.retailersVerified} verificados · ${MARKET_STATS.mcpTools} MCP`
          : `AI agent · compare + basket · ${MARKET_STATS.retailersDefined} retailers · ${MARKET_STATS.retailersVerified} verified · ${MARKET_STATS.mcpTools} MCP`}
      </p>
    </div>
  );
}