"use client";

import { useLang } from "@/lib/LanguageContext";

export default function CoverageToUseCasesBridge() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <div
      className="landing-section-alt py-12 animate-fade-in border-y border-[var(--cm-outline-variant)]/25"
      aria-label={isES ? "Puente entre cobertura y casos de uso" : "Bridge between coverage and use cases"}
    >
      <div className="landing-container-wide landing-content-narrow text-center">
        <p className="text-base text-[var(--cm-on-surface-variant)] leading-relaxed">
          {isES ? (
            <>
              Con esta cobertura,{" "}
              <a href="#intelligence" className="font-semibold text-[var(--cm-mint)] underline underline-offset-2 hover:brightness-110">
                equipos de pricing y trade
              </a>{" "}
              validan spreads e inflación;{" "}
              <a href="#pricing" className="font-semibold text-[var(--cm-mint)] underline underline-offset-2 hover:brightness-110">
                builders
              </a>{" "}
              integran la misma API en agentes;{" "}
              <a href="#procure" className="font-semibold text-[var(--cm-mint)] underline underline-offset-2 hover:brightness-110">
                equipos de compras
              </a>{" "}
              usan Procure — tres productos, un solo dataset de precios normalizados.
            </>
          ) : (
            <>
              With this coverage,{" "}
              <a href="#intelligence" className="font-semibold text-[var(--cm-mint)] underline underline-offset-2 hover:brightness-110">
                pricing and trade teams
              </a>{" "}
              validate spreads and inflation;{" "}
              <a href="#pricing" className="font-semibold text-[var(--cm-mint)] underline underline-offset-2 hover:brightness-110">
                builders
              </a>{" "}
              plug the same API into agents;{" "}
              <a href="#procure" className="font-semibold text-[var(--cm-mint)] underline underline-offset-2 hover:brightness-110">
                procurement teams
              </a>{" "}
              use Procure — three products, one normalized price dataset.
            </>
          )}
        </p>
      </div>
    </div>
  );
}
