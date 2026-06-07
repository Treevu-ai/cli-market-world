"use client";

import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import ProSubscribeButton from "@/components/ProSubscribeButton";

type AccountData = {
  username: string;
  tier: string;
  limits: {
    req_day: number | string;
    req_min: number | string;
    api_keys: number | string;
    checkout: boolean;
    alerts: number;
    export: boolean;
  };
  usage: {
    requests_today: number;
    requests_last_minute: number;
    api_keys_used: number;
    daily_pct?: number | null;
    minute_pct?: number | null;
  };
  upgrade: {
    next_tier?: string | null;
    title?: string;
    cli?: string;
    url?: string | null;
    cta?: string | null;
  };
  billing?: {
    state?: string;
    activation?: string | null;
    request_id?: string | null;
    approve_url?: string | null;
    message?: string | null;
  };
};

function UsageBar({
  used,
  limit,
  label,
}: {
  used: number;
  limit: number | string;
  label: string;
}) {
  const unlimited = limit === "unlimited" || limit === -1;
  const lim = typeof limit === "number" ? limit : 0;
  const pct = unlimited || !lim ? 0 : Math.min((used / lim) * 100, 100);

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-[var(--cm-on-surface-variant)]">
        <span>{label}</span>
        <span className="font-mono tabular-nums">
          {unlimited ? `${used.toLocaleString()} / ∞` : `${used.toLocaleString()} / ${lim.toLocaleString()}`}
        </span>
      </div>
      <div className="h-2 rounded-full bg-[var(--cm-surface-high)] overflow-hidden">
        <div
          className="h-full bg-[var(--cm-mint)] transition-all duration-300"
          style={{ width: unlimited ? "8%" : `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function AccountDashboard() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [apiKey, setApiKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState<AccountData | null>(null);

  const load = async () => {
    setError("");
    if (!apiKey.trim().startsWith("sk-")) {
      setError(isES ? "Ingrese su API key (sk-...)" : "Enter your API key (sk-...)");
      return;
    }
    setLoading(true);
    try {
      const r = await fetch(`${API_URL}/auth/account?lang=${isES ? "es" : "en"}`, {
        headers: { Authorization: `Bearer ${apiKey.trim()}` },
      });
      const body = await r.json().catch(() => ({}));
      if (!r.ok) {
        setError(body.detail || body.error || `HTTP ${r.status}`);
        setData(null);
        return;
      }
      setData(body);
    } catch {
      setError(isES ? "Error de red" : "Network error");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="landing-section animate-fade-in">
      <div className="landing-container-narrow">
        <p className="section-eyebrow mb-4 text-[var(--cm-mint)] text-center">
          {isES ? "Su cuenta" : "Your account"}
        </p>
        <h1 className="section-title text-center mb-2">
          {isES ? "Dashboard de uso" : "Usage dashboard"}
        </h1>
        <p className="text-sm text-[var(--cm-on-surface-variant)] text-center max-w-lg mx-auto mb-8">
          {isES
            ? "Consulte tier, límites y consumo. La API key no se guarda en el navegador."
            : "View tier, limits, and consumption. Your API key is not stored in the browser."}
        </p>

        <div className="card-cyber p-6 space-y-4 max-w-xl mx-auto">
          <label className="block text-sm font-medium text-white">
            API key
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="sk-..."
            className="input-cyber font-mono text-sm"
            autoComplete="off"
          />
          <p className="text-xs text-[var(--cm-on-surface-variant)]/70">
            {isES
              ? "Obténgala con market register · También: market account en terminal"
              : "Get one with market register · Or run market account in the terminal"}
          </p>
          {error && <p className="text-sm text-[#ffb4ab]">{error}</p>}
          <button
            type="button"
            onClick={load}
            disabled={loading}
            className="btn-mint w-full disabled:opacity-50"
          >
            {loading
              ? isES
                ? "Cargando..."
                : "Loading..."
              : isES
                ? "Ver mi cuenta →"
                : "View my account →"}
          </button>
        </div>

        {data && (
          <div className="mt-10 grid gap-4 md:grid-cols-2 max-w-3xl mx-auto">
            <div className="card-cyber p-5 space-y-3">
              <h2 className="text-sm font-bold text-[var(--cm-mint)] uppercase tracking-wider">
                {isES ? "Plan" : "Plan"}
              </h2>
              <p className="text-2xl font-black text-white capitalize">{data.tier}</p>
              <p className="text-xs font-mono text-[var(--cm-on-surface-variant)]">
                {data.username}
              </p>
              <ul className="text-sm text-[var(--cm-on-surface-variant)] space-y-1">
                <li>
                  {isES ? "Checkout" : "Checkout"}: {data.limits.checkout ? "✓" : "—"}
                </li>
                <li>
                  {isES ? "Export" : "Export"}: {data.limits.export ? "✓" : "—"}
                </li>
                <li>
                  {isES ? "Alertas" : "Alerts"}: {data.limits.alerts}
                </li>
              </ul>
            </div>

            {data.billing?.message && (
              <div className="card-cyber p-5 md:col-span-2 space-y-2 border border-yellow-500/20 bg-yellow-500/5">
                <h2 className="text-sm font-bold text-yellow-400 uppercase tracking-wider">
                  {isES ? "Facturación" : "Billing"}
                </h2>
                <p className="text-sm text-[var(--cm-on-surface-variant)]">{data.billing.message}</p>
                {data.billing.request_id && (
                  <p className="text-xs font-mono text-[var(--cm-on-surface-variant)]/70">
                    ref: {data.billing.request_id}
                  </p>
                )}
                {data.billing.approve_url && data.billing.activation === "auto" && (
                  <a
                    href={data.billing.approve_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-mint inline-flex text-sm"
                  >
                    {isES ? "Confirmar en PayPal →" : "Confirm on PayPal →"}
                  </a>
                )}
              </div>
            )}

            <div className="card-cyber p-5 space-y-4">
              <h2 className="text-sm font-bold text-[var(--cm-mint)] uppercase tracking-wider">
                {isES ? "Uso" : "Usage"}
              </h2>
              <UsageBar
                used={data.usage.requests_today}
                limit={data.limits.req_day}
                label={isES ? "Hoy" : "Today"}
              />
              <UsageBar
                used={data.usage.requests_last_minute}
                limit={data.limits.req_min}
                label={isES ? "Último minuto" : "Last minute"}
              />
              <p className="text-xs text-[var(--cm-on-surface-variant)]">
                API keys: {data.usage.api_keys_used} / {String(data.limits.api_keys)}
              </p>
            </div>

            {data.upgrade?.next_tier && (
              <div className="card-cyber p-5 md:col-span-2 space-y-4 border border-[var(--cm-mint)]/20">
                <h2 className="text-sm font-bold text-[var(--cm-mint)] uppercase tracking-wider">
                  {isES ? "Siguiente paso" : "Next step"}
                </h2>
                <p className="text-white font-semibold">{data.upgrade.title}</p>
                {data.upgrade.cli && (
                  <pre className="code-snippet text-xs text-[var(--cm-mint)] bg-black/30 p-3 rounded-lg overflow-x-auto">
                    {data.upgrade.cli}
                  </pre>
                )}
                {data.upgrade.next_tier === "pro" ? (
                  <div id="account-pro-upgrade">
                    <ProSubscribeButton />
                  </div>
                ) : data.upgrade.url ? (
                  <a href={data.upgrade.url} className="btn-mint inline-flex">
                    {data.upgrade.cta || (isES ? "Ver planes →" : "View plans →")}
                  </a>
                ) : null}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}