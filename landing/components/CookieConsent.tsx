"use client";

import { useEffect, useState } from "react";
import { useLang } from "@/lib/LanguageContext";

const STORAGE_KEY = "cm-cookie-consent";

export default function CookieConsent() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    try {
      if (!window.localStorage.getItem(STORAGE_KEY)) setVisible(true);
    } catch {
      setVisible(true);
    }
  }, []);

  const accept = () => {
    try {
      window.localStorage.setItem(STORAGE_KEY, "accepted");
    } catch {
      // ignore
    }
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div
      role="dialog"
      aria-live="polite"
      aria-label={isES ? "Aviso de cookies" : "Cookie notice"}
      className="fixed bottom-0 inset-x-0 z-50 p-4 md:px-6 md:pb-6 pointer-events-none"
    >
      <div className="landing-container-wide pointer-events-auto">
        <div className="card-cyber border border-[var(--cm-outline-variant)]/40 p-4 md:p-5 flex flex-col md:flex-row md:items-center gap-4 shadow-lg">
          <p className="text-xs text-[var(--cm-on-surface-variant)] leading-relaxed flex-1">
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
            className="btn-mint text-xs px-5 py-2.5 shrink-0 self-end md:self-center"
          >
            {isES ? "Entendido" : "Got it"}
          </button>
        </div>
      </div>
    </div>
  );
}