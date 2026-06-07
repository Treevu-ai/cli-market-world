"use client";

import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import { recordFunnelEvent } from "@/lib/funnel";
import LegalConsentCheckbox from "@/components/LegalConsentCheckbox";

type StarterResponse = {
  ok?: boolean;
  approve_url?: string;
  subscription_id?: string;
  username?: string;
  auto_activate?: boolean;
  email_sent?: boolean;
  message?: string;
  detail?: string | { msg?: string }[];
};

function parseApiError(data: StarterResponse, fallback: string): string {
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail) && data.detail[0]?.msg) return data.detail[0].msg;
  return data.message || fallback;
}

export default function StarterSubscribeButton() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [legal, setLegal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<StarterResponse | null>(null);
  const [error, setError] = useState("");

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
      const r = await fetch(`${API_URL}/billing/starter-subscribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email.trim(),
          username: username.trim() || undefined,
          lang: isES ? "es" : "en",
        }),
      });
      const data: StarterResponse = await r.json();
      if (r.ok && data.ok && data.approve_url) {
        recordFunnelEvent("starter_subscribe", {
          username: data.username || username.trim() || undefined,
          meta: { source: "landing_checkout", email: email.trim() },
        });
        setResult(data);
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
    return (
      <div className="space-y-3 text-left">
        <div className="rounded border border-[var(--cm-mint)]/20 bg-[var(--cm-mint)]/5 p-3 text-sm text-[var(--cm-on-surface-variant)]">
          <p>{result.message}</p>
          {result.email_sent && (
            <p className="mt-1 text-[11px]">
              {isES ? "Revise su bandeja (y spam) por el enlace de PayPal." : "Check your inbox (and spam) for the PayPal link."}
            </p>
          )}
        </div>
        <a
          href={result.approve_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center text-sm font-semibold px-6 py-3 transition-colors w-full btn-mint"
        >
          {isES ? "Suscribirse en PayPal — $29/mes →" : "Subscribe on PayPal — $29/mo →"}
        </a>
        <p className="text-xs text-[var(--cm-on-surface-variant)]/60">
          {isES ? "Tras pagar: market whoami — tier: starter" : "After payment: market whoami — tier: starter"}
        </p>
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
        placeholder={isES ? "usuario CLI (opcional)" : "CLI username (optional)"}
        className="w-full input-cyber text-sm"
      />
      <p className="text-[11px] text-[var(--cm-on-surface-variant)]/70 leading-relaxed rounded border border-[var(--cm-outline-variant)]/30 bg-[var(--cm-surface-low)]/50 p-2.5">
        {isES ? (
          <>
            Plan Starter: <strong>USD 29/mes</strong>, renovación automática vía PayPal. Activación en segundos tras
            confirmar (webhook). Recomendado: <code className="text-[var(--cm-mint)]">market register</code> antes.
          </>
        ) : (
          <>
            Starter plan: <strong>USD 29/mo</strong>, auto-renewal via PayPal. Activates in seconds after confirmation
            (webhook). Recommended: <code className="text-[var(--cm-mint)]">market register</code> first.
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
            ? "Obtener Starter — $29/mes"
            : "Get Starter — $29/mo"}
      </button>
    </div>
  );
}