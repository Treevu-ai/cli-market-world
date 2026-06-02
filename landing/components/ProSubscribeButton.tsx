"use client";

import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL, PRO_PAYMENT_URL } from "@/lib/api";
import PayPalHostedButton from "@/components/PayPalHostedButton";

type ProResponse = {
  ok?: boolean;
  request_id?: string;
  payment_link?: string;
  email_sent?: boolean;
  duplicate?: boolean;
  message?: string;
  detail?: string;
};

export default function ProSubscribeButton() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ProResponse | null>(null);
  const [error, setError] = useState("");

  const submit = async () => {
    setError("");
    if (!email.trim()) {
      setError(isES ? "Ingresa tu email" : "Enter your email");
      return;
    }
    setLoading(true);
    try {
      const r = await fetch(`${API_URL}/billing/request-pro`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), lang: isES ? "es" : "en" }),
      });
      const data: ProResponse = await r.json();
      if (!r.ok) {
        setError(data.detail || data.message || "Error");
        setLoading(false);
        return;
      }
      setResult(data);
    } catch {
      setError(isES ? "Error de red" : "Network error");
    }
    setLoading(false);
  };

  if (result?.ok) {
    const payLink = result.payment_link || PRO_PAYMENT_URL;
    const ref = result.request_id || "";

    return (
      <div className="space-y-3 text-left">
        <div className="rounded border border-[var(--cm-mint)]/20 bg-[var(--cm-mint)]/5 p-3 text-sm text-[var(--cm-on-surface-variant)]">
          {result.email_sent ? (
            <p>
              {isES
                ? `Revisa ${email} — enviamos el link desde hello@cli-market.dev`
                : `Check ${email} — link sent from hello@cli-market.dev`}
            </p>
          ) : (
            <p>
              {isES
                ? "SMTP pendiente. Paga abajo o usa el link:"
                : "Server SMTP pending. Pay below or use the link:"}
            </p>
          )}
          {ref && (
            <p className="mt-1 font-mono text-[11px] text-[var(--cm-on-surface-variant)]/60">
              Ref: {ref}
            </p>
          )}
        </div>

        <a
          href={payLink}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center text-sm font-semibold px-6 py-3 transition-colors w-full btn-mint"
        >
          {isES ? "Pagar USD 49 con PayPal →" : "Pay USD 49 with PayPal →"}
        </a>

        <p className="text-xs text-[var(--cm-on-surface-variant)]/60 leading-relaxed">
          {isES
            ? "Si el botón de PayPal aparece agotado, use el botón verde de arriba."
            : "If the PayPal button shows sold out, use the green button above."}
        </p>

        <PayPalHostedButton className="w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder={isES ? "tu@email.com" : "you@email.com"}
        className="w-full input-cyber"
      />
      {error && <p className="text-xs text-[#ffb4ab]">{error}</p>}
      <button
        onClick={submit}
        disabled={loading}
        className="btn-mint w-full disabled:opacity-50"
      >
        {loading
          ? isES
            ? "Enviando..."
            : "Sending..."
          : isES
            ? "Solicitar Pro — $49/mes"
            : "Request Pro — $49/mo"}
      </button>
    </div>
  );
}
