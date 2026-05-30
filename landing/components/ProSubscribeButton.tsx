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
  const [cliUsername, setCliUsername] = useState("");
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
      const payload: Record<string, string | boolean> = {
        email: email.trim(),
        lang: isES ? "es" : "en",
      };
      if (cliUsername.trim()) payload.username = cliUsername.trim();

      const r = await fetch(`${API_URL}/billing/request-pro`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
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
      <div className="space-y-4 text-left">
        <div className="rounded-2xl bg-[var(--wise-green-pale)] p-4 text-sm text-[var(--wise-body)]">
          {result.email_sent ? (
            <p>
              {isES
                ? `Revisa ${email} — enviamos el link desde hello@cli-market.dev`
                : `Check ${email} — link sent from hello@cli-market.dev`}
            </p>
          ) : (
            <p>
              {isES
                ? "SMTP pendiente en servidor. Paga abajo o usa el link:"
                : "Server SMTP pending. Pay below or use the link:"}
            </p>
          )}
          {ref && (
            <p className="mt-2 font-mono text-xs text-[var(--wise-mute)]">
              Ref: {ref}
            </p>
          )}
        </div>

        <a
          href={payLink}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center rounded-3xl text-sm font-semibold px-6 py-3 transition-colors w-full bg-[var(--wise-green)] text-[var(--wise-ink)] hover:bg-[var(--wise-green-hover)]"
        >
          {isES ? "Pagar USD 49 con PayPal →" : "Pay USD 49 with PayPal →"}
        </a>

        <p className="text-[11px] text-[var(--wise-mute)] leading-relaxed">
          {isES
            ? "Si el botón embebido muestra «Agotado», use el botón verde de arriba. Revise inventario del botón en PayPal Business."
            : "If the embedded button shows “Sold out”, use the green button above. Check button inventory in PayPal Business."}
        </p>

        <PayPalHostedButton className="w-full" />

        <a
          href={payLink}
          target="_blank"
          rel="noopener noreferrer"
          className="block text-center text-xs text-[var(--wise-mute)] underline hover:text-[var(--wise-ink)]"
        >
          {isES ? "Abrir link de pago en PayPal (alternativa)" : "Open PayPal payment link (fallback)"}
        </a>

        <div className="rounded-2xl border border-[var(--wise-green-pale)] p-4 text-xs text-[var(--wise-body)] space-y-2">
          <p className="font-semibold text-[var(--wise-ink)]">
            {isES ? "Después de pagar" : "After payment"}
          </p>
          <ol className="list-decimal list-inside space-y-1">
            <li>
              {isES
                ? "Si aún no tienes cuenta: pip install cli-market && market login"
                : "No account yet? pip install cli-market && market login"}
            </li>
            <li>
              {isES
                ? `Responde al email con tu usuario CLI${cliUsername ? ` (${cliUsername})` : ""} y ref ${ref}`
                : `Reply to the email with your CLI username${cliUsername ? ` (${cliUsername})` : ""} and ref ${ref}`}
            </li>
          </ol>
        </div>
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
        className="w-full rounded-2xl border border-[var(--wise-green-pale)] px-4 py-2.5 text-sm bg-[var(--wise-canvas-soft)]"
      />
      <input
        type="text"
        value={cliUsername}
        onChange={(e) => setCliUsername(e.target.value)}
        placeholder={
          isES
            ? "Usuario CLI (opcional, si ya hiciste market login)"
            : "CLI username (optional, if you ran market login)"
        }
        className="w-full rounded-2xl border border-[var(--wise-green-pale)] px-4 py-2.5 text-sm bg-[var(--wise-canvas-soft)]"
      />
      {error && <p className="text-xs text-red-600">{error}</p>}
      <button
        onClick={submit}
        disabled={loading}
        className="inline-flex items-center justify-center rounded-3xl text-sm font-semibold px-6 py-3 transition-colors w-full bg-[var(--wise-green)] text-[var(--wise-ink)] hover:bg-[var(--wise-green-hover)] disabled:opacity-50"
      >
        {loading
          ? isES
            ? "Enviando..."
            : "Sending..."
          : isES
            ? "Solicitar Pro — $49/mo"
            : "Request Pro — $49/mo"}
      </button>
    </div>
  );
}
