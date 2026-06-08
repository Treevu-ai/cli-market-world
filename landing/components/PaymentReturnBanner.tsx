"use client";

import { useEffect, useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { PROCURE_APP_URL } from "@/lib/procurePlans";

export type PaymentReturnState = "success" | "cancelled" | null;

export function readPaymentReturnState(): {
  state: PaymentReturnState;
  audience: "build" | "procure";
} {
  if (typeof window === "undefined") return { state: null, audience: "build" };
  const params = new URLSearchParams(window.location.search);
  const sub = params.get("sub");
  const payment = params.get("payment");
  const audience = params.get("audience") === "procure" ? "procure" : "build";

  let state: PaymentReturnState = null;
  if (sub === "success" || payment === "success") state = "success";
  else if (sub === "cancelled") state = "cancelled";

  return { state, audience };
}

export function clearPaymentReturnQuery(): void {
  if (typeof window === "undefined") return;
  const url = new URL(window.location.href);
  url.searchParams.delete("sub");
  url.searchParams.delete("payment");
  window.history.replaceState(null, "", url.pathname + url.search + url.hash);
}

export default function PaymentReturnBanner() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [visible, setVisible] = useState(false);
  const [state, setState] = useState<PaymentReturnState>(null);
  const [audience, setAudience] = useState<"build" | "procure">("build");

  useEffect(() => {
    const { state: next, audience: aud } = readPaymentReturnState();
    if (!next) return;
    setState(next);
    setAudience(aud);
    setVisible(true);
    clearPaymentReturnQuery();
  }, []);

  if (!visible || !state) return null;

  const isProcure = audience === "procure";
  const isSuccess = state === "success";

  return (
    <div
      role="status"
      className={`mb-8 rounded-xl border px-5 py-4 text-left ${
        isSuccess
          ? "border-[var(--cm-mint)]/40 bg-[var(--cm-mint)]/10"
          : "border-[var(--cm-outline-variant)]/40 bg-[var(--cm-surface-low)]/60"
      }`}
    >
      <p className="text-sm font-semibold text-white mb-2">
        {isSuccess
          ? isES
            ? isProcure
              ? "Suscripción Procure confirmada en PayPal"
              : "Suscripción Build Pro confirmada en PayPal"
            : isProcure
              ? "Procure subscription confirmed on PayPal"
              : "Build Pro subscription confirmed on PayPal"
          : isES
            ? "Pago cancelado en PayPal"
            : "Payment cancelled on PayPal"}
      </p>
      {isSuccess ? (
        <div className="space-y-2 text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
          {isProcure ? (
            <>
              <p>
                {isES
                  ? "La activación tarda unos segundos vía webhook. Luego:"
                  : "Activation takes a few seconds via webhook. Then:"}
              </p>
              <ol className="list-decimal list-inside space-y-1 font-mono text-xs">
                <li>{isES ? "market register  (si es cuenta nueva)" : "market register  (if new account)"}</li>
                <li>{isES ? "market account  → copia sk-…" : "market account  → copy sk-…"}</li>
                <li>{isES ? "Pega la API key en el dashboard Procure" : "Paste API key in Procure dashboard"}</li>
              </ol>
              <a href={PROCURE_APP_URL} className="inline-block text-[var(--cm-mint)] text-xs hover:underline">
                {isES ? "Abrir dashboard Procure →" : "Open Procure dashboard →"}
              </a>
            </>
          ) : (
            <>
              <p>
                {isES
                  ? "Pro se activa en segundos. Verifica con market whoami y prueba market checkout."
                  : "Pro activates in seconds. Verify with market whoami, then try market checkout."}
              </p>
              <p className="font-mono text-xs">
                pip install cli-market-world && market whoami
              </p>
            </>
          )}
        </div>
      ) : (
        <p className="text-sm text-[var(--cm-on-surface-variant)]">
          {isES
            ? "Puedes volver a intentar desde el botón de suscripción."
            : "You can try again from the subscribe button."}
        </p>
      )}
      <button
        type="button"
        onClick={() => setVisible(false)}
        className="mt-3 text-xs text-[var(--cm-on-surface-variant)]/70 hover:text-white"
      >
        {isES ? "Cerrar" : "Dismiss"}
      </button>
    </div>
  );
}