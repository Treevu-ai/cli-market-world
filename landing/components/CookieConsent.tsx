"use client";

import { useLayoutEffect, useState } from "react";
import { useLang } from "@/lib/LanguageContext";

const STORAGE_KEY = "cm-cookie-consent";

function readNeedsConsent(): boolean {
  try {
    return !window.localStorage.getItem(STORAGE_KEY);
  } catch {
    return true;
  }
}

export default function CookieConsent() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [visible, setVisible] = useState(false);
  const [ready, setReady] = useState(false);

  useLayoutEffect(() => {
    setVisible(readNeedsConsent());
    setReady(true);
  }, []);

  useLayoutEffect(() => {
    if (!visible) {
      document.body.classList.remove("cookie-banner-active");
      return;
    }
    document.body.classList.add("cookie-banner-active");
    return () => document.body.classList.remove("cookie-banner-active");
  }, [visible]);

  const accept = () => {
    try {
      window.localStorage.setItem(STORAGE_KEY, "accepted");
    } catch {
      // ignore
    }
    setVisible(false);
  };

  if (!ready || !visible) return null;

  return (
    <div
      role="dialog"
      aria-live="polite"
      aria-label={isES ? "Aviso de cookies" : "Cookie notice"}
      data-cookie-banner="true"
      className="fixed bottom-0 inset-x-0 z-[100] p-3 sm:p-4 md:px-6 pb-[max(0.75rem,env(safe-area-inset-bottom))] md:pb-6 pointer-events-none"
    >
      <div className="landing-container-wide pointer-events-auto">
        <div className="rounded-lg border border-[var(--cm-mint)]/30 bg-[var(--cm-surface-low)]/95 backdrop-blur-md p-4 md:p-5 flex flex-col md:flex-row md:items-center gap-3 md:gap-4 shadow-[0_-8px_32px_rgba(0,0,0,0.45)]">
          <p className="text-sm md:text-xs text-[var(--cm-on-surface-variant)] leading-relaxed flex-1">
            {isES ? (
              <>
                Usamos cookies técnicas y analíticas esenciales (Cloudflare, Plausible) para medir
                visitas agregadas y proteger el sitio. No usamos cookies de publicidad. Consulte la{" "}
                <a href="/legal/privacy" className="text-[var(--cm-mint)] hover:underline">
                  Política de Privacidad
                </a>
                .
              </>
            ) : (
              <>
                We use essential technical and analytics cookies (Cloudflare, Plausible) for
                aggregated visit metrics and site protection. We do not use advertising cookies. See
                our{" "}
                <a href="/legal/privacy" className="text-[var(--cm-mint)] hover:underline">
                  Privacy Policy
                </a>
                .
              </>
            )}
          </p>
          <button
            type="button"
            onClick={accept}
            className="btn-mint text-xs px-5 py-2.5 w-full md:w-auto shrink-0 md:self-center"
          >
            {isES ? "Entendido" : "Got it"}
          </button>
        </div>
      </div>
    </div>
  );
}