"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";

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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const isES = lang === "es";

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !useCase) { setError(isES ? "Completa todos los campos" : "Fill all fields"); return; }
    setLoading(true); setError("");
    try {
      await fetch("https://cli-market-production.up.railway.app/v1/contact", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan, email, use_case: useCase }),
      });
      setSent(true);
    } catch { setSent(true); }
    setLoading(false);
  };

  if (sent) return (
    <div className="bg-[var(--wise-green-pale)] rounded-3xl p-8 text-center max-w-[480px] mx-auto">
      <p className="text-lg font-semibold text-[var(--wise-ink)]">{isES ? "¡Gracias! Te escribiremos pronto." : "Thanks! We'll reach out soon."}</p>
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
