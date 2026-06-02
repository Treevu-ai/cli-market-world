"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";

type ContactFormProps = {
  plan?: string;
  eyebrow?: string;
  title?: string;
  subtitle?: string;
  placeholder?: string;
};

export default function ContactForm({
  plan = "enterprise",
  eyebrow,
  title,
  subtitle,
  placeholder,
}: ContactFormProps) {
  const { lang } = useLang();
  const [email, setEmail] = useState("");
  const [useCase, setUseCase] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const isES = lang === "es";
  const isNewsletter = plan === "newsletter";
  const isNewsletter = plan === "newsletter";
  const isNewsletter = plan === "newsletter";
  const isNewsletter = plan === "newsletter";

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || (!isNewsletter && !useCase)) {
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
          plan,
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
      const subject = encodeURIComponent(`CLI Market ${plan} — ${email}`);
      const body = encodeURIComponent(useCase);
      window.location.href = `mailto:hello@cli-market.dev?subject=${subject}&body=${body}`;
    }
  };

  if (sent) {
    return (
      <div className="card-cyber energy-border-active p-6 sm:p-8 text-center w-full max-w-lg mx-auto space-y-3 min-w-0">
        <p className="text-lg font-semibold text-white">
          {isES ? "¡Gracias! Te escribiremos pronto." : "Thanks! We'll reach out soon."}
        </p>
        <p className="text-sm text-[var(--cm-on-surface-variant)] break-words">
          {isES ? `Revisaremos tu caso y responderemos a ${email}.` : `We'll review your use case and reply to ${email}.`}
        </p>
      </div>
    );
  }

  return (
    <form
      onSubmit={submit}
      className="card-cyber p-5 sm:p-8 w-full max-w-lg mx-auto space-y-5 text-left min-w-0 overflow-hidden"
    >
      <div className="text-center space-y-1">
        <span className="inline-block font-label-caps text-[var(--cm-on-surface-variant)]/60">
          {eyebrow || "Enterprise"}
        </span>
        <h3 className="text-lg font-semibold text-white">
          {title || (isES ? "Cuéntanos tu caso" : "Tell us about your use case")}
        </h3>
        {subtitle && <p className="text-sm text-[var(--cm-on-surface-variant)]">{subtitle}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-white mb-1">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="input-cyber"
          placeholder="tu@email.com"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-white mb-1">
          {isNewsletter ? "" : (isES ? "Qué necesitas" : "What you need")}
        </label>
        {!isNewsletter && <textarea
          value={useCase}
          onChange={(e) => setUseCase(e.target.value)}
          rows={3}
          className="input-cyber resize-none"
          placeholder={
            placeholder ||
            (isES ? "Volumen, SLA, webhooks, integración..." : "Volume, SLA, webhooks, integration...")
          }
        />
      </div>
      {error && <p className="text-sm text-[#ffb4ab]">{error}</p>}
      <button type="submit" disabled={loading} className="btn-mint w-full disabled:opacity-50">
        {loading ? (isES ? "Enviando..." : "Sending...") : isNewsletter ? (isES ? "Suscribirme gratis" : "Subscribe free") : (isES ? "Contactar ventas" : "Contact sales")}
      </button>
    </form>
  );
}
