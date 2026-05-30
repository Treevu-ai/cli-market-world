"use client";

import { useLang } from "@/lib/LanguageContext";

export default function CoverageToUseCasesBridge() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <div
      className="relative bg-[var(--wise-canvas)] border-y border-[#c5edab] py-8"
      aria-label={isES ? "Puente entre cobertura y casos de uso" : "Bridge between coverage and use cases"}
    >
      <div className="landing-container max-w-2xl mx-auto text-center px-4">
        <p className="text-sm text-[var(--wise-body)] leading-relaxed">
          {isES ? (
            <>
              Con esta cobertura,{" "}
              <a href="#pricing-intelligence" className="font-semibold text-[var(--wise-ink)] underline underline-offset-2 hover:opacity-80">
                equipos de pricing y trade
              </a>{" "}
              validan spreads e inflación;{" "}
              <a href="#pricing-build" className="font-semibold text-[var(--wise-ink)] underline underline-offset-2 hover:opacity-80">
                builders
              </a>{" "}
              integran la misma API en agentes — dos productos, un solo moat de datos.
            </>
          ) : (
            <>
              With this coverage,{" "}
              <a href="#pricing-intelligence" className="font-semibold text-[var(--wise-ink)] underline underline-offset-2 hover:opacity-80">
                pricing and trade teams
              </a>{" "}
              validate spreads and inflation;{" "}
              <a href="#pricing-build" className="font-semibold text-[var(--wise-ink)] underline underline-offset-2 hover:opacity-80">
                builders
              </a>{" "}
              plug the same API into agents — two products, one data moat.
            </>
          )}
        </p>
      </div>
    </div>
  );
}
