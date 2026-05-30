"use client";

import { useState } from "react";
import { API_URL } from "@/lib/api";

const PLATFORMS = [
  { value: "vtex", label: "VTEX" },
  { value: "shopify", label: "Shopify" },
  { value: "magento", label: "Magento" },
  { value: "other", label: "Other" },
];

const COUNTRIES = ["PE", "AR", "BR", "MX", "CO", "CL", "US", "IT", "FR"];

export default function RetailerApplyForm() {
  const [storeName, setStoreName] = useState("");
  const [platform, setPlatform] = useState("vtex");
  const [country, setCountry] = useState("PE");
  const [contactName, setContactName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [website, setWebsite] = useState("");
  const [apiToken, setApiToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [appId, setAppId] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
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
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Request failed");
      }
      setAppId(data.application_id || "");
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
        <p className="text-lg font-semibold text-white mb-2">Application received</p>
        <p className="text-sm text-[var(--cm-on-surface-variant)] mb-4">
          ID: <code className="font-mono text-[var(--cm-mint)]">{appId}</code>
        </p>
        <p className="text-xs text-[var(--cm-on-surface-variant)]/70">
          We validate read-only catalog access and email you within 24 hours. Free forever.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="card-cyber p-6 md:p-8 max-w-[520px] mx-auto space-y-4 text-left">
      <h3 className="text-lg font-semibold text-white text-center">List your store — 30 seconds</h3>

      <div>
        <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">Store name</label>
        <input required value={storeName} onChange={(e) => setStoreName(e.target.value)} className="input-cyber" placeholder="Metro Perú" />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">Platform</label>
          <select value={platform} onChange={(e) => setPlatform(e.target.value)} className="input-cyber">
            {PLATFORMS.map((p) => (
              <option key={p.value} value={p.value}>{p.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">Country</label>
          <select value={country} onChange={(e) => setCountry(e.target.value)} className="input-cyber">
            {COUNTRIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">Contact email</label>
        <input required type="email" value={contactEmail} onChange={(e) => setContactEmail(e.target.value)} className="input-cyber" placeholder="ecommerce@yourstore.com" />
      </div>

      <div>
        <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">Contact name (optional)</label>
        <input value={contactName} onChange={(e) => setContactName(e.target.value)} className="input-cyber" />
      </div>

      <div>
        <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">Store URL (optional)</label>
        <input value={website} onChange={(e) => setWebsite(e.target.value)} className="input-cyber" placeholder="https://..." />
      </div>

      <div>
        <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">
          Read-only API token (Shopify/Magento — optional)
        </label>
        <input type="password" value={apiToken} onChange={(e) => setApiToken(e.target.value)} className="input-cyber font-mono" placeholder="shpat_... or integration token" />
        <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-1">VTEX public catalogs often need no token.</p>
      </div>

      {error && <p className="text-sm text-[#ffb4ab]">{error}</p>}

      <button type="submit" disabled={loading} className="btn-mint w-full disabled:opacity-50">
        {loading ? "Submitting…" : "Submit — free listing"}
      </button>
    </form>
  );
}
