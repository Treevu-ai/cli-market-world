"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";

/** Enterprise / sales contact — Pro checkout lives in ProSubscribeButton on the Pro card. */
export default function ContactForm() {
  const { lang } = useLang();
  const [email, setEmail] = useState("");
  const [useCase, setUseCase] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const isES = lang === "es";

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !useCase) {
      setError(isES ? "Completa todos los campos" : "Fill all fields");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/v1/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          plan: "enterprise",
          email,
          use_case: useCase,
          lang: isES ? "es" : "en",
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setSent(true);
        return;
      }
      throw new Error(data.detail || "Server error");
    } catch {
      setLoading(false);
      const subject = encodeURIComponent(`CLI Market Enterprise — ${email}`);
      const body = encodeURIComponent(useCase);
      window.location.href = `mailto:hello@cli-market.dev?subject=${subject}&body=${body}`;
    }
  };

  if (sent) {
    return (
      <div className="bg-[var(--wise-green-pale)] rounded-3xl p-6 sm:p-8 text-center w-full max-w-lg mx-auto space-y-3 min-w-0">
        <p className="text-lg font-semibold text-[var(--wise-ink)]">
          {isES ? "¡Gracias! Te escribiremos pronto." : "Thanks! We'll reach out soon."}
        </p>
        <p className="text-sm text-[var(--wise-body)] break-words">
          {isES ? `Revisaremos tu caso y responderemos a ${email}.` : `We'll review your use case and reply to ${email}.`}
        </p>
      </div>
    );
  }

  return (
    <form
      onSubmit={submit}
      className="bg-white rounded-3xl border border-[#c5edab] p-5 sm:p-8 w-full max-w-lg mx-auto space-y-5 text-left min-w-0 overflow-hidden"
    >
      <div className="text-center space-y-1">
        <span className="inline-block text-[10px] font-mono uppercase tracking-widest text-[var(--wise-mute)]">
          Enterprise
        </span>
        <h3 className="text-lg font-semibold text-[var(--wise-ink)]">
          {isES ? "Cuéntanos tu caso" : "Tell us about your use case"}
        </h3>
      </div>

      <div>
        <label className="block text-sm font-medium text-[var(--wise-ink)] mb-1">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full min-w-0 rounded-3xl border border-[#c5edab] px-4 py-2.5 text-sm text-[var(--wise-ink)] bg-[var(--wise-canvas-soft)] focus:outline-none focus:border-[#9fe870]"
          placeholder="tu@email.com"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-[var(--wise-ink)] mb-1">
          {isES ? "Qué necesitas" : "What you need"}
        </label>
        <textarea
          value={useCase}
          onChange={(e) => setUseCase(e.target.value)}
          rows={3}
          className="w-full min-w-0 rounded-3xl border border-[#c5edab] px-4 py-2.5 text-sm text-[var(--wise-ink)] bg-[var(--wise-canvas-soft)] focus:outline-none focus:border-[#9fe870] resize-none"
          placeholder={
            isES
              ? "Volumen, SLA, webhooks, integración..."
              : "Volume, SLA, webhooks, integration..."
          }
        />
      </div>
      {error && <p className="text-sm text-[#a7000d]">{error}</p>}
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-3xl bg-[var(--wise-green)] text-[var(--wise-ink)] text-base font-semibold px-6 py-3 hover:bg-[var(--wise-green-hover)] transition-colors disabled:opacity-50"
      >
        {loading ? (isES ? "Enviando..." : "Sending...") : (isES ? "Contactar ventas" : "Contact sales")}
      </button>
    </form>
  );
}
