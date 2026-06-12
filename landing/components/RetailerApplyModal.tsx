"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { useBodyScrollLock } from "@/hooks/useBodyScrollLock";
import { useLang } from "@/lib/LanguageContext";
import RetailerApplyForm from "@/components/RetailerApplyForm";
import {
  LANDING_MODAL_BACKDROP,
  LANDING_MODAL_OVERLAY,
  LANDING_MODAL_PANEL,
  LANDING_MODAL_PANEL_MD,
} from "@/lib/modalLayout";

const MODAL_PANEL = `${LANDING_MODAL_PANEL} ${LANDING_MODAL_PANEL_MD} card-cyber p-0 sm:max-w-[540px] overflow-hidden`;

export default function RetailerApplyModal({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const { lang } = useLang();
  const isES = lang === "es";
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);
  useBodyScrollLock(open);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open || !mounted) return null;

  return createPortal(
    <div role="dialog" aria-modal="true" className={LANDING_MODAL_OVERLAY}>
      <div className={LANDING_MODAL_BACKDROP} aria-hidden onClick={onClose} />
      <div className={`${MODAL_PANEL} relative`}>
        <button
          type="button"
          onClick={onClose}
          aria-label={isES ? "Cerrar" : "Close"}
          className="absolute top-4 right-4 z-10 text-[var(--cm-on-surface-variant)] hover:text-white transition-colors text-lg leading-none"
        >
          ✕
        </button>
        <div className="max-h-[min(85dvh,720px)] overflow-y-auto p-6 sm:p-8">
          <RetailerApplyForm variant="modal" onSuccess={onClose} />
        </div>
      </div>
    </div>,
    document.body,
  );
}
