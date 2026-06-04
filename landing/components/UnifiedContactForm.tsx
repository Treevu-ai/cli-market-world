"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";

const TOPICS_ES = [
  { value: "enterprise", label: "Enterprise / Volumen personalizado" },
  { value: "press",      label: "Prensa / Alianza" },
  { value: "general",    label: "Consulta general" },
];
const TOPICS_EN = [
  { value: "enterprise", label: "Enterprise / Custom volume" },
  { value: "press",      label: "Press / Partnership" },
  { value: "general",    label: "General inquiry" },
];

const PLACEHOLDERS_ES: Record<string, string> = {
  enterprise: "País, categorías, volumen estimado, SLA esperado…",
  press:      "Medio, tema de la nota, fecha de publicación…",
  general:    "¿En qué podemos ayudarte?",
};
const PLACEHOLDERS_EN: Record<string, string> = {
  enterprise: "Country, categories, estimated volume, expected SLA…",
  press:      "Publication, story topic, publish date…",
  general:    "How can we help?",
};

export default function UnifiedContactForm() {
  const { lang } = useLang();
  const isES = lang === "es";

  const topics = isES ? TOPICS_ES : TOPICS_EN;
  const [topic, setTopic] = useState("enterprise");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.includes("@")) {
      setError(isES ? "Email inválido" : "Invalid email");
      return;
    }
    if (!message.trim() || message.trim().length < 10) {
      setError(isES ? "Escribe al menos 10 caracteres" : "Write at least 10 characters");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/v1/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          plan: topic,
          email,
          use_case: message,
          lang: isES ? "es" : "en",
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) { setSent(true); return; }
      throw new Error(data.detail || "error");
    } catch {
      setLoading(false);
      const subject = encodeURIComponent(`CLI Market ${topic} — ${email}`);
      const body = encodeURIComponent(message);
      window.location.href = `mailto:hello@cli-market.dev?subject=${subject}&body=${body}`;
    }
  };

  if (sent) {
    return (
      <div className="card-cyber energy-border-active p-6 sm:p-8 text-center w-full max-w-lg mx-auto space-y-3">
        <p className="text-lg font-semibold text-white">
          {isES ? "¡Gracias! Te escribiremos pronto." : "Thanks! We'll reach out soon."}
        </p>
        <p className="text-sm text-[var(--cm-on-surface-variant)]">
          {isES ? `Respondemos a ${email} en menos de 30 min.` : `We'll reply to ${email} within 30 min.`}
        </p>
      </div>
    );
  }

  return (
    <form
      onSubmit={submit}
      className="card-cyber p-5 sm:p-8 w-full max-w-lg mx-auto space-y-5 text-left"
    >
      <div className="text-center space-y-1">
        <span className="inline-block font-label-caps text-[var(--cm-on-surface-variant)]/60">
          {isES ? "Contacto" : "Contact"}
        </span>
        <h3 className="text-lg font-semibold text-white">
          {isES ? "¿En qué podemos ayudarte?" : "How can we help?"}
        </h3>
        <p className="text-sm text-[var(--cm-on-surface-variant)]">
          {isES ? "Respondemos en menos de 30 min." : "We reply within 30 min."}
        </p>
      </div>

      {/* Topic selector */}
      <div>
        <label className="block text-sm font-medium text-white mb-1">
          {isES ? "Tema" : "Topic"}
        </label>
        <select
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className="input-cyber"
        >
          {topics.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-white mb-1">Email</label>
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="input-cyber"
          placeholder="tu@email.com"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-white mb-1">
          {isES ? "Mensaje" : "Message"}
        </label>
        <textarea
          required
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows={3}
          className="input-cyber resize-none"
          placeholder={(isES ? PLACEHOLDERS_ES : PLACEHOLDERS_EN)[topic]}
        />
      </div>

      {error && <p className="text-sm text-[#ffb4ab]">{error}</p>}

      <button
        type="submit"
        disabled={loading}
        className="btn-mint w-full disabled:opacity-50"
      >
        {loading
          ? isES ? "Enviando…" : "Sending…"
          : isES ? "Enviar →" : "Send →"}
      </button>
    </form>
  );
}
