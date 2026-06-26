"use client";

const GIF_W = 920;
const GIF_H = 520;

type ProcureHeroTerminalProps = {
  retailersVerified?: number;
};

export default function ProcureHeroTerminal({
  retailersVerified = 40,
}: ProcureHeroTerminalProps) {
  return (
    <div className="mt-10 w-full max-w-[920px] mx-auto text-left">
      <div
        className="rounded-xl border border-[var(--cm-mint)]/35 bg-[var(--cm-surface-lowest)] overflow-hidden"
        aria-label="Demo del flujo de procurement"
      >
        <div className="flex items-center gap-2 px-4 py-2.5 border-b border-[var(--cm-outline-variant)] bg-[var(--cm-surface)]/80">
          <span className="w-2.5 h-2.5 rounded-full bg-red-400/80" aria-hidden="true" />
          <span className="w-2.5 h-2.5 rounded-full bg-yellow-400/80" aria-hidden="true" />
          <span className="w-2.5 h-2.5 rounded-full bg-[var(--cm-mint)]/80" aria-hidden="true" />
          <span className="ml-2 text-[10px] font-mono text-[var(--cm-on-surface-variant)] uppercase tracking-wider">
            procure-copilot · demo
          </span>
        </div>
        <div className="relative w-full aspect-[920/520] bg-[#0a0a0a]">
          <img
            src="/demo.gif"
            alt={`Demo Procure Copilot: canasta, compare y checkout con ${retailersVerified} retailers verificados`}
            width={GIF_W}
            height={GIF_H}
            className="w-full h-full object-contain object-top block"
            loading="eager"
            decoding="async"
          />
        </div>
      </div>
      <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-2 font-mono text-center">
        Canasta → compare → aprobación → checkout · datos CLI Market · {retailersVerified}{" "}
        retailers verificados
      </p>
    </div>
  );
}
