"use client";

import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import PayPalHostedButton from "@/components/PayPalHostedButton";

type ProResponse = {
  ok?: boolean;
  approve_url?: string;
  subscription_id?: string;
  username?: string;
  auto_activate?: boolean;
  message?: string;
  detail?: string;
};

function escapeHtml(unsafe: string): string {
  return unsafe
    .replace(/&/g, "\u0026amp;")
    .replace(/</g, "\u0026lt;")
    .replace(/>/g, "\u0026gt;")
    .replace(/\"/g, "\u0026quot;")
    .replace(/'/g, "\u0026#039;");
}

export default function ProSubscribeButton() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
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
      const r = await fetch(`${API_URL}/billing/paypal-subscribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email.trim(),
          username: username.trim() || undefined,
          lang: isES ? "es" : "en",
        }),
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

  if (result?.ok && result.approve_url) {
    const safeUser = String(result.username || "");
    return (
      <div className="space-y-3 text-left">
        <div className="rounded border border-[var(--cm-mint)]/20 bg-[var(--cm-mint)]/5 p-3 text-sm text-[var(--cm-on-surface-variant)]">
          <p>
            {result.message ||
              (isES
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
          {isES ? "Suscribirse en PayPal — $79/mes →" : "Subscribe on PayPal — $79/mo →"}
        </a>

        <p className="text-xs text-[var(--cm-on-surface-variant)]/60 leading-relaxed">
          {isES
            ? "Tras pagar ejecute market whoami — tier: pro. Sin esperar activación manual."
            : "After payment run market whoami — tier: pro. No manual activation wait."}
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
    <div className="space-y-2">
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder={isES ? "tu@email.com" : "you@email.com"}
        className="w-full input-cyber"
      />
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder={isES ? "usuario CLI (market whoami) — opcional" : "CLI username (market whoami) — optional"}
        className="w-full input-cyber text-sm"
      />
      {error && <p className="text-xs text-[#ffb4ab]">{error}</p>}
      <button
        onClick={submit}
        disabled={loading}
        className="btn-mint w-full disabled:opacity-50"
      >
        {loading
          ? isES
            ? "Conectando PayPal..."
            : "Connecting PayPal..."
          : isES
            ? "Activar Pro con PayPal — $79/mes"
            : "Activate Pro with PayPal — $79/mo"}
      </button>
      <p className="text-xs text-center text-[var(--cm-on-surface-variant)]/60">
        {isES
          ? "Activación automática vía webhook · Recomendado: market register primero"
          : "Auto-activation via webhook · Recommended: market register first"}
      </p>
    </div>
  );
}