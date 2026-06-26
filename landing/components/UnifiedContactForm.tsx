"use client";
import { useState, useEffect } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import LegalConsentCheckbox from "@/components/LegalConsentCheckbox";

const TOPICS_ES = [
  { value: "enterprise", label: "Enterprise / Volumen personalizado" },
  { value: "procure",    label: "Procure Copilot — demo o piloto" },
  { value: "press",      label: "Prensa / Alianza" },
  { value: "general",    label: "Consulta general" },
  { value: "retailer",   label: "Listar mi tienda (gratis)" },
];
const TOPICS_EN = [
  { value: "enterprise", label: "Enterprise / Custom volume" },
  { value: "procure",    label: "Procure Copilot — demo or pilot" },
  { value: "press",      label: "Press / Partnership" },
  { value: "general",    label: "General inquiry" },
  { value: "retailer",   label: "List my store (free)" },
];

const MSG_PLACEHOLDERS_ES: Record<string, string> = {
  enterprise: "País, categorías, volumen estimado, SLA esperado…",
  procure:    "Empresa, sector (restaurante/hotel/etc.), volumen de compras mensual, país…",
  press:      "Medio, tema de la nota, fecha de publicación…",
  general:    "¿En qué podemos ayudarte?",
};
const MSG_PLACEHOLDERS_EN: Record<string, string> = {
  enterprise: "Country, categories, estimated volume, expected SLA…",
  procure:    "Company, sector (restaurant/hotel/etc.), monthly procurement volume, country…",
  press:      "Publication, story topic, publish date…",
  general:    "How can we help?",
};

const PLATFORMS = [
  { value: "vtex", label: "VTEX" },
  { value: "shopify", label: "Shopify" },
  { value: "magento", label: "Magento" },
  { value: "woocommerce", label: "WooCommerce" },
  { value: "other", label: "Other" },
];
const COUNTRIES = ["PE", "AR", "BR", "MX", "CO", "CL", "US", "IT", "FR"];

export default function UnifiedContactForm() {
  const { lang } = useLang();
  const isES = lang === "es";

  const topics = isES ? TOPICS_ES : TOPICS_EN;
  const [topic, setTopic] = useState("enterprise");

  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    const fromQuery = params.get("topic");
    const hash = window.location.hash.replace("#", "");
    const fromHash =
      hash === "contact-procure" ? "procure" : hash === "contact-intelligence" ? "enterprise" : null;
    const next = fromQuery || fromHash;
    const allowed = new Set(["enterprise", "procure", "press", "general", "retailer"]);
    if (next && allowed.has(next)) {
      setTopic(next);
    }
  }, []);

  // General contact fields
  const [email, setEmail]     = useState("");
  const [message, setMessage] = useState("");

  // Retailer fields
  const [storeName,     setStoreName]     = useState("");
  const [platform,      setPlatform]      = useState("vtex");
  const [country,       setCountry]       = useState("PE");
  const [contactName,   setContactName]   = useState("");
  const [contactEmail,  setContactEmail]  = useState("");
  const [website,       setWebsite]       = useState("");
  const [apiToken,      setApiToken]      = useState("");
  const [appId,         setAppId]         = useState("");

  const [sent,    setSent]    = useState(false);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState("");
  const [legal,   setLegal]   = useState(false);

  const isRetailer = topic === "retailer";

  const submitContact = async () => {
    if (!email.includes("@")) {
      setError(isES ? "Email inválido" : "Invalid email");
      return false;
    }
    if (!message.trim() || message.trim().length < 10) {
      setError(isES ? "Escribe al menos 10 caracteres" : "Write at least 10 characters");
      return false;
    }
    const res = await fetch(`${API_URL}/v1/contact`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ plan: topic, email, use_case: message, lang: isES ? "es" : "en" }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || "error");
    return true;
  };

  const submitRetailer = async () => {
    const res = await fetch(`${API_URL}/v1/retailers/apply`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        store_name: storeName,
        platform,
        country,
        contact_name: contactName,
        contact_email: contactEmail,
        website,
        api_token: apiToken || undefined,
        lang: isES ? "es" : "en",
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Request failed");
    setAppId(data.application_id || "");
    return true;
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    if (!legal) {
      setError(
        isES
          ? "Debe aceptar los términos y la política de privacidad."
          : "You must accept the terms and privacy policy.",
      );
      return;
    }
    setLoading(true);
    setError("");
    try {
      const ok = isRetailer ? await submitRetailer() : await submitContact();
      if (ok && !appId) setSent(true);
    } catch {
      setLoading(false);
      if (isRetailer) {
        const subject = encodeURIComponent(`CLI Market retailer — ${storeName}`);
        const body = encodeURIComponent(`Store: ${storeName}\nPlatform: ${platform}\nCountry: ${country}\nEmail: ${contactEmail}\nWebsite: ${website}`);
        window.location.href = `mailto:hello@cli-market.dev?subject=${subject}&body=${body}`;
      } else {
        const subject = encodeURIComponent(`CLI Market ${topic} — ${email}`);
        window.location.href = `mailto:hello@cli-market.dev?subject=${subject}&body=${encodeURIComponent(message)}`;
      }
      return;
    }
    setLoading(false);
  };

  if (sent || appId) {
    const confirmEmail = isRetailer ? contactEmail : email;
    return (
      <div className="card-cyber energy-border-active p-6 sm:p-8 text-center w-full max-w-lg mx-auto space-y-3">
        <p className="text-lg font-semibold text-white">
          {isES ? "¡Gracias! Te escribiremos pronto." : "Thanks! We'll reach out soon."}
        </p>
        {appId && (
          <p className="text-xs font-mono text-[var(--cm-mint)]">
            ID: {appId}
          </p>
        )}
        <p className="text-sm text-[var(--cm-on-surface-variant)]">
          {isES
            ? `Responderemos a ${confirmEmail} en el mismo día hábil.`
            : `We'll reply to ${confirmEmail} on the same business day.`}
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="card-cyber p-5 sm:p-8 w-full max-w-lg mx-auto space-y-5 text-left">
      <div className="text-center space-y-1">
        <span className="inline-block font-label-caps text-[var(--cm-on-surface-variant)]/60">
          {isES ? "Contacto" : "Contact"}
        </span>
        <h3 className="text-lg font-semibold text-white">
          {isES ? "¿En qué podemos ayudarte?" : "How can we help?"}
        </h3>
        <p className="text-sm text-[var(--cm-on-surface-variant)]">
          {isES ? "Respondemos habitualmente el mismo día hábil." : "We usually reply the same business day."}
        </p>
      </div>

      {/* Topic selector */}
      <div>
        <label className="block text-sm font-medium text-white mb-1">
          {isES ? "Motivo" : "Topic"}
        </label>
        <select value={topic} onChange={(e) => { setTopic(e.target.value); setError(""); }} className="input-cyber">
          {topics.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
      </div>

      {/* Retailer fields */}
      {isRetailer && (
        <>
          <div>
            <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">
              {isES ? "Nombre de la tienda" : "Store name"}
            </label>
            <input required value={storeName} onChange={(e) => setStoreName(e.target.value)} className="input-cyber" placeholder="Metro Perú" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">Platform</label>
              <select value={platform} onChange={(e) => setPlatform(e.target.value)} className="input-cyber">
                {PLATFORMS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">{isES ? "País" : "Country"}</label>
              <select value={country} onChange={(e) => setCountry(e.target.value)} className="input-cyber">
                {COUNTRIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">
              {isES ? "Email de contacto" : "Contact email"}
            </label>
            <input required type="email" value={contactEmail} onChange={(e) => setContactEmail(e.target.value)} className="input-cyber" placeholder="ecommerce@yourstore.com" />
          </div>
          <div>
            <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">
              {isES ? "Nombre de contacto (opcional)" : "Contact name (optional)"}
            </label>
            <input value={contactName} onChange={(e) => setContactName(e.target.value)} className="input-cyber" />
          </div>
          <div>
            <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">
              {isES ? "URL de la tienda (opcional)" : "Store URL (optional)"}
            </label>
            <input value={website} onChange={(e) => setWebsite(e.target.value)} className="input-cyber" placeholder="https://..." />
          </div>
          <div>
            <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">
              {isES ? "API token de solo lectura (opcional)" : "Read-only API token (optional)"}
            </label>
            <input type="password" value={apiToken} onChange={(e) => setApiToken(e.target.value)} className="input-cyber font-mono" placeholder="shpat_... or integration token" />
            <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-1">
              {isES
                ? "VTEX y WooCommerce Store API pública suelen no requerir token."
                : "VTEX and public WooCommerce Store API often need no token."}
            </p>
          </div>
        </>
      )}

      {/* General contact fields */}
      {!isRetailer && (
        <>
          <div>
            <label className="block text-sm font-medium text-white mb-1">Email</label>
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="input-cyber" placeholder="tu@email.com" />
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
              placeholder={(isES ? MSG_PLACEHOLDERS_ES : MSG_PLACEHOLDERS_EN)[topic]}
            />
          </div>
        </>
      )}

      <LegalConsentCheckbox checked={legal} onChange={setLegal} />

      {error && <p className="text-sm text-[#ffb4ab]">{error}</p>}

      <button type="submit" disabled={loading || !legal} className="btn-mint w-full disabled:opacity-50 disabled:cursor-not-allowed">
        {loading
          ? (isES ? "Enviando…" : "Sending…")
          : isRetailer
            ? (isES ? "Enviar aplicación — gratis →" : "Submit — free listing →")
            : (isES ? "Enviar →" : "Send →")}
      </button>
    </form>
  );
}
