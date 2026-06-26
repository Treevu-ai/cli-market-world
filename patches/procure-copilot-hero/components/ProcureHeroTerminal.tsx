"use client";

import { useState } from "react";

const GIF_W = 920;
const GIF_H = 520;

type ProcureHeroTerminalProps = {
  retailersVerified?: number;
};

/** GIF-only hero demo — no HTML chrome (the asset already includes the terminal frame). */
export default function ProcureHeroTerminal({
  retailersVerified = 40,
}: ProcureHeroTerminalProps) {
  const [gifOk, setGifOk] = useState(true);

  return (
    <div className="mt-10 w-full mx-auto text-left">
      <div
        className="rounded-xl border border-[var(--cm-mint)]/35 bg-[#0a0a0a] overflow-hidden"
        aria-label="Demo del flujo de procurement"
      >
        {gifOk ? (
          <img
            src="/demo.gif"
            alt={`Demo Procure Copilot: canasta, compare y checkout con ${retailersVerified} retailers verificados`}
            width={GIF_W}
            height={GIF_H}
            className="w-full h-auto block"
            loading="eager"
            decoding="async"
            onError={() => setGifOk(false)}
          />
        ) : (
          <div className="flex items-center justify-center aspect-[920/520] text-[10px] font-mono text-[var(--cm-on-surface-variant)]">
            Demo no disponible
          </div>
        )}
      </div>
      <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-2 font-mono text-center text-balance px-1">
        Canasta → compare → aprobación → checkout · CLI Market · {retailersVerified} retailers
      </p>
    </div>
  );
}
