"use client";

import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import LegalConsentCheckbox from "@/components/LegalConsentCheckbox";
import type { ProcurePlanSlug } from "@/lib/procurePlans";

type SubscribeResponse = {
  ok?: boolean;
  approve_url?: string;
  tier?: string;
  plan?: string;
  message?: string;
  detail?: string;
  username?: string;
};

export default function ProcureSubscribeButton({
  plan,
  className = "btn-mint w-full",
}: {
  plan: ProcurePlanSlug;
  className?: string;
}) {
  const { lang } = useLang();
  const isES = lang === "es";
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [legal, setLegal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<SubscribeResponse | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!legal) {
      setError(isES ? "Acepta términos y privacidad." : "Accept terms and privacy.");
      return;
    }
    if (!email.includes("@")) {
      setError(isES ? "Email inválido" : "Invalid email");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch(`${API_URL}/billing/procure-subscribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email.trim(),
          username: username.trim() || undefined,
          plan,
          lang: isES ? "es" : "en",
        }),
      });
      const data = (await res.json()) as SubscribeResponse;
      if (!res.ok || !data.ok) {
        setError(
          typeof data.detail === "string"
            ? data.detail
            : data.message || (isES ? "Error al iniciar suscripción" : "Subscription error"),
        );
        return;
      }
      setResult(data);
      if (data.approve_url) window.location.assign(data.approve_url);
    } catch {
      setError(isES ? "Error de conexión" : "Connection error");
    } finally {
      setLoading(false);
    }
  }

  if (result?.approve_url) {
    return (
      <a href={result.approve_url} className={className}>
        {isES ? "Continuar en PayPal →" : "Continue on PayPal →"}
      </a>
    );
  }

  return (
    <form onSubmit={submit} className="space-y-3 text-left">
      <input
        type="email"
        required
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="input-cyber text-sm"
        placeholder={isES ? "email@empresa.com" : "work@company.com"}
      />
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="input-cyber text-sm"
        placeholder={isES ? "usuario CLI (opcional)" : "CLI username (optional)"}
      />
      <LegalConsentCheckbox checked={legal} onChange={setLegal} />
      {error && <p className="text-xs text-[#ffb4ab]">{error}</p>}
      <button type="submit" disabled={loading || !legal} className={`${className} disabled:opacity-50`}>
        {loading
          ? isES
            ? "Conectando PayPal…"
            : "Connecting PayPal…"
          : isES
            ? "Suscribir con PayPal"
            : "Subscribe with PayPal"}
      </button>
    </form>
  );
}