"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { useBodyScrollLock } from "@/hooks/useBodyScrollLock";
import { useLang } from "@/lib/LanguageContext";
import { recordUseCaseDemoOpen } from "@/lib/funnel";
import type { UseCaseDemo } from "@/lib/useCaseDemos";
import { MARKET_STATS } from "@/lib/marketStats";
import {
  LANDING_MODAL_BACKDROP,
  LANDING_MODAL_OVERLAY,
  LANDING_MODAL_PANEL,
  LANDING_MODAL_PANEL_LG,
} from "@/lib/modalLayout";

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
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (!open || !useCase) return;
    recordUseCaseDemoOpen(useCase.id);
  }, [open, useCase]);

  useBodyScrollLock(open);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!mounted || !open || !useCase) return null;

  return createPortal(
    <div className={LANDING_MODAL_OVERLAY} role="dialog" aria-modal="true" aria-labelledby="use-case-demo-title">
      <button type="button" className={LANDING_MODAL_BACKDROP} aria-label={isES ? "Cerrar demo" : "Close demo"} onClick={onClose} />
      <div className={`${LANDING_MODAL_PANEL} ${LANDING_MODAL_PANEL_LG}`}>
        <div className="shrink-0 flex items-start justify-between gap-3 p-3 sm:p-6 sm:pb-3 border-b border-[var(--cm-outline-variant)]/20">
          <div className="text-left min-w-0">
            <p className="hidden sm:block font-label-caps text-[10px] text-[var(--cm-mint)]/70 mb-1">
              {isES ? "Demo terminal · terminalizer" : "Terminal demo · terminalizer"}
            </p>
            <h3
              id="use-case-demo-title"
              className="font-display text-base sm:text-xl font-bold text-white flex items-center gap-2"
            >
              <span aria-hidden="true">{useCase.icon}</span>
              <span className="line-clamp-2">{isES ? useCase.title_es : useCase.title_en}</span>
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

        <div className="flex-1 min-h-0 overflow-hidden px-3 sm:px-6 py-2 sm:py-4 bg-[#0a0a0a]/40">
          <div className="hero-playground-terminal h-full min-h-[200px] flex items-center justify-center p-2 sm:p-4">
            <img
              key={useCase.id}
              src={useCase.gif}
              alt={isES ? useCase.alt_es : useCase.alt_en}
              width={920}
              height={520}
              draggable={false}
              className="max-w-full max-h-full w-auto h-auto object-contain object-center block select-none mx-auto"
              loading="eager"
              decoding="async"
            />
          </div>
        </div>

        <div className="shrink-0 flex flex-col sm:flex-row sm:flex-wrap items-stretch sm:items-center justify-between gap-2 sm:gap-3 p-3 sm:p-6 pt-2 sm:pt-3 border-t border-[var(--cm-outline-variant)]/20 bg-[var(--cm-surface-low)] safe-bottom">
          <p className="hidden sm:block text-[10px] font-mono text-[var(--cm-on-surface-variant)]/70">
            {isES
              ? `${MARKET_STATS.pipInstallCmd} · animación terminalizer`
              : `${MARKET_STATS.pipInstallCmd} · terminalizer animation`}
          </p>
          <div className="flex flex-row gap-2 w-full sm:w-auto sm:ml-auto">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 sm:flex-none text-xs font-mono text-[var(--cm-on-surface-variant)] hover:text-white px-4 py-2.5 border border-[var(--cm-outline-variant)]/40 rounded-lg"
            >
              {isES ? "Cerrar" : "Close"}
            </button>
            <a href={useCase.ctaHref} className="btn-mint flex-1 sm:flex-none text-xs px-4 py-2.5 text-center" onClick={onClose}>
              {isES ? useCase.cta_es : useCase.cta_en}
            </a>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  );
}
