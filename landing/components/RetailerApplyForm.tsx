"use client";

import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import LegalConsentCheckbox from "@/components/LegalConsentCheckbox";

const PLATFORMS = [
  { value: "vtex", label: "VTEX" },
  { value: "shopify", label: "Shopify" },
  { value: "magento", label: "Magento" },
  { value: "woocommerce", label: "WooCommerce" },
  { value: "other", label: "Other" },
];

const COUNTRIES = ["PE", "AR", "BR", "MX", "CO", "CL", "US", "IT", "FR"];

export default function RetailerApplyForm({
  variant = "inline",
  onSuccess,
}: {
  variant?: "inline" | "modal";
  onSuccess?: () => void;
}) {
  const { lang } = useLang();
  const isES = lang === "es";

  const [storeName, setStoreName] = useState("");
  const [platform, setPlatform] = useState("vtex");
  const [country, setCountry] = useState("PE");
  const [contactName, setContactName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [website, setWebsite] = useState("");
  const [apiToken, setApiToken] = useState("");
  const [legal, setLegal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [appId, setAppId] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!legal) {
      setError(
        isES
          ? "Debe aceptar los términos y la política de privacidad."
          : "You must accept the terms and privacy policy.",
      );
      return;
    }
    setError("");
    setLoading(true);
    try {
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
      if (!res.ok) {
        const detail = typeof data.detail === "string" ? data.detail : "Request failed";
        const friendly =
          detail.includes("platform must be one of")
            ? isES
              ? "Plataforma no reconocida. Elija VTEX, Shopify, Magento, WooCommerce u Otra."
              : "Unrecognized platform. Choose VTEX, Shopify, Magento, WooCommerce, or Other."
            : detail;
        throw new Error(friendly);
      }
      setAppId(data.application_id || "");
      onSuccess?.();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Error";
      setError(msg);
      const subject = encodeURIComponent(`CLI Market retailer — ${storeName}`);
      const body = encodeURIComponent(
        `Store: ${storeName}\nPlatform: ${platform}\nCountry: ${country}\nEmail: ${contactEmail}\nWebsite: ${website}`,
      );
      window.location.href = `mailto:hello@cli-market.dev?subject=${subject}&body=${body}`;
    } finally {
      setLoading(false);
    }
  };

  if (appId) {
    return (
      <div className="card-cyber energy-border-active p-8 max-w-[520px] mx-auto text-center">
        <p className="text-lg font-semibold text-white mb-2">
          {isES ? "Solicitud recibida" : "Application received"}
        </p>
        <p className="text-sm text-[var(--cm-on-surface-variant)] mb-4">
          ID: <code className="font-mono text-[var(--cm-mint)]">{appId}</code>
        </p>
        <p className="text-xs text-[var(--cm-on-surface-variant)]/70">
          {isES
            ? "Revisamos acceso de solo lectura al catálogo y le enviamos confirmación por email en minutos (≤24h hábiles para activación). Gratis para siempre."
            : "We review read-only catalog access and send email confirmation within minutes (≤24 business hours to go live). Free forever."}
        </p>
      </div>
    );
  }

  return (
    <form
      onSubmit={submit}
      className={`${
        variant === "inline" ? "card-cyber p-6 md:p-8 max-w-[520px] mx-auto" : ""
      } space-y-4 text-left`}
    >
      <div className={variant === "modal" ? "text-center mb-2" : ""}>
        <h3 className="text-lg font-semibold text-white text-center">
          {isES ? "Liste su tienda — 30 segundos" : "List your store — 30 seconds"}
        </h3>
        <p className="text-xs text-[var(--cm-on-surface-variant)] text-center mt-2 leading-relaxed">
          {isES
            ? "VTEX, Shopify, Magento o WooCommerce. Token de catálogo de solo lectura — gratis para siempre."
            : "VTEX, Shopify, Magento, or WooCommerce. Read-only catalog token — free forever."}
        </p>
      </div>

      <div>
        <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">
          {isES ? "Nombre de la tienda" : "Store name"}
        </label>
        <input
          required
          value={storeName}
          onChange={(e) => setStoreName(e.target.value)}
          className="input-cyber"
          placeholder="Metro Perú"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">
            {isES ? "Plataforma" : "Platform"}
          </label>
          <select value={platform} onChange={(e) => setPlatform(e.target.value)} className="input-cyber">
            {PLATFORMS.map((p) => (
              <option key={p.value} value={p.value}>
                {p.value === "other" ? (isES ? "Otra" : p.label) : p.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">
            {isES ? "País" : "Country"}
          </label>
          <select value={country} onChange={(e) => setCountry(e.target.value)} className="input-cyber">
            {COUNTRIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">
          {isES ? "Email de contacto" : "Contact email"}
        </label>
        <input
          required
          type="email"
          value={contactEmail}
          onChange={(e) => setContactEmail(e.target.value)}
          className="input-cyber"
          placeholder="ecommerce@yourstore.com"
        />
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
          {isES
            ? "Token API de solo lectura (Shopify / Magento / WooCommerce — opcional)"
            : "Read-only API token (Shopify / Magento / WooCommerce — optional)"}
        </label>
        <input
          type="password"
          value={apiToken}
          onChange={(e) => setApiToken(e.target.value)}
          className="input-cyber font-mono"
          placeholder="shpat_... or integration token"
        />
        <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-1">
          {isES
            ? "VTEX y WooCommerce Store API pública suelen no requerir token."
            : "VTEX and public WooCommerce Store API often need no token."}
        </p>
      </div>

      <LegalConsentCheckbox checked={legal} onChange={setLegal} />

      {error && <p className="text-sm text-[#ffb4ab]">{error}</p>}

      <button type="submit" disabled={loading || !legal} className="btn-mint w-full disabled:opacity-50 disabled:cursor-not-allowed">
        {loading
          ? isES
            ? "Enviando…"
            : "Submitting…"
          : isES
            ? "Enviar solicitud — gratis"
            : "Submit — free listing"}
      </button>
    </form>
  );
}