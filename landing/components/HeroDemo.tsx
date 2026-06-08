"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

type DemoLine = { type: "cmd" | "out"; text: string };

const STEPS_ES: DemoLine[][] = [
  [{ type: "cmd", text: MARKET_STATS.pipInstallCmd }],
  [{ type: "out", text: `✓ ${MARKET_STATS.pypiPackageName} ${MARKET_STATS.packageVersion}` }],
  [{ type: "cmd", text: "market init" }],
  [
    {
      type: "out",
      text: `✓ ${MARKET_STATS.retailersVerified} retailers verificados · ${MARKET_STATS.mcpTools} MCP · ${MARKET_STATS.countries} países`,
    },
  ],
  [{ type: "cmd", text: 'market compare "arroz" --country PE' }],
  [{ type: "out", text: "Metro S/2.90 · Wong S/3.10 · Plaza Vea S/2.95 · normalizado/kg" }],
  [{ type: "cmd", text: 'market basket "arroz:1 leche:1" --country PE' }],
  [{ type: "out", text: "Mejor: Metro S/12.40 · ahorro S/1.20 vs promedio" }],
];

const STEPS_EN: DemoLine[][] = [
  [{ type: "cmd", text: MARKET_STATS.pipInstallCmd }],
  [{ type: "out", text: `✓ ${MARKET_STATS.pypiPackageName} ${MARKET_STATS.packageVersion}` }],
  [{ type: "cmd", text: "market init" }],
  [
    {
      type: "out",
      text: `✓ ${MARKET_STATS.retailersVerified} verified retailers · ${MARKET_STATS.mcpTools} MCP · ${MARKET_STATS.countries} countries`,
    },
  ],
  [{ type: "cmd", text: 'market compare "rice" --country PE' }],
  [{ type: "out", text: "Metro S/2.90 · Wong S/3.10 · Plaza Vea S/2.95 · per kg" }],
  [{ type: "cmd", text: 'market basket "rice:1 milk:1" --country PE' }],
  [{ type: "out", text: "Best: Metro S/12.40 · saves S/1.20 vs average" }],
];

export default function HeroDemo() {
  const { lang } = useLang();
  const isES = lang === "es";
  const steps = isES ? STEPS_ES : STEPS_EN;
  const [visible, setVisible] = useState<DemoLine[]>([]);
  const [stepIdx, setStepIdx] = useState(0);

  useEffect(() => {
    setVisible([]);
    setStepIdx(0);
  }, [isES]);

  useEffect(() => {
    if (stepIdx >= steps.length) {
      const reset = window.setTimeout(() => {
        setVisible([]);
        setStepIdx(0);
      }, 2800);
      return () => window.clearTimeout(reset);
    }

    const delay = stepIdx === 0 ? 400 : steps[stepIdx][0].type === "cmd" ? 900 : 700;
    const timer = window.setTimeout(() => {
      setVisible((prev) => [...prev, ...steps[stepIdx]]);
      setStepIdx((i) => i + 1);
    }, delay);
    return () => window.clearTimeout(timer);
  }, [stepIdx, steps]);

  return (
    <div className="mt-12 w-full max-w-[900px]">
      <div
        className="rounded-xl border border-[var(--cm-outline-variant)]/40 bg-[#0a0a0a] shadow-lg overflow-hidden text-left"
        aria-label={isES ? "Demo terminal CLI Market" : "CLI Market terminal demo"}
      >
        <div className="flex items-center gap-2 px-4 py-2.5 border-b border-[var(--cm-outline-variant)]/30 bg-[var(--cm-surface-low)]">
          <span className="w-2.5 h-2.5 rounded-full bg-[var(--cm-mint)]/80" />
          <span className="text-[10px] font-mono text-[var(--cm-on-surface-variant)] tracking-wide">
            agent@cli-market · {isES ? "canasta PE" : "PE basket"}
          </span>
        </div>
        <div className="px-4 py-4 sm:px-5 sm:py-5 min-h-[220px] sm:min-h-[240px] font-mono text-xs sm:text-sm leading-relaxed">
          <AnimatePresence initial={false}>
            {visible.map((line, i) => (
              <motion.div
                key={`${line.type}-${i}-${line.text.slice(0, 12)}`}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
                className={
                  line.type === "cmd"
                    ? "text-[var(--cm-mint)] mb-1.5"
                    : "text-[var(--cm-on-surface-variant)] mb-2 pl-0 sm:pl-2"
                }
              >
                {line.type === "cmd" ? `$ ${line.text}` : line.text}
              </motion.div>
            ))}
          </AnimatePresence>
          <span className="inline-block w-2 h-4 bg-[var(--cm-mint)]/80 animate-pulse align-middle" aria-hidden="true" />
        </div>
      </div>
      <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-2 font-mono text-center">
        {isES
          ? `Agente IA · compare + basket · ${MARKET_STATS.retailersVerified} verificados · ${MARKET_STATS.mcpTools} MCP`
          : `AI agent · compare + basket · ${MARKET_STATS.retailersVerified} verified · ${MARKET_STATS.mcpTools} MCP`}
      </p>
    </div>
  );
}