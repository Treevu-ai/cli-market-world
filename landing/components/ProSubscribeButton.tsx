"use client";

import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import { MARKET_STATS } from "@/lib/marketStats";
import PayPalHostedButton from "@/components/PayPalHostedButton";
import LegalConsentCheckbox from "@/components/LegalConsentCheckbox";

type ProResponse = {
  ok?: boolean;
  approve_url?: string;
  payment_link?: string;
  subscription_id?: string;
  username?: string;
  auto_activate?: boolean;
  message?: string;
  detail?: string | { msg?: string }[];
  email_sent?: boolean;
  duplicate?: boolean;
};

function escapeHtml(unsafe: string): string {
  return unsafe
    .replace(/&/g, "\u0026amp;")
    .replace(/</g, "\u0026lt;")
    .replace(/>/g, "\u0026gt;")
    .replace(/\"/g, "\u0026quot;")
    .replace(/'/g, "\u0026#039;");
}

function parseApiError(data: ProResponse, fallback: string): string {
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail) && data.detail[0]?.msg) return data.detail[0].msg;
  return data.message || fallback;
}

export default function ProSubscribeButton() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [legal, setLegal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ProResponse | null>(null);
  const [error, setError] = useState("");

  const payload = () => ({
    email: email.trim(),
    username: username.trim() || undefined,
    lang: isES ? "es" : "en",
  });

  const submit = async () => {
    setError("");
    if (!email.trim()) {
      setError(isES ? "Ingrese su email" : "Enter your email");
      return;
    }
    if (!legal) {
      setError(
        isES
          ? "Debe aceptar los Términos y la Política de Privacidad."
          : "You must accept the Terms and Privacy Policy.",
      );
      return;
    }
    setLoading(true);
    try {
      const r = await fetch(`${API_URL}/billing/paypal-subscribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload()),
      });
      const data: ProResponse = await r.json();

      if (r.ok && data.ok && data.approve_url) {
        setResult(data);
        setLoading(false);
        return;
      }

      if (r.status === 404 || r.status === 501 || r.status === 502 || r.status === 503) {
        const fallback = await fetch(`${API_URL}/billing/request-pro`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload()),
        });
        const fb: ProResponse = await fallback.json();
        if (fallback.ok && fb.ok && fb.payment_link) {
          setResult({ ...fb, approve_url: fb.payment_link });
          setLoading(false);
          return;
        }
        setError(parseApiError(fb, isES ? "No se pudo iniciar el pago" : "Could not start checkout"));
        setLoading(false);
        return;
      }

      setError(parseApiError(data, isES ? "Error al conectar con PayPal" : "PayPal connection error"));
    } catch {
      setError(isES ? "Error de red" : "Network error");
    }
    setLoading(false);
  };

  if (result?.ok && result.approve_url) {
    const safeUser = String(result.username || "");
    const isEmailLink = Boolean(result.payment_link && !result.subscription_id);
    return (
      <div className="space-y-3 text-left">
        <div className="rounded border border-[var(--cm-mint)]/20 bg-[var(--cm-mint)]/5 p-3 text-sm text-[var(--cm-on-surface-variant)]">
          <p>
            {result.message ||
              (isEmailLink
                ? isES
                  ? "Le enviamos el link de pago. Revise su bandeja (y spam)."
                  : "We sent the payment link. Check your inbox (and spam)."
                : isES
                  ? "Confirme en PayPal — Pro se activa automáticamente vía webhook."
                  : "Confirm in PayPal — Pro activates automatically via webhook.")}
          </p>
          {safeUser && (
            <p className="mt-1 font-mono text-[11px] text-[var(--cm-on-surface-variant)]/60">
              {isES ? "Usuario CLI" : "CLI user"}: {escapeHtml(safeUser)}
            </p>
          )}
        </div>

        <a
          href={result.approve_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center text-sm font-semibold px-6 py-3 transition-colors w-full btn-mint"
        >
          {isEmailLink
            ? isES
              ? "Abrir link de pago →"
              : "Open payment link →"
            : isES
              ? "Suscribirse en PayPal — $79/mes →"
              : "Subscribe on PayPal — $79/mo →"}
        </a>

        <p className="text-xs text-[var(--cm-on-surface-variant)]/60 leading-relaxed">
          {isES
            ? `Pagos: ${MARKET_STATS.paymentsLabel}. Tras pagar ejecute market whoami — tier: pro.`
            : `Payments: ${MARKET_STATS.paymentsLabel}. After payment run market whoami — tier: pro.`}
        </p>

        <details className="text-xs text-[var(--cm-on-surface-variant)]/50">
          <summary className="cursor-pointer hover:text-white">
            {isES ? "Alternativa: botón alojado PayPal" : "Alternative: PayPal hosted button"}
          </summary>
          <div className="mt-2">
            <PayPalHostedButton className="w-full" />
          </div>
        </details>
      </div>
    );
  }

  return (
    <div className="form-stack">
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder={isES ? "su@email.com" : "you@email.com"}
        className="w-full input-cyber"
      />
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder={isES ? "usuario CLI (market whoami) — opcional" : "CLI username (market whoami) — optional"}
        className="w-full input-cyber text-sm"
      />

      <p className="text-[11px] text-[var(--cm-on-surface-variant)]/70 leading-relaxed rounded border border-[var(--cm-outline-variant)]/30 bg-[var(--cm-surface-low)]/50 p-2.5">
        {isES ? (
          <>
            Plan Pro: <strong>USD 79/mes</strong>, renovación automática vía PayPal. Puede cancelar en cualquier
            momento desde su cuenta PayPal o escribiendo a{" "}
            <a href="mailto:hello@cli-market.dev" className="text-[var(--cm-mint)] underline">
              hello@cli-market.dev
            </a>
            . Facturación PEN disponible (RUC 20613045563). El tier Pro se activa tras confirmar el pago (webhook).
          </>
        ) : (
          <>
            Pro plan: <strong>USD 79/mo</strong>, auto-renewal via PayPal. Cancel anytime from your PayPal account or
            email{" "}
            <a href="mailto:hello@cli-market.dev" className="text-[var(--cm-mint)] underline">
              hello@cli-market.dev
            </a>
            . PEN invoicing available (tax ID 20613045563). Pro tier activates after payment confirmation (webhook).
          </>
        )}
      </p>

      <LegalConsentCheckbox checked={legal} onChange={setLegal} includeSubscriptions />

      {error && <p className="text-xs text-[#ffb4ab]">{error}</p>}
      <button
        onClick={submit}
        disabled={loading || !legal}
        className="btn-mint w-full disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading
          ? isES
            ? "Preparando pago..."
            : "Preparing checkout..."
          : isES
            ? "Obtener Pro — $79/mes"
            : "Get Pro — $79/mo"}
      </button>
      <p className="text-xs text-center text-[var(--cm-on-surface-variant)]/60">
        {isES
          ? `${MARKET_STATS.paymentsLabel} · Checkout de productos vía MP/Yape con tier Pro`
          : `${MARKET_STATS.paymentsLabel} · Product checkout via MP/Yape on Pro tier`}
      </p>
    </div>
  );
}