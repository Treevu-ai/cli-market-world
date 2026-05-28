"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL, PRO_PAYMENT_URL } from "@/lib/api";
import PayPalHostedButton from "@/components/PayPalHostedButton";

const PLANS = [
  { key: "free", es: "Free", en: "Free", price: "$0" },
  { key: "pro", es: "Pro", en: "Pro", price: "$49/mes" },
  { key: "enterprise", es: "Enterprise", en: "Enterprise", price: "Custom" },
];

export default function ContactForm({ initial = "pro" }: { initial?: string }) {
  const { lang } = useLang();
  const [plan, setPlan] = useState(initial);
  const [email, setEmail] = useState("");
  const [useCase, setUseCase] = useState("");
  const [sent, setSent] = useState(false);
  const [proResult, setProResult] = useState<{ request_id?: string; email_sent?: boolean; payment_link?: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const isES = lang === "es";

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !useCase) { setError(isES ? "Completa todos los campos" : "Fill all fields"); return; }
    setLoading(true); setError("");
    const endpoint = plan === "pro" ? `${API_URL}/billing/request-pro` : `${API_URL}/v1/contact`;
    const payload =
      plan === "pro"
        ? { email, lang: isES ? "es" : "en", use_case: useCase }
        : { plan, email, use_case: useCase, lang: isES ? "es" : "en" };
    try {
      const res = await fetch(endpoint, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        if (plan === "pro") setProResult(data);
        setSent(true);
        return;
      }
      throw new Error(data.detail || "Server error");
    } catch {
      setLoading(false);
      const subject = encodeURIComponent(`CLI Market ${plan} — ${email}`);
      const body = encodeURIComponent(useCase);
      window.location.href = `mailto:hello@cli-market.dev?subject=${subject}&body=${body}`;
    }
  };

  if (sent) return (
    <div className="bg-[var(--wise-green-pale)] rounded-3xl p-8 text-center max-w-[480px] mx-auto space-y-4">
      <p className="text-lg font-semibold text-[var(--wise-ink)]">
        {plan === "pro"
          ? (isES
            ? "Solicitud Pro recibida"
            : "Pro request received")
          : (isES ? "¡Gracias! Te escribiremos pronto." : "Thanks! We'll reach out soon.")}
      </p>
      {plan === "pro" && (
        <>
          <p className="text-sm text-[var(--wise-body)]">
            {proResult?.email_sent
              ? (isES ? `Revisa ${email} — link desde hello@cli-market.dev` : `Check ${email} — link from hello@cli-market.dev`)
              : (isES ? "Paga abajo o usa el link de PayPal:" : "Pay below or use the PayPal link:")}
          </p>
          {proResult?.request_id && (
            <p className="font-mono text-xs text-[var(--wise-mute)]">Ref: {proResult.request_id}</p>
          )}
          <PayPalHostedButton />
          <a href={proResult?.payment_link || PRO_PAYMENT_URL} target="_blank" rel="noopener noreferrer"
            className="text-xs underline text-[var(--wise-mute)]">
            {isES ? "Abrir PayPal" : "Open PayPal"}
          </a>
        </>
      )}
    </div>
  );

  return (
    <form onSubmit={submit} className="bg-white rounded-3xl border border-[#c5edab] p-8 max-w-[480px] mx-auto space-y-5 text-left">
      <h3 className="text-lg font-semibold text-[var(--wise-ink)]">{isES ? "Solicitar acceso" : "Request access"}</h3>
      <div className="flex gap-2">
        {PLANS.map((p) => (
          <button key={p.key} type="button" onClick={() => setPlan(p.key)}
            className={`flex-1 rounded-3xl px-4 py-2 text-sm font-semibold transition-colors ${plan === p.key ? "bg-[#9fe870] text-[var(--wise-ink)]" : "bg-[var(--wise-canvas-soft)] text-[var(--wise-body)] hover:bg-[#c5edab]"}`}>
            {isES ? p.es : p.en} {p.price}
          </button>
        ))}
      </div>
      <div>
        <label className="block text-sm font-medium text-[var(--wise-ink)] mb-1">Email</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
          className="w-full rounded-3xl border border-[#c5edab] px-4 py-2.5 text-sm text-[var(--wise-ink)] bg-[var(--wise-canvas-soft)] focus:outline-none focus:border-[#9fe870]"
          placeholder="tu@email.com" />
      </div>
      <div>
        <label className="block text-sm font-medium text-[var(--wise-ink)] mb-1">{isES ? "Caso de uso" : "Use case"}</label>
        <textarea value={useCase} onChange={(e) => setUseCase(e.target.value)} rows={3}
          className="w-full rounded-3xl border border-[#c5edab] px-4 py-2.5 text-sm text-[var(--wise-ink)] bg-[var(--wise-canvas-soft)] focus:outline-none focus:border-[#9fe870] resize-none"
          placeholder={isES ? "Cuéntanos qué quieres construir..." : "Tell us what you want to build..."} />
      </div>
      {error && <p className="text-sm text-[#a7000d]">{error}</p>}
      <button type="submit" disabled={loading}
        className="w-full rounded-3xl bg-[#9fe870] text-[var(--wise-ink)] text-base font-semibold px-8 py-3 hover:bg-[#cdffad] transition-colors disabled:opacity-50">
        {loading ? (isES ? "Enviando..." : "Sending...") : (isES ? "Enviar solicitud" : "Send request")}
      </button>
    </form>
  );
}
