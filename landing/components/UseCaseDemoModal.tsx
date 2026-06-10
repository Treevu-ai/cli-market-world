"use client";

import { useEffect } from "react";
import { useLang } from "@/lib/LanguageContext";
import { recordUseCaseDemoOpen } from "@/lib/funnel";
import type { UseCaseDemo } from "@/lib/useCaseDemos";

const OVERLAY =
  "fixed inset-0 z-[60] flex items-end sm:items-center justify-center p-3 sm:p-6 pointer-events-none";
const BACKDROP = "absolute inset-0 bg-black/70 pointer-events-auto backdrop-blur-sm";
const PANEL =
  "relative pointer-events-auto w-full sm:max-w-[960px] card-cyber p-4 sm:p-6 animate-fade-in max-h-[92vh] overflow-y-auto";

export default function UseCaseDemoModal({
  open,
  useCase,
  onClose,
}: {
  open: boolean;
  useCase: UseCaseDemo | null;
  onClose: () => void;
}) {
  const { lang } = useLang();
  const isES = lang === "es";

  useEffect(() => {
    if (!open || !useCase) return;
    recordUseCaseDemoOpen(useCase.id);
  }, [open, useCase]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [open, onClose]);

  if (!open || !useCase) return null;

  return (
    <div className={OVERLAY} role="dialog" aria-modal="true" aria-labelledby="use-case-demo-title">
      <button type="button" className={BACKDROP} aria-label={isES ? "Cerrar demo" : "Close demo"} onClick={onClose} />
      <div className={PANEL}>
        <div className="flex items-start justify-between gap-4 mb-4">
          <div className="text-left min-w-0">
            <p className="font-label-caps text-[10px] text-[var(--cm-mint)]/70 mb-1">
              {isES ? "Demo terminal · terminalizer" : "Terminal demo · terminalizer"}
            </p>
            <h3 id="use-case-demo-title" className="font-display text-lg sm:text-xl font-bold text-white flex items-center gap-2">
              <span aria-hidden="true">{useCase.icon}</span>
              {isES ? useCase.title_es : useCase.title_en}
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="shrink-0 font-mono text-xs text-[var(--cm-on-surface-variant)] hover:text-white px-2 py-1"
          >
            ✕
          </button>
        </div>

        <div className="rounded-xl border border-[var(--cm-mint)]/35 bg-[#0a0a0a] overflow-hidden shadow-[0_0_40px_rgba(58,254,207,0.12)]">
          <img
            src={useCase.gif}
            alt={isES ? useCase.alt_es : useCase.alt_en}
            width={920}
            height={520}
            className="w-full h-auto block"
            loading="eager"
            decoding="async"
          />
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]/70">
            {isES ? "pip install cli-market-world · animación tipo terminalizer" : "pip install cli-market-world · terminalizer-style animation"}
          </p>
          <a href={useCase.ctaHref} className="btn-mint text-xs px-4 py-2" onClick={onClose}>
            {isES ? useCase.cta_es : useCase.cta_en}
          </a>
        </div>
      </div>
    </div>
  );
}
